from flask import Flask, Response, request
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory
from Src.Dtos.report_type_dto import report_type_dto


"""
Точка входа веб-приложения API формирования отчетов.
"""
app = Flask(__name__)

# Инициализация менеджеров настроек и хранилища данных (первый старт)
settings = settings_manager()
settings.load()

storage = storage_manager()
storage.load()

factory = report_factory()


@app.route("/")
@app.route("/api/get_report", methods=["GET"])
def get_report():
    """
    HTTP GET endpoint формирования отчета по рецепту.
    :return: Текстовый результат формирования отчета или сообщение об ошибке
    """
    if not storage.recipes:
        return Response("Рецепты в хранилище не найдены", status=404, mimetype="text/plain; charset=utf-8")

    # Берем первый доступный рецепт из первого старта
    recipe = storage.recipes[0]

    report = factory.create(report_type_dto.TEXT)
    result = report.build(recipe)

    return Response(result.text, status=200, mimetype="text/plain; charset=utf-8")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
