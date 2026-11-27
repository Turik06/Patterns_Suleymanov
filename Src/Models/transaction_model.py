import datetime
from Src.Core.abstract_model import abstract_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.exception import argument_exception


class transaction_model(abstract_model):
    """Складская транзакция"""

    def __init__(
        self,
        storage: storage_model = None,
        nomenclature: nomenclature_model = None,
        range_unit: range_model = None,
        value: float = 0.0,
        period: datetime.datetime = None,
    ):
        super().__init__()
        self.__storage = storage
        self.__nomenclature = nomenclature
        self.__range = range_unit
        self.__value = float(value)
        self.__period = period or datetime.datetime.now()
        nom_name = getattr(nomenclature, "name", "")
        self.name = f"Транзакция {nom_name}".strip()[:50] or "Транзакция"

    @property
    def value(self) -> float:
        return self.__value

    @value.setter
    def value(self, source: float) -> None:
        if source == 0:
            raise argument_exception("value", "Значение = 0")
        self.__value = float(source)

    @property
    def storage(self) -> storage_model:
        return self.__storage

    @storage.setter
    def storage(self, val: storage_model) -> None:
        self.__storage = val

    @property
    def nomenclature(self) -> nomenclature_model:
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, val: nomenclature_model) -> None:
        self.__nomenclature = val

    @property
    def range(self) -> range_model:
        return self.__range

    @range.setter
    def range(self, val: range_model) -> None:
        self.__range = val

    @property
    def period(self) -> datetime.datetime:
        return self.__period

    @period.setter
    def period(self, val: datetime.datetime) -> None:
        self.__period = val

    def references(self) -> list:
        refs = []
        if self.__storage:
            refs.append(self.__storage)
        if self.__nomenclature:
            refs.append(self.__nomenclature)
        if self.__range:
            refs.append(self.__range)
        return refs
