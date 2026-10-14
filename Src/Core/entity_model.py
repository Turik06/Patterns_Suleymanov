from Src.Core.abstract_model import abstract_model, abstact_model, name_id


class entity_model(abstract_model):
    """
    Общий класс для наследования сущностей предметной области.
    Содержит стандартное определение: уникальный идентификатор (id / unique_code) и наименование (name).
    """

    def __init__(self, name: str = ""):
        """
        Конструктор базовой сущности.

        Параметры:
            name: Наименование сущности (опционально).
        """
        super().__init__()
        if name and str(name).strip():
            self.name = str(name).strip()
