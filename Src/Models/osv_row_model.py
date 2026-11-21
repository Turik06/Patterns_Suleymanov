from Src.Core.abstract_model import abstract_model


class osv_row_model(abstract_model):
    """Строка оборотно-сальдовой ведомости"""

    def __init__(self, storage=None, nomenclature=None, range_unit=None, start_balance: float = 0.0, incoming: float = 0.0, outgoing: float = 0.0):
        super().__init__()
        self.storage = storage
        self.nomenclature = nomenclature
        self.range = range_unit
        self.start_balance = float(start_balance)
        self.incoming = float(incoming)
        self.outgoing = float(outgoing)
        nom_name = getattr(nomenclature, "name", "")
        self.name = f"ОСВ {nom_name}".strip()[:50] or "Строка ОСВ"

    @property
    def final_balance(self) -> float:
        return self.start_balance + self.incoming - self.outgoing

    def references(self) -> list:
        refs = []
        if self.storage:
            refs.append(self.storage)
        if self.nomenclature:
            refs.append(self.nomenclature)
        if self.range:
            refs.append(self.range)
        return refs

    def to_dict(self) -> dict:
        return {
            "storage": getattr(self.storage, "name", ""),
            "nomenclature": getattr(self.nomenclature, "name", ""),
            "range": getattr(self.range, "name", ""),
            "start_balance": self.start_balance,
            "incoming": self.incoming,
            "outgoing": self.outgoing,
            "final_balance": self.final_balance,
        }
