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



class max_length_exception(argument_exception):
    """
    Исключение при превышении максимальной длины строкового поля.
    """

    def __init__(self, field="", current_length=0, max_length=0):
        """
        Конструктор исключения превышения длины.
        <param name="field">Наименование поля, в котором превышена длина</param>
        <param name="current_length">Текущая длина значения</param>
        <param name="max_length">Максимально допустимая длина</param>
        """
        self.__current_length = current_length
        self.__max_length = max_length
        message = (
            f"Превышена максимальная длина поля! "
            f"Текущая: {current_length}, максимальная: {max_length}"
        )
        super().__init__(field, message)

    @property
    def current_length(self):
        """
        Текущая длина значения поля.
        """
        return self.__current_length

    @property
    def max_length(self):
        """
        Максимально допустимая длина поля.
        """
        return self.__max_length


# Алиас для обратной совместимости
arguments_exception = argument_exception
