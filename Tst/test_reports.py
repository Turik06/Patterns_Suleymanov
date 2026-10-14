import pytest
from Src.Core.abstract_report import abstract_report, AbstractReport
from Src.Core.exception import argument_exception
from Src.Dtos.report_result_dto import report_result_dto
from Src.Dtos.report_type_dto import report_type_dto, ReportTypeEnum
from Src.Logics.report_factory import report_factory, ReportFactory
from Src.Logics.text_report import text_report, TextReport
from Src.Models.nomenclature_group_model import nomenclature_group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model


def test_success_report_factory_create_text_report():
    """
    <summary>
    Проверка успешного создания инстанса текстового отчета через абстрактную фабрику.
    </summary>
    <description>
    Arrange: Инициализация фабрики report_factory.
    Act: Вызов create с поддерживаемым типом отчета TXT.
    Assert: Созданный объект не None, является экземпляром abstract_report и text_report.
    </description>
    """
    # Arrange
    factory = report_factory()

    # Act
    report = factory.create(report_type_dto.TXT)

    # Assert
    assert report is not None
    assert isinstance(report, abstract_report)
    assert isinstance(report, text_report)


def test_fail_report_factory_create_unsupported_type_raises_argument_exception():
    """
    <summary>
    Проверка выброса исключения при попытке запросить нереализованный тип отчета.
    </summary>
    <description>
    Arrange: Инициализация фабрики report_factory.
    Act & Assert: При передаче некорректного значения или None генерируется argument_exception.
    </description>
    """
    # Arrange
    factory = report_factory()

    # Act & Assert
    with pytest.raises(argument_exception):
        factory.create("UNSUPPORTED_TYPE")

    with pytest.raises(argument_exception):
        factory.create(None)


def test_success_full_chain_report_factory_build_recipe():
    """
    <summary>
    Сквозной тест генерации отчета по рецепту через фабрику отчетов.
    </summary>
    <description>
    Arrange: Инициализация фабрики, создание рецепта с строками ингредиентов.
    Act: Получение инстанса отчета через factory.create и генерация отчета методом build.
    Assert: Результат является report_result_dto, текст содержит заголовок и строки брутто/нетто.
    </description>
    """
    # Arrange
    factory = report_factory()
    group = nomenclature_group_model.create_grocery()
    gram = range_model.create_gram()
    flour = nomenclature_model.create_flour(group, gram)
    sugar = nomenclature_model.create_sugar(group, gram)

    recipe = recipe_model("Блинчики классические")
    row_flour = recipe_row_model(flour, 100.0, 95.0, gram)
    row_sugar = recipe_row_model(sugar, 20.0, 20.0, gram)
    recipe.add_row(row_flour)
    recipe.add_row(row_sugar)

    # Act
    report = factory.create(report_type_dto.TXT)
    result = report.build(recipe)

    # Assert
    assert result is not None
    assert isinstance(result, report_result_dto)
    assert result.text != ""
    assert "Код | Наименование | Брутто | Нетто" in result.text
    assert f"{row_flour.unique_code} | Мука пшеничная | 100.0 | 95.0" in result.text
    assert f"{row_sugar.unique_code} | Сахар | 20.0 | 20.0" in result.text
