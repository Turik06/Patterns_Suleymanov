from Src.Core.validator import validator
from Src.Logics.storage_manager import storage_manager
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_model import recipe_model
from Src.Logics.convertor import convertor
from Src.Logics.mapping_factory import mapping_factory
from Src.Core.event_type import event_type
from Src.Logics.observer import observer


class entity_service:
    """Сервис для работы с доменными сущностями"""

    def __init__(self, storage: storage_manager):
        """Инициализация сервиса"""
        validator.validate(storage, storage_manager)
        self.__storage = storage

    @property
    def storage(self) -> storage_manager:
        """Хранилище данных"""
        return self.__storage

    def get_catalog(self, entity_type: str) -> dict:
        """Получить словарь сущностей по типу"""
        return self.__storage.get_catalog(entity_type)

    def _get_all_catalogs(self) -> list:
        """Получить все словари сущностей"""
        return [
            self.__storage.ranges,
            self.__storage.groups,
            self.__storage.nomenclatures,
            self.__storage.recipes,
            self.__storage.storages,
        ]

    def find_referrers(self, unique_code: str) -> list:
        """Найти объекты, ссылающиеся на код"""
        if not unique_code:
            return []

        referrers = []
        all_items = [item for cat in self._get_all_catalogs() for item in cat.values()]

        for item in all_items:
            if getattr(item, "unique_code", None) == unique_code:
                continue
            for ref in item.references():
                if getattr(ref, "unique_code", None) == unique_code:
                    referrers.append(item)
                    break

        return referrers

    def is_linked(self, unique_code: str) -> bool:
        """Проверить наличие ссылок на сущность"""
        repo = getattr(self.__storage, "repository", None)
        if repo is not None and hasattr(repo, "counts") and unique_code in repo.counts:
            return repo.counts[unique_code] > 0
        return len(self.find_referrers(unique_code)) > 0

    def validate_dependencies_exist(self, dto, entity) -> tuple[bool, str]:
        """Проверить наличие связанных сущностей"""
        base_code = getattr(dto, "base_code", None)
        if base_code and (not getattr(entity, "base", None) or entity.base.unique_code not in self.__storage.ranges):
            return False, f"Базовая единица измерения '{base_code}' не найдена"

        group_code = getattr(dto, "group_code", None)
        if group_code and (not getattr(entity, "group", None) or entity.group.unique_code not in self.__storage.groups):
            return False, f"Группа номенклатуры '{group_code}' не найдена"

        range_code = getattr(dto, "range_code", None)
        if range_code and (not getattr(entity, "range", None) or entity.range.unique_code not in self.__storage.ranges):
            return False, f"Единица измерения '{range_code}' не найдена"

        if isinstance(entity, recipe_model):
            for row in getattr(entity, "rows", []):
                if row.nomenclature and row.nomenclature.unique_code not in self.__storage.nomenclatures:
                    return False, f"Номенклатура '{row.nomenclature.name}' не найдена"
                if row.range and row.range.unique_code not in self.__storage.ranges:
                    return False, f"Единица измерения '{row.range.name}' не найдена"

        return True, ""

    def get_entity(self, entity_type: str, unique_code: str):
        """Получить сущность по коду"""
        catalog = self.get_catalog(entity_type)
        if catalog is None:
            raise ValueError(f"Неизвестный тип сущности '{entity_type}'")
        entity = catalog.get(unique_code)
        if not entity:
            raise LookupError(f"Сущность '{unique_code}' не найдена")
        observer.create(event_type.crud_operation(), {"action": "read", "entity_type": entity_type, "id": unique_code})
        return entity

    def create_entity(self, entity_type: str, payload: dict, worker=None):
        """Создать сущность из словаря"""
        category = self.__storage.resolve_category(entity_type)
        if not category or category not in self.__storage.data:
            raise ValueError(f"Неизвестный тип сущности '{entity_type}'")

        worker = worker or convertor()
        dto = worker.resolve_dto(payload, type_hint=entity_type) or worker.resolve_dto(payload, type_hint=category)
        if not dto:
            raise ValueError("Не удалось создать объект из данных")

        resolver = {item.unique_code: item for cat in self._get_all_catalogs() for item in cat.values()}
        model = mapping_factory().to_model(dto, resolver)
        if not model:
            raise ValueError("Не удалось создать объект из данных")

        is_valid, msg = self.validate_dependencies_exist(dto, model)
        if not is_valid:
            raise ValueError(msg)

        catalog = self.get_catalog(entity_type)
        if catalog is not None and model.unique_code in catalog:
            raise ValueError(f"Сущность '{model.unique_code}' уже существует")

        self.__storage.save_entity(model)
        observer.create(event_type.crud_operation(), {"action": "create", "entity_type": entity_type, "id": model.unique_code})
        return model

    def update_entity(self, entity_type: str, unique_code: str, payload: dict):
        """Обновить поля сущности"""
        catalog = self.get_catalog(entity_type)
        if catalog is None:
            raise ValueError(f"Неизвестный тип сущности '{entity_type}'")

        entity = catalog.get(unique_code)
        if not entity:
            raise LookupError(f"Сущность '{unique_code}' не найдена")

        new_code = payload.get("unique_code") or payload.get("id")
        changing_code = bool(new_code and new_code != unique_code)

        if changing_code:
            if self.is_linked(unique_code):
                raise PermissionError(f"Нельзя менять код связанной сущности '{unique_code}'")
            if new_code in catalog:
                raise ValueError(f"Сущность с кодом '{new_code}' уже существует")

        fields_to_update = {
            key: val for key, val in payload.items()
            if key not in ("unique_code", "id", "type") and hasattr(entity, key) and val is not None
        }

        old_values = {key: getattr(entity, key) for key in fields_to_update}

        try:
            for key, val in fields_to_update.items():
                setattr(entity, key, val)
        except Exception as ex:
            for key, old_val in old_values.items():
                setattr(entity, key, old_val)
            raise ValueError(f"Ошибка валидации поля: {ex}") from ex

        if changing_code:
            del catalog[unique_code]
            repo = getattr(self.__storage, "repository", None)
            if repo is not None:
                repo.data.pop(unique_code, None)
                repo.counts.pop(unique_code, None)
            entity.unique_code = new_code
            catalog[new_code] = entity
            if repo is not None:
                repo.registry(entity)

        observer.create(event_type.crud_operation(), {"action": "update", "entity_type": entity_type, "id": entity.unique_code, "fields": list(fields_to_update.keys())})
        return entity

    def delete_entity(self, entity_type: str, unique_code: str):
        """Удалить сущность с проверкой связей"""
        catalog = self.get_catalog(entity_type)
        if catalog is None:
            raise ValueError(f"Неизвестный тип сущности '{entity_type}'")

        entity = catalog.get(unique_code)
        if not entity:
            raise LookupError(f"Сущность '{unique_code}' не найдена")

        repo = getattr(self.__storage, "repository", None)
        if repo is not None and hasattr(repo, "can_delete"):
            if not repo.can_delete(entity):
                referrers = self.find_referrers(unique_code)
                ref_names = [getattr(r, "name", str(r)) for r in referrers]
                raise PermissionError(f"Нельзя удалить сущность '{unique_code}', так как она связана с другими", ref_names)
        elif self.is_linked(unique_code):
            referrers = self.find_referrers(unique_code)
            ref_names = [getattr(r, "name", str(r)) for r in referrers]
            raise PermissionError(f"Нельзя удалить сущность '{unique_code}', так как она связана с другими", ref_names)

        self.__storage.delete_entity(entity_type, unique_code)
        observer.create(event_type.crud_operation(), {"action": "delete", "entity_type": entity_type, "id": unique_code})
        return True
