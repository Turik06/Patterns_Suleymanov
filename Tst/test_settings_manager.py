import pytest
from Src.Core.validator import operation_exception
from Src.Logics.settings_manager import settings_manager
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model


"""
Набор модульных тестов для класса settings_manager
"""


def test_not_raise_settings_manager_load():
    """
    Ожидание: Загрузка настроек не вызывает исключений.
    Метод: settings_manager.load
    Описание: Проверяет, что вызов load() с дефолтным файлом settings.json
              завершается без выброса operation_exception или иных ошибок.
    """
    # Подготовка
    manager = settings_manager()

    # Действие и проверки
    try:
        manager.load()
    except operation_exception:
        assert False
    except Exception:
        assert False


def test_not_empty_settings_manager_load():
    """
    Ожидание: Настройки не пустые после загрузки.
    Метод: settings_manager.settings (getter)
    Описание: После вызова load() свойство settings не должно быть None.
    """
    # Подготовка
    manager = settings_manager()

    # Действие
    try:
        manager.load()
    except Exception:
        assert False

    # Проверки
    assert manager.settings is not None


def test_equal_settings_manager_create():
    """
    Ожидание: Два экземпляра settings_manager равны (Singleton).
    Метод: settings_manager.__new__
    Описание: Проверяет работу шаблона Singleton — оператор == возвращает True.
    """
    # Подготовка
    instance1 = settings_manager()
    instance2 = settings_manager()

    # Действие

    # Проверки
    assert instance1 == instance2


def test_true_settings_manager_is_loaded():
    """
    Ожидание: is_loaded возвращает True после загрузки.
    Метод: settings_manager.is_loaded (getter)
    Описание: После успешного вызова load() и convert() флаг is_loaded становится True.
    """
    # Подготовка
    manager = settings_manager()

    # Действие
    try:
        manager.load()
    except Exception:
        assert False

    # Проверки
    assert manager.is_loaded == True


def test_same_strings_settings_manager_create():
    """
    Ожидание: Строковые представления и ссылки двух инстансов совпадают (Singleton).
    Метод: settings_manager.__new__
    Описание: Проверяет, что str() и оператор is подтверждают единственность экземпляра.
    """
    # Подготовка
    instance1 = settings_manager()
    instance2 = settings_manager()

    # Действие

    # Проверки
    try:
        assert str(instance1) == str(instance2)
        assert instance1 is instance2
    except Exception:
        assert False


def test_true_settings_manager_convert():
    """
    Ожидание: convert() возвращает True после загрузки данных.
    Метод: settings_manager.convert
    Описание: После load() метод convert() успешно маппит JSON в settings_model.
    """
    # Подготовка
    manager = settings_manager()
    manager.load()

    # Действие
    result = manager.convert()

    # Проверки
    assert result == True


def test_success_settings_manager_convert_organization_fields():
    """
    Ожидание: Все поля организации корректно заполнены после convert().
    Метод: settings_manager.convert
    Описание: Проверяет маппинг полей organization из JSON: name, inn, bik, account, ownership_form.
    """
    # Подготовка
    manager = settings_manager()

    # Действие
    manager.load()

    # Проверки
    org = manager.settings.organization
    assert isinstance(org, organization_model)
    assert org.name == "Ромашка"
    assert org.inn == "7736050003"
    assert org.bik == "044525225"
    assert org.account == "40702810400000000001"
    assert org.ownership_form == "ООО"


def test_success_settings_manager_convert_boss_and_accountant():
    """
    Ожидание: ФИО руководителя и бухгалтера корректно заполнены.
    Метод: settings_manager.convert
    Описание: Проверяет маппинг строковых полей boss_name и account_name из JSON.
    """
    # Подготовка
    manager = settings_manager()

    # Действие
    manager.load()

    # Проверки
    assert manager.settings.boss_name == "Иванов Иван Иванович"
    assert manager.settings.account_name == "Петрова Анна Сергеевна"


def test_true_settings_manager_is_first_start():
    """
    Ожидание: Флаг is_first_start равен True (согласно settings.json).
    Метод: settings_manager.convert
    Описание: Проверяет корректный маппинг булевого флага первого старта.
    """
    # Подготовка
    manager = settings_manager()

    # Действие
    manager.load()

    # Проверки
    assert manager.settings.is_first_start == True


def test_same_settings_manager_singleton_identity():
    """
    Ожидание: Настройки в двух инстансах ссылаются на один объект (Singleton).
    Метод: settings_manager.settings (getter)
    Описание: Тест с пары — в двух инстансах settings_manager объект settings
              один и тот же (is), а организация совпадает (==).
    """
    # Подготовка
    m1 = settings_manager()
    m2 = settings_manager()

    # Действие
    m1.load()

    # Проверки
    assert m1.settings is m2.settings
    assert m1.settings.organization == m2.settings.organization


def test_not_raise_settings_manager_convert_empty_organization_name():
    """
    Ожидание: Конвертация не падает, если имя организации пустое или состоит из пробелов.
    Метод: settings_manager.convert
    Описание: Проверяет безопасную обработку невалидного имени организации: метод convert()
              завершается успешно, не выбрасывая исключение и не ломая загрузку остальных настроек.
    """
    # Подготовка
    manager = settings_manager()
    manager._settings_manager__data = {
        "organization": {
            "name": "   ",
            "inn": "7736050003"
        },
        "boss_name": "Иванов Иван",
        "is_first_start": True
    }

    # Действие
    result = manager.convert()

    # Проверки
    assert result == True
    assert manager.settings.boss_name == "Иванов Иван"
    assert manager.settings.is_first_start == True