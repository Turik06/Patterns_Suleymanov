import pytest
from Src.Core.validator import operation_exception
from Src.Logics.settings_manager import settings_manager
from Src.Models.settings_model import settings_model
from Src.Models.organization_model import organization_model


"""
Набор модульных тестов для класса settings_manager
"""


def test_not_raise_settings_manager_load():
    """Загрузка настроек не вызывает исключений."""
    manager = settings_manager()
    try:
        manager.load()
    except operation_exception:
        assert False
    except Exception:
        assert False


def test_not_empty_settings_manager_load():
    """Проверить загрузку настроек. Настройки не пустые."""
    manager = settings_manager()
    try:
        manager.load()
    except Exception:
        assert False

    assert manager.settings is not None


def test_equall_settings_manager_create():
    """Проверить работу шаблона Singletone."""
    instance1 = settings_manager()
    instance2 = settings_manager()
    assert instance1 == instance2


def test_is_loaded_settings_manager_true():
    """Проверить загрузку и конвертацию настроек."""
    manager = settings_manager()
    try:
        manager.load()
    except Exception:
        assert False

    assert manager.is_loaded == True


def test_same_strings_settings_manager_create():
    """Проверить создание settings_manager: одинаковые строки и ссылки (Singletone)."""
    instance1 = settings_manager()
    instance2 = settings_manager()
    try:
        assert str(instance1) == str(instance2)
        assert instance1 is instance2
    except Exception:
        assert False


def test_convert_settings_manager_returns_true():
    """Проверить, что convert() возвращает True после успешной загрузки."""
    manager = settings_manager()
    manager.load()
    assert manager.convert() == True


def test_convert_settings_manager_organization_fields():
    """Проверить корректность маппинга всех полей организации."""
    manager = settings_manager()
    manager.load()

    org = manager.settings.organization
    assert isinstance(org, organization_model)
    assert org.name == "Ромашка"
    assert org.inn == "7736050003"
    assert org.bik == "044525225"
    assert org.account == "40702810400000000001"
    assert org.ownership_form == "ООО"


def test_convert_settings_manager_boss_and_accountant():
    """Проверить корректность маппинга ФИО руководителя и бухгалтера."""
    manager = settings_manager()
    manager.load()

    assert manager.settings.boss_name == "Иванов Иван Иванович"
    assert manager.settings.account_name == "Петрова Анна Сергеевна"


def test_convert_settings_manager_is_first_start():
    """Проверить корректность маппинга флага первого старта."""
    manager = settings_manager()
    manager.load()

    assert manager.settings.is_first_start == True


def test_singleton_settings_manager_settings_are_same():
    """
    Тест с пары: проверить, что в двух инстансах settings_manager
    настройки одинаковые и ссылаются на один и тот же объект.
    """
    m1 = settings_manager()
    m1.load()

    m2 = settings_manager()
    assert m1.settings is m2.settings
    assert m1.settings.organization == m2.settings.organization