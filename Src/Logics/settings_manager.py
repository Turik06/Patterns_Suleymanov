import os
import json
from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator, operation_exception
from Src.Core.common import common
from Src.Core.exception import argument_exception
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model
from Src.Dtos.report_type_enum import report_type_enum
from Src.Dtos.response_format_dto import response_format_dto


class settings_manager(abstract_manager):
    """
    Менеджер для работы с настройками приложения.
    Реализует шаблон Singleton и загрузку данных через интроспекцию моделей.
    """
    __default_file_name: str = "settings.json"

    _settings: settings_model = None
    __data: dict = None

    # Singleton
    def __new__(cls):
        """
        Реализация шаблона Singleton. Возвращает единственный экземпляр класса.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        """
        Конструктор менеджера настроек. Инициализирует поля модели настроек и данных.
        """
        if not hasattr(self, "_settings") or self._settings is None:
            self._settings = settings_model()
            self.__data = {}

    def load(self, file_name: str = "") -> None:
        """
        Загружает данные настроек из JSON файла.
        """
        inner_file_name = file_name.strip() if file_name.strip() != "" else self.__default_file_name
        validator.validate(inner_file_name, str)

        full_file_name = os.path.abspath(inner_file_name)
        if not os.path.exists(full_file_name):
            raise operation_exception(f"Не найден указанный файл {full_file_name}")

        try:
            with open(full_file_name, "r", encoding="utf-8") as file:
                self.__data = json.load(file)

            self.is_loaded = self.build()
            if not self.is_loaded:
                self._settings = self.__create_default_data()

        except operation_exception:
            raise
        except Exception as ex:
            raise operation_exception(
                f"Ошибка при загрузке и обработке файла: {inner_file_name}. Детали: {ex}"
            ) from ex

    def build(self) -> bool:
        """Загрузка настроек через десериализацию"""
        if not isinstance(self.__data, dict) or len(self.__data) == 0:
            return False

        try:
            if self._settings is None:
                self._settings = settings_model()

            org_data = self.__data.get("organization") or self.__data.get("company")
            if not isinstance(org_data, dict):
                org_data = {}
                for k, v in self.__data.items():
                    if k.startswith("company_"):
                        org_data[k[len("company_"):]] = v

            if isinstance(org_data, dict) and len(org_data) > 0:
                from Src.Logics.convertor import convertor
                worker = convertor()
                org_dto = worker.resolve_dto(org_data, type_hint="organization")
                if org_dto:
                    from Src.Logics.mapping_factory import mapping_factory
                    org_model = mapping_factory().to_model(org_dto)
                    if org_model:
                        self._settings.organization = org_model

            if "first_start" in self.__data:
                self._settings.is_first_start = bool(self.__data.get("first_start"))
            elif "is_first_start" in self.__data:
                self._settings.is_first_start = bool(self.__data.get("is_first_start"))

            if "boss_name" in self.__data and self.__data["boss_name"]:
                self._settings.boss_name = str(self.__data["boss_name"])

            if "account_name" in self.__data and self.__data["account_name"]:
                self._settings.account_name = str(self.__data["account_name"])

            if "response_format" in self.__data:
                self._settings.response_format = self.convert_report_type(self.__data["response_format"])

            return True

        except Exception:
            return False

    @staticmethod
    def convert_report_type(value) -> report_type_enum:
        """
        Преобразование произвольного формата (строки, числа, Enum) в report_type_enum.
        Инкапсулирует логику разбора формата данных настроек.
        """
        if value is None:
            raise argument_exception("report_type", "Тип отчета не может быть пустым!")
        if isinstance(value, report_type_enum):
            return value

        candidates = [value]
        if hasattr(value, "name"):
            candidates.append(value.name)
        if hasattr(value, "value"):
            candidates.append(value.value)

        aliases = {
            "TEXT": report_type_enum.TXT,
            "MD": report_type_enum.MARKDOWN,
        }

        for item in candidates:
            if isinstance(item, int) or (isinstance(item, str) and str(item).strip().isdigit()):
                try:
                    return report_type_enum(int(item))
                except ValueError:
                    pass

            key = str(item).strip().upper()
            if key in report_type_enum.__members__:
                return report_type_enum[key]
            if key in aliases:
                return aliases[key]

        raise argument_exception("report_type", f"Указанный тип отчета '{value}' не реализован!")

    def convert(self) -> bool:
        """
        Преобразует сырые данные JSON в объект settings_model.
        Псевдоним метода build() для обратной совместимости.
        """
        return self.build()

    def __create_default_data(self) -> settings_model:
        """
        Сформировать настройки по умолчанию при ошибке обработки данных.
        """
        result = settings_model()

        company = organization_model(
            name="ООО Ромашка",
            inn="7736050003",
            bik="044525225",
            account="40812810400000000225",
            ownership_form="ООО"
        )

        result.organization = company
        result.boss_name = "Шеметов Александр Борисович"
        result.account_name = "Сулейманов Турал Кямалович"
        result.is_first_start = True
        result.response_format = report_type_enum.HTML
        return result

    @property
    def settings(self) -> settings_model:
        """Объект настроек settings_model."""
        return self._settings