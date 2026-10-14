from abc import ABC, abstractmethod
from Src.Core.exception import argument_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model

class abstract_report(ABC):
    """
    Базовый класс отчетов (шаблонный метод + нормализация данных).
    """
    # Флаг формата результата: True -> binary (CSV, MD), False -> text (XML, HTML, TXT)
    is_binary: bool = False

    def build(self, source) -> report_result_dto:
        """
        Шаблонный метод формирования отчета.
        Проверяет источник, извлекает данные и формирует результат.
        """
        if source is None:
            raise argument_exception("source", "Источник данных не может быть пустым!")

        if isinstance(source, recipe_model):
            headers = ["Код", "Наименование", "Брутто", "Нетто"]
            rows = [
                [item.unique_code, item.name, item.brutto, item.netto]
                for item in source.items
            ]
            content = self._render_recipe(source, headers, rows)
        else:
            title, xml_root, fields = self._extract_card_fields(source)
            content = self._render_card(title, xml_root, fields)

        result = report_result_dto()
        if self.is_binary:
            result.binary = list(content.encode("utf-8"))
        else:
            result.text = content
        return result

    @staticmethod
    def _extract_card_fields(source):
        """
        Превращает линейную модель в универсальный набор:
        (Заголовок, корневой_тег_xml, [(Русское_имя, xml_тег, значение), ...])
        """
        if isinstance(source, nomenclature_model):
            return (
                f"Номенклатура: {source.name}",
                "nomenclature",
                [
                    ("Код", "id", source.unique_code),
                    ("Наименование", "name", source.name),
                    ("Полное наименование", "full_name", source.full_name),
                    ("Группа", "group", source.group.name if source.group else ""),
                    ("Единица измерения", "range", source.range.name if source.range else ""),
                ],
            )
        if isinstance(source, range_model):
            return (
                f"Единица измерения: {source.name}",
                "range",
                [
                    ("Код", "id", source.unique_code),
                    ("Наименование", "name", source.name),
                    ("Коэффициент", "conversion_factor", source.conversion_factor),
                    ("Базовая единица", "base_unit", source.base.name if source.base else ""),
                ],
            )
        raise argument_exception("source", f"Неподдерживаемый тип источника данных: {type(source)}")

    @abstractmethod
    def _render_recipe(self, source: recipe_model, headers: list, rows: list) -> str:
        """Отрисовка отчета по рецепту."""
        pass

    @abstractmethod
    def _render_card(self, title: str, xml_root: str, fields: list) -> str:
        """Отрисовка карточки одиночной сущности."""
        pass


AbstractReport = abstract_report