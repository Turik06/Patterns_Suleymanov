from Src.Core.abstract_model import name_id
from Src.Core.exception import argument_exception


class organization_model(name_id):
    """
    Модель организации (юридического лица).
    Содержит реквизиты: ИНН, БИК, расчётный счёт, форму собственности.
    """

    def __init__(self, name="", inn="", bik="", account="", ownership_form=""):
        """
        Конструктор организации.

        Параметры:
            name: Наименование организации (до 50 символов)
            inn: ИНН (10 или 12 цифр)
            bik: БИК (9 цифр)
            account: Расчётный счёт (20 цифр)
            ownership_form: Форма собственности (например, "ООО", "ИП", "ПАО", до 5 символов)
        """
        super().__init__()
        self.name = name
        self.inn = inn
        self.bik = bik
        self.account = account
        self.ownership_form = ownership_form

    @property
    def inn(self):
        """
        Возвращает ИНН организации.
        """
        return self.__inn

    @inn.setter
    def inn(self, value):
        """
        Задаёт ИНН организации. Допустимая длина — 10 или 12 цифр.
        """
        if not isinstance(value, str):
            raise argument_exception("inn", "ИНН должен быть строкой")

        value = value.strip()

        if not value.isdigit():
            raise argument_exception("inn", "ИНН должен содержать только цифры")

        if len(value) not in (10, 12):
            raise argument_exception("inn", "ИНН должен содержать 10 или 12 цифр")

        self.__inn = value

    @property
    def bik(self):
        """
        Возвращает БИК организации.
        """
        return self.__bik

    @bik.setter
    def bik(self, value):
        """
        Задаёт БИК организации. Допустимая длина — 9 цифр.
        """
        if not isinstance(value, str):
            raise argument_exception("bik", "БИК должен быть строкой")

        value = value.strip()

        if not value.isdigit():
            raise argument_exception("bik", "БИК должен содержать только цифры")

        if len(value) != 9:
            raise argument_exception("bik", "БИК должен содержать 9 цифр")

        self.__bik = value

    @property
    def account(self):
        """
        Возвращает расчётный счёт организации.
        """
        return self.__account

    @account.setter
    def account(self, value):
        """
        Задаёт расчётный счёт организации. Допустимая длина — 20 цифр.
        """
        if not isinstance(value, str):
            raise argument_exception("account", "Счёт должен быть строкой")

        value = value.strip()

        if not value.isdigit():
            raise argument_exception("account", "Счёт должен содержать только цифры")

        if len(value) != 20:
            raise argument_exception("account", "Счёт должен содержать 20 цифр")

        self.__account = value

    @property
    def ownership_form(self):
        """
        Возвращает форму собственности организации.
        """
        return self.__ownership_form

    @ownership_form.setter
    def ownership_form(self, value):
        """
        Задаёт форму собственности организации. Максимальная длина — 5 символов.
        """
        if not isinstance(value, str):
            raise argument_exception("ownership_form", "Форма собственности должна быть строкой")

        value = value.strip()

        if value == "":
            raise argument_exception("ownership_form", "Форма собственности не должна быть пустой")

        if len(value) > 5:
            raise argument_exception("ownership_form", "Форма собственности не должна превышать 5 символов")

        self.__ownership_form = value
