from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator, operation_exception
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model
import json


class settings_manager(abstract_manager):
    __default_file_name: str = "settings.json"

    _settings: settings_model = None
    __is_loaded: bool = False
    __data: dict = None

    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance

    def load(self, file_name: str = "") -> None:
        """
        Загружает данные настроек из JSON файла.
        """
        file_name = file_name.strip() or self.__default_file_name
        validator.validate(file_name, str)

        try:
            with open(file_name, "r", encoding="utf-8") as file:
                self.__data = json.load(file)

            self.__is_loaded = self.convert()

        except Exception as ex:
            raise operation_exception(
                f"Ошибка при загрузке данных из файла {file_name}: {ex}"
            ) from ex

    def convert(self) -> bool:
        """
        Преобразует сырые данные JSON в объект settings_model.
        """
        if not isinstance(self.__data, dict):
            return False

        try:
            if self._settings is None:
                self._settings = settings_model()

            # 1. Заполняем организацию
            org = self.__data.get("organization")
            if isinstance(org, dict):
                name = str(org.get("name", "")).strip()
                inn = str(org.get("inn", "")).strip()
                if name and inn:
                    try:
                        self._settings.organization = organization_model(**org)
                    except Exception:
                        pass

            # 2. Заполняем ФИО руководителя и бухгалтера
            for key in ("boss_name", "account_name"):
                value = self.__data.get(key)
                if value and str(value).strip():
                    setattr(self._settings, key, str(value).strip())

            # 3. Заполняем флаг первого старта
            if "is_first_start" in self.__data:
                self._settings.is_first_start = bool(self.__data.get("is_first_start"))

            return True

        except Exception:
            return False

    @property
    def is_loaded(self) -> bool:
        """Флаг успешности загрузки настроек."""
        return self.__is_loaded

    @property
    def settings(self) -> settings_model:
        """Объект настроек settings_model."""
        return self._settings