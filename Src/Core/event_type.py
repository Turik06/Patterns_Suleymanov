class event_type:
    """Типы сообщений"""

    @staticmethod
    def change_settings() -> str:
        """Изменены настройки"""
        return "change_settings"

    @staticmethod
    def load_settings() -> str:
        """Загружены настройки"""
        return "load_settings"

    @staticmethod
    def crud_operation() -> str:
        """CRUD операция"""
        return "crud_operation"

    @staticmethod
    def storage_operation() -> str:
        """Складская операция"""
        return "storage_operation"

    @staticmethod
    def web_call() -> str:
        """Вызов web метода"""
        return "web_call"

    @staticmethod
    def events() -> dict:
        """Словарь зарегистрированных событий и их описаний"""
        result = {}
        for name in dir(event_type):
            if name.startswith("_") or name == "events":
                continue
            method = getattr(event_type, name)
            if callable(method):
                doc = method.__doc__.strip().split("\n")[0] if method.__doc__ else name
                result[method()] = doc
        return result
