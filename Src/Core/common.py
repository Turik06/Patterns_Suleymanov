from Src.Core.validator import argument_exception


class common:
    """
    Набор общих статических методов.
    """

    @staticmethod
    def get_fields(source, is_common: bool = False) -> list:
        """
        Получить полный список полей любой модели.
            - is_common = True - исключить из списка словари и списки.
        """
        if source is None:
            raise argument_exception("Некорректно переданы аргументы!")

        items = list(filter(lambda x: not x.startswith("_"), dir(source)))
        result = []

        for item in items:
            attribute = getattr(source.__class__, item)
            if isinstance(attribute, property):
                value = getattr(source, item)

                # Флаг. Только простые типы и модели включать
                if is_common == True and (isinstance(value, dict) or isinstance(value, list)):
                    continue

                result.append(item)

        return result

    """
        Возвращает словарь всех доступных ключей и их описаний.
        Ключ — значение, возвращаемое методом (например, "nomenclature_model").
        Значение — описание из docstring метода (например, "Номенклатура").
    """
    @staticmethod
    def domains(source: object) -> dict:
        result = {}
        
        # Получаем список имен всех статических методов, заканчивающихся на '_key'
        method_names = [
            name for name in dir(source) 
            if callable(getattr(source, name)) and name.endswith('_key')
        ]

        for method_name in method_names:
            # Получаем сам объект метода
            method = getattr(source, method_name)
            
            # Получаем значение ключа (например, "nomenclature_model")
            key_value = method()
            
            # Получаем описание из документации (первая строка docstring)
            docstring = method.__doc__
            description = docstring.strip().split('\n')[0] if docstring else method_name
            
            result[key_value] = description
            
        return result
