# Исключение. Обработка аргументов
class argument_exception(Exception):
    """
    Пользовательское исключение для некорректных аргументов моделей.
    
    """

    def __init__(self, field="", message="", stack_trace=""):
        """
        Конструктор исключения некорректного аргумента.
        <param name="field">Наименование ошибочного аргумента/поля</param>
        <param name="message">Поясняющее сообщение об ошибке</param>
        <param name="stack_trace">Стек вызовов (трассировка)</param>
        """
        self.__field = str(field).strip() if field is not None else ""
        self.__message = str(message).strip() if message is not None else ""
        self.__stack_trace = str(stack_trace).strip() if stack_trace is not None else ""
        super().__init__(str(self))

    @property
    def field(self):
        """
        Поле/аргумент с ошибкой.
        """
        return self.__field

    @property
    def message(self):
        """
        Сообщение об ошибке.
        """
        return self.__message

    @property
    def stack_trace(self):
        """
        Трассировка стека ошибки.
        """
        return self.__stack_trace

    def __str__(self):
        """
        Строковое представление ошибки.
        """
        parts = [f"Ошибка: Некорректный аргумент! {self.__field}".strip()]
        if self.__message:
            parts.append(self.__message)
        if self.__stack_trace:
            parts.append(self.__stack_trace)
        return "\n".join(parts)


# Алиас для обратной совместимости
arguments_exception = argument_exception
