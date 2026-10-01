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
    manager = settings_manager()
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
    manager = settings_manager()
    try:
        manager.load()
    except Exception:
        assert False

    assert manager.settings is not None


def test_equal_settings_manager_create():
    """
    Ожидание: Два экземпляра settings_manager равны (Singleton).
    Метод: settings_manager.__new__
    Описание: Проверяет работу шаблона Singleton — оператор == возвращает True.
    """
    instance1 = settings_manager()
    instance2 = settings_manager()
    assert instance1 == instance2


def test_true_settings_manager_is_loaded():
    """
    Ожидание: is_loaded возвращает True после загрузки.
    Метод: settings_manager.is_loaded (getter)
    Описание: После успешного вызова load() и convert() флаг is_loaded становится True.
    """
    manager = settings_manager()
    try:
        manager.load()
    except Exception:
        assert False

    assert manager.is_loaded == True


def test_same_strings_settings_manager_create():
    """
    Ожидание: Строковые представления и ссылки двух инстансов совпадают (Singleton).
    Метод: settings_manager.__new__
    Описание: Проверяет, что str() и оператор is подтверждают единственность экземпляра.
    """
    instance1 = settings_manager()
    instance2 = settings_manager()
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
    manager = settings_manager()
    manager.load()
    assert manager.convert() == True


def test_success_settings_manager_convert_organization_fields():
    """
    Ожидание: Все поля организации корректно заполнены после convert().
    Метод: settings_manager.convert
    Описание: Проверяет маппинг полей organization из JSON: name, inn, bik, account, ownership_form.
    """
    manager = settings_manager()
    manager.load()

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
    manager = settings_manager()
    manager.load()

    assert manager.settings.boss_name == "Иванов Иван Иванович"
    assert manager.settings.account_name == "Петрова Анна Сергеевна"


def test_true_settings_manager_is_first_start():
    """
    Ожидание: Флаг is_first_start равен True (согласно settings.json).
    Метод: settings_manager.convert
    Описание: Проверяет корректный маппинг булевого флага первого старта.
    """
    manager = settings_manager()
    manager.load()

    assert manager.settings.is_first_start == True


def test_same_settings_manager_singleton_identity():
    """
    Ожидание: Настройки в двух инстансах ссылаются на один объект (Singleton).
    Метод: settings_manager.settings (getter)
    Описание: Тест с пары — в двух инстансах settings_manager объект settings
              один и тот же (is), а организация совпадает (==).
    """
    m1 = settings_manager()
    m1.load()

    m2 = settings_manager()
    assert m1.settings is m2.settings
    assert m1.settings.organization == m2.settings.organization