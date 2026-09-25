from Src.Core.abstract_model import name_id


class nomenclature_group_model(name_id):
    """
    Модель группы номенклатуры.
    Категория для объединения позиций номенклатуры (например, "Мясо", "Овощи", "Молочные продукты").
    """

    def __init__(self, name=""):
        """
        Конструктор группы номенклатуры.
        <param name="name">Наименование группы (до 50 символов)</param>
        """
        super().__init__()
        self.name = name
