import os
from datetime import datetime
from Src.Core.abstract_observabile import abstract_observabile
from Src.Core.event_type import event_type
from Src.Logics.observer import observer


class logger_service(abstract_observabile):
    """Сервис логирования событий"""

    __log_file: str = "logs/app.log"
    __events = (
        event_type.change_settings(),
        event_type.load_settings(),
        event_type.crud_operation(),
        event_type.storage_operation(),
        event_type.web_call(),
    )

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(logger_service, cls).__new__(cls)
        return cls.instance

    def __init__(self, log_file: str = None):
        if log_file:
            self.__log_file = log_file
        observer.add(self)

    @property
    def log_file(self) -> str:
        return self.__log_file

    @log_file.setter
    def log_file(self, value: str) -> None:
        self.__log_file = value

    def handler(self, event_types: str, params: object = None) -> None:
        """Обработка и запись события в лог"""
        if event_types not in self.__events:
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        description = event_type.events().get(event_types, "")
        desc_part = f" {description}" if description else ""
        details = f" | {params}" if params is not None else ""
        line = f"[{now}] | [{event_types}]{desc_part}{details}"

        print(line)
        log_dir = os.path.dirname(self.__log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        with open(self.__log_file, "a", encoding="utf-8") as file:
            file.write(line + "\n")
