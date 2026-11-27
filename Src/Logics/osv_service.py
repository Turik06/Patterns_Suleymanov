from Src.Core.validator import validator
from Src.Dtos.filter_dto import filter_dto, filter_item_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Logics.prototype import prototype
from Src.Logics.storage_manager import storage_manager
from Src.Models.osv_row_model import osv_row_model


class osv_service:
    """Сервис для формирования ОСВ"""

    def __init__(self, storage: storage_manager = None):
        if storage is not None:
            validator.validate(storage, storage_manager)
            self.__storage = storage
        else:
            self.__storage = storage_manager()

    @property
    def storage(self) -> storage_manager:
        return self.__storage

    def build_osv(self, filter_item: filter_dto = None) -> list[osv_row_model]:
        """Сформировать ОСВ"""
        transactions = list(self.__storage.transactions.values())
        if not transactions:
            data = self.__storage.data.get(self.__storage.transaction_key(), [])
            transactions = list(data)

        proto = prototype(transactions)

        start_date = getattr(filter_item, "start_date", None) if filter_item else None
        end_date = getattr(filter_item, "end_date", None) if filter_item else None

        extra_filters = []
        if filter_item:
            for f in filter_item.all_filters:
                if f.field_name != "period":
                    extra_filters.append(f)

        grouped = {}

        # отбираем прототипом транзакции до даты и считаем начальный остаток
        if start_date:
            before_filters = [
                filter_item_dto("period", filter_type_enum.LESS_THAN, start_date)
            ] + extra_filters
            for tr in proto.clone(filter_dto(filters=before_filters)).data:
                st = getattr(tr, "storage", None)
                nom = getattr(tr, "nomenclature", None)
                rng = getattr(tr, "range", None)
                val = float(getattr(tr, "value", 0.0))
                key = (getattr(st, "id", None), getattr(nom, "id", None), getattr(rng, "id", None))
                if key not in grouped:
                    grouped[key] = {
                        "storage": st,
                        "nomenclature": nom,
                        "range": rng,
                        "start_balance": 0.0,
                        "incoming": 0.0,
                        "outgoing": 0.0,
                    }
                grouped[key]["start_balance"] += val

        # отбираем прототипом транзакции за период и считаем обороты
        period_filters = list(extra_filters)
        if start_date:
            period_filters.append(
                filter_item_dto("period", filter_type_enum.GREATER_EQUALS, start_date)
            )
        if end_date:
            period_filters.append(
                filter_item_dto("period", filter_type_enum.LESS_EQUALS, end_date)
            )

        period_proto = proto.clone(filter_dto(filters=period_filters)) if period_filters else proto
        for tr in period_proto.data:
            st = getattr(tr, "storage", None)
            nom = getattr(tr, "nomenclature", None)
            rng = getattr(tr, "range", None)
            val = float(getattr(tr, "value", 0.0))
            key = (getattr(st, "id", None), getattr(nom, "id", None), getattr(rng, "id", None))
            if key not in grouped:
                grouped[key] = {
                    "storage": st,
                    "nomenclature": nom,
                    "range": rng,
                    "start_balance": 0.0,
                    "incoming": 0.0,
                    "outgoing": 0.0,
                }
            if val > 0:
                grouped[key]["incoming"] += val
            else:
                grouped[key]["outgoing"] += abs(val)

        # формируем строки отчета
        rows = [
            osv_row_model(
                storage=item["storage"],
                nomenclature=item["nomenclature"],
                range_unit=item["range"],
                start_balance=item["start_balance"],
                incoming=item["incoming"],
                outgoing=item["outgoing"],
            )
            for item in grouped.values()
        ]

        # фильтрация итоговых строк если заданы условия
        if filter_item and filter_item.all_filters:
            rows = prototype(rows).clone(filter_item).data

        return rows

    def get_osv_response(self, filter_item: filter_dto = None):
        """Ответ для API"""
        rows = self.build_osv(filter_item)
        return [row.to_dict() for row in rows], 200
