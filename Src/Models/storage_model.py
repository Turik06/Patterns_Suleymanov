from Src.Core.abstract_model import name_id


class storage_model(name_id):
    """
    Модель склада.
    Место хранения запасов продуктов и заготовок (например, "Основной склад", "Холодильник цеха").
    """

    def __init__(self, name=""):
        """
        Конструктор склада.
        <param name="name">Наименование склада (до 50 символов)</param>
        """
        super().__init__()
        self.name = name
