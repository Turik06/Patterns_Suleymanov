from flask import Flask, Response, request
from urllib.parse import quote
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory
from Src.Core.exception import argument_exception


app = Flask(__name__)

# Инициализация настроек и первичных данных хранилища
settings = settings_manager()
settings.load()

storage = storage_manager()
storage.load()

factory = report_factory(settings=settings.settings)


def find_recipe(recipe_id: str = ""):
    """
    Поиск рецепта в хранилище по его уникальному коду, наименованию или индексу.
    """
    recipes = storage.recipes
    if not recipes:
        return None, "Хранилище рецептов пусто."

    clean_id = (recipe_id or "").strip()
    if not clean_id:
        return list(recipes.values())[0], None

    if clean_id in recipes:
        return recipes[clean_id], None

    for item in recipes.values():
        if (
            getattr(item, "unique_code", None) == clean_id
            or getattr(item, "name", "").lower() == clean_id.lower()
        ):
            return item, None

    if clean_id.isdigit():
        idx = int(clean_id)
        items = list(recipes.values())
        if 0 <= idx < len(items):
            return items[idx], None

    return None, f"Рецепт с кодом/именем '{recipe_id}' не найден."


def format_response(report, result, entity_name: str) -> Response:
    """
    Формирование HTTP ответа на основе свойств объекта отчета (MIME-тип, расширение, бинарность).
    """
    mimetype = getattr(report, "mime_type", "text/plain")
    ext = getattr(report, "extension", "txt")
    safe_name = entity_name.replace(" ", "_")
    encoded_name = quote(safe_name)

    if result.binary:
        return Response(
            bytes(result.binary),
            status=200,
            mimetype=mimetype,
            headers={
                "Content-Disposition": f"attachment; filename=\"report.{ext}\"; filename*=UTF-8''{encoded_name}.{ext}"
            },
        )

    return Response(result.text, status=200, mimetype=f"{mimetype}; charset=utf-8")


def _make_report(recipe_id: str = "", fmt: str = None) -> Response:
    """
    Единая логика построения отчета по рецепту.
    """
    recipe, err = find_recipe(recipe_id)
    if err:
        return Response(err, status=404, mimetype="text/plain; charset=utf-8")

    try:
        report = factory.create(fmt) if fmt is not None else factory.create_default()
    except argument_exception as ex:
        return Response(str(ex), status=400, mimetype="text/plain; charset=utf-8")

    result = report.build(recipe)
    return format_response(report, result, getattr(recipe, "name", "report"))


@app.route("/")
@app.route("/api/get_report", methods=["GET"])
def get_report():
    """Отчет по первому доступному рецепту в формате TXT."""
    return _make_report("", fmt="txt")


@app.route("/api/report", methods=["GET"])
@app.route("/api/report/<recipe_id>/<report_format>", methods=["GET"])
@app.route("/api/report/<entity_type>/<recipe_id>/<report_format>", methods=["GET"])
def get_report_by_format(recipe_id: str = "", report_format: str = "txt", entity_type: str = "recipe"):
    """GET endpoint с явным указанием формата и кода рецепта."""
    req_id = (
        request.args.get("code")
        or request.args.get("id")
        or request.args.get("recipe_id")
        or recipe_id
    )
    req_format = (
        request.args.get("format")
        or request.args.get("report_format")
        or report_format
    )
    return _make_report(req_id, fmt=req_format)


@app.route("/api/report/default", methods=["GET"])
@app.route("/api/report/default/<recipe_id>", methods=["GET"])
@app.route("/api/report/default/<entity_type>/<recipe_id>", methods=["GET"])
def get_report_default(recipe_id: str = "", entity_type: str = "recipe"):
    """GET endpoint с использованием отчета по умолчанию из настроек."""
    req_id = (
        request.args.get("code")
        or request.args.get("id")
        or request.args.get("recipe_id")
        or recipe_id
    )
    return _make_report(req_id, fmt=None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
