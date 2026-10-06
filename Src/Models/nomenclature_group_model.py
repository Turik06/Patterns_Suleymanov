from Src.Core.abstract_model import name_id


class nomenclature_group_model(name_id):
    """
    Модель группы номенклатуры.
    Категория для объединения позиций номенклатуры (например, "Мясо", "Овощи", "Молочные продукты").
    """

    def __init__(self, name=""):
        """
        Конструктор группы номенклатуры.

        Параметры:
            name: Наименование группы (до 50 символов)
        """
        super().__init__()
        self.name = name

    @staticmethod
    def create_grocery():
        """Фабричный метод: создать группу 'Бакалея'."""
        return nomenclature_group_model(name="Бакалея")

    @staticmethod
    def create_dairy():
        """Фабричный метод: создать группу 'Молочные продукты'."""
        return nomenclature_group_model(name="Молочные продукты")

    @staticmethod
    def create_dishes():
        """Фабричный метод: создать группу 'Блюда'."""
        return nomenclature_group_model(name="Блюда")

    @staticmethod
    def create_primary_list() -> list:
        """Фабричный метод: создать первичный список всех групп номенклатуры."""
        return [
            nomenclature_group_model.create_grocery(),
            nomenclature_group_model.create_dairy(),
            nomenclature_group_model.create_dishes(),
        ]
