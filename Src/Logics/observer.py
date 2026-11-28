from Src.Core.abstract_observabile import abstract_observabile
from Src.Core.validator import validator


class observer:
    """Наблюдатель"""
    handlers: list[abstract_observabile] = []

    @staticmethod
    def add(sourse: abstract_observabile) -> None:
        """Добавить под наблюдение"""
        validator.validate(sourse, abstract_observabile)

        for handler in observer.handlers:
            if handler == sourse:
                return

        observer.handlers.append(sourse)

    @staticmethod
    def delete(sourse: abstract_observabile) -> None:
        """Удалить из-под наблюдения"""
        validator.validate(sourse, abstract_observabile)

        for handler in observer.handlers:
            if handler == sourse:
                observer.handlers.remove(handler)

    @staticmethod
    def create(event_types: str, params: object = None) -> None:
        """Вызвать сообщение"""
        for handler in observer.handlers:
            if handler is not None:
                handler.handler(event_types, params)

    @staticmethod
    def clear() -> None:
        """Очистить список наблюдателей"""
        observer.handlers.clear()
