from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Models.recipe_model import recipe_model
from Src.Core.validator import validator
from Src.Dtos.report_result_dto import report_result_dto


"""
Реализация текстового представления отчета по рецепту
"""
class text_report(abstract_report):
    """
    Класс построения отчета по технологической карте (рецепту) в текстовом формате.
    """
    __receipt: recipe_model = None

    def build(self, source) -> report_result_dto:
        """
        Формирует текстовый отчет по переданной модели рецепта.
        :param source: Модель рецепта (recipe_model)
        :return: report_result_dto с текстовым представлением
        """
        validator.validate(source, recipe_model)
        self.__receipt = source

        header = "Код | Наименование | Брутто | Нетто"
        rows_data = []

        for item in self.__receipt.items:
            rows_data.append(f"{item.unique_code} | {item.name} | {item.brutto} | {item.netto}")

        data = "\n".join(rows_data)
        text = f"{header}\n{data}" if data else header

        result = report_result_dto()
        result.text = text

        return result


TextReport = text_report