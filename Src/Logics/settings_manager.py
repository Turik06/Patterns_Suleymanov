import os
import json
from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator, operation_exception
from Src.Core.common import common
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model


class settings_manager(abstract_manager):
    """
    Менеджер для работы с настройками приложения.
    Реализует шаблон Singleton и загрузку данных через интроспекцию моделей.
    """
    __default_file_name: str = "settings.json"

    _settings: settings_model = None
    __data: dict = None

    @staticmethod
    def create_killogramm() -> range_model:
        """
        Фабричный метод - создать килограмм (делегирует создание range_model).
        """
        return range_model.create_killogramm()

    @staticmethod
    def create_kilogram() -> range_model:
        """
        Фабричный метод - создать килограмм (делегирует создание range_model).
        """
        return range_model.create_kilogram()



    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(settings_manager, cls).__new__(cls)
            cls.instance._settings = settings_model()
            cls.instance.__data = {}
        return cls.instance

    def load(self, file_name: str = "") -> None:
        """
        Загружает данные настроек из JSON файла.
        """
        inner_file_name = file_name.strip() if file_name.strip() != "" else self.__default_file_name
        validator.validate(inner_file_name, str)

        full_file_name = os.path.abspath(inner_file_name)
        if not os.path.exists(full_file_name):
            raise operation_exception(f"Не найден указанный файл {full_file_name}")

        try:
            with open(full_file_name, "r", encoding="utf-8") as file:
                self.__data = json.load(file)

            self.is_loaded = self.build()
            if not self.is_loaded:
                self._settings = self.__create_default_data()

        except operation_exception:
            raise
        except Exception as ex:
            raise operation_exception(
                f"Ошибка при загрузке и обработке файла: {inner_file_name}. Детали: {ex}"
            ) from ex

    def build(self) -> bool:
        """
        Обработать загруженные сырые данные и заполнить settings_model через интроспекцию полей.
        Использует common.get_fields для динамического связывания.
        """
        if not isinstance(self.__data, dict) or len(self.__data) == 0:
            return False

        try:
            if self._settings is None:
                self._settings = settings_model()

            # 1. Загрузка данных организации через рефлексию
            company = self._settings.organization or organization_model()
            company_fields = common.get_fields(company, is_common=True)

            # Вариант А: вложенный словарь {"organization": {...}} или {"company": {...}}
            org_data = self.__data.get("organization") or self.__data.get("company")
            if isinstance(org_data, dict):
                for field in company_fields:
                    if field in ("id",):
                        continue
                    if field in org_data:
                        val = org_data[field]
                        if val is not None and str(val).strip():
                            try:
                                setattr(company, field, val)
                            except Exception:
                                pass

            # Вариант Б: плоские ключи вида "company_<field>" (например, "company_name", "company_inn")
            for field in company_fields:
                key = f"company_{field}"
                if key in self.__data:
                    val = self.__data[key]
                    if val is not None and str(val).strip():
                        try:
                            setattr(company, field, val)
                        except Exception:
                            pass

            # Если у компании есть обязательные поля (например, name), привязываем к настройкам
            if company.name:
                self._settings.organization = company

            # 2. Загрузка данных настроек через рефлексию
            settings_fields = common.get_fields(self._settings, is_common=True)
            for field in settings_fields:
                if field in ("organization", "company", "id", "name"):
                    continue
                if field in self.__data:
                    val = self.__data[field]
                    if val is not None and str(val).strip():
                        try:
                            setattr(self._settings, field, val)
                        except Exception:
                            pass

            # Поддержка альтернативных наименований флага первого старта
            if "first_start" in self.__data:
                self._settings.is_first_start = bool(self.__data.get("first_start"))
            elif "is_first_start" in self.__data:
                self._settings.is_first_start = bool(self.__data.get("is_first_start"))

            return True

        except Exception:
            return False

    def convert(self) -> bool:
        """
        Преобразует сырые данные JSON в объект settings_model.
        Псевдоним метода build() для обратной совместимости.
        """
        return self.build()

    def __create_default_data(self) -> settings_model:
        """
        Сформировать настройки по умолчанию при ошибке обработки данных.
        """
        result = settings_model()

        company = organization_model(
            name="ООО Ромашка",
            inn="7736050003",
            bik="044525225",
            account="40812810400000000225",
            ownership_form="ООО"
        )

        result.organization = company
        result.boss_name = "Воловиков Александр Сергеевич"
        result.account_name = "Балахчи Анна Георгиевна"
        result.is_first_start = True
        return result

    @property
    def settings(self) -> settings_model:
        """Объект настроек settings_model."""
        return self._settings