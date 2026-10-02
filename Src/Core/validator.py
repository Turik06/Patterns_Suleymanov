from Src.Core.exception import argument_exception, operation_exception


class validator:
    """
    Набор статических проверок данных.
    Централизованная валидация аргументов моделей.
    """

    @staticmethod
    def validate(value, type_, len_=None):
        """
        Валидация аргумента по типу и длине.

        Параметры:
            value: Проверяемый аргумент
            type_: Ожидаемый тип данных
            len_: Максимально допустимая длина (для строк)

        Исключения:
            argument_exception: Некорректный тип, пустое значение или превышение длины

        Возвращает:
            True при успешной валидации
        """
        if value is None:
            raise argument_exception("value", "Пустой аргумент")

        # Проверка типа
        if not isinstance(value, type_):
            raise argument_exception(
                "value",
                f"Некорректный тип! Ожидается {type_}. Текущий тип {type(value)}"
            )

        # Проверка аргумента
        if len(str(value).strip()) == 0:
            raise argument_exception("value", "Пустой аргумент")

        if len_ is not None and len(str(value).strip()) > len_:
            raise argument_exception("value", "Некорректная длина аргумента")

        return True
