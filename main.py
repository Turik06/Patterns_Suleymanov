from flask import Flask, Response, request
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory
from Src.Dtos.report_type_dto import report_type_dto
from Src.Logics.csv_report import csv_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.xml_report import xml_report
from Src.Logics.html_report import html_report
from Src.Logics.text_report import text_report
from urllib.parse import quote
from Src.Core.exception import argument_exception


"""
Точка входа веб-приложения API формирования отчетов.
"""
app = Flask(__name__)

# Инициализация настроек и первичных данных хранилища
settings = settings_manager()
settings.load()

storage = storage_manager()
storage.load()

factory = report_factory(settings=settings.settings)

# Конфигурация ответов: (mimetype, расширение файла)
REPORT_CONFIG = {
    csv_report: ("text/csv", "csv"),
    markdown_report: ("text/markdown", "md"),
    xml_report: ("application/xml", "xml"),
    html_report: ("text/html", "html"),
    text_report: ("text/plain", "txt"),
}


def find_entity(entity_type: str, entity_id: str):
    """
    Поиск сущности в хранилище по ее типу и коду/имени/индексу.
    """
    type_norm = (entity_type or "recipe").strip().lower()

    if type_norm in ("recipe", "рецепт", "recipes"):
        container = storage.recipes
    elif type_norm in ("nomenclature", "номенклатура", "nomenclatures"):
        container = storage.nomenclatures
    elif type_norm in ("range", "единица_измерения", "единица измерения", "ranges", "unit"):
        container = storage.ranges
    else:
        return None, (
            f"Неизвестный тип сущности '{entity_type}'. "
            f"Поддерживаются: recipe, nomenclature, range."
        )

    if not container:
        return None, f"Хранилище для типа '{entity_type}' пусто."

    clean_id = (entity_id or "").strip()
    if not clean_id:
        return list(container.values())[0], None

    # 1. Поиск по точному ID (ключу словаря)
    if clean_id in container:
        return container[clean_id], None

    # 2. Поиск по unique_code или имени
    for item in container.values():
        if getattr(item, "unique_code", None) == clean_id or getattr(item, "name", "").lower() == clean_id.lower():
            return item, None

    # 3. Поиск по числовому индексу
    if clean_id.isdigit():
        idx = int(clean_id)
        items = list(container.values())
        if 0 <= idx < len(items):
            return items[idx], None

    return None, f"Сущность типа '{entity_type}' с кодом/именем '{entity_id}' не найдена."


def format_response(report, result, entity_name: str) -> Response:
    """
    Универсальное формирование Flask Response по конфигурации класса отчета.
    Бинарные отчеты возвращаются как вложение для скачивания файла.
    """
    mimetype, ext = REPORT_CONFIG.get(report.__class__, ("text/plain", "txt"))
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

    return Response(result.text, status=200, mimetype=mimetype)


def _make_report(entity_type: str, entity_id: str, fmt: str = None) -> Response:
    """
    Единая логика построения отчета.
    Если fmt передан — создается через factory.create(fmt),
    иначе — через factory.create_default().
    """
    entity, err = find_entity(entity_type, entity_id)
    if err:
        return Response(err, status=404, mimetype="text/plain; charset=utf-8")

    try:
        report = factory.create(fmt) if fmt is not None else factory.create_default()
    except argument_exception as ex:
        return Response(str(ex), status=400, mimetype="text/plain; charset=utf-8")

    result = report.build(entity)
    return format_response(report, result, getattr(entity, "name", "report"))


@app.route("/")
@app.route("/api/get_report", methods=["GET"])
def get_report():
    """Отчет по первому доступному рецепту в формате TXT."""
    return _make_report("recipe", "", fmt=report_type_dto.TEXT)


@app.route("/api/report", methods=["GET"])
@app.route("/api/report/<entity_type>/<entity_id>/<report_format>", methods=["GET"])
def get_report_by_format(entity_type: str = "recipe", entity_id: str = "", report_format: str = "txt"):
    """GET endpoint с явным указанием формата, типа и кода сущности."""
    req_type = request.args.get("type") or request.args.get("entity_type") or entity_type
    req_id = request.args.get("code") or request.args.get("id") or request.args.get("entity_id") or entity_id
    req_format = request.args.get("format") or request.args.get("report_format") or report_format
    return _make_report(req_type, req_id, fmt=req_format)


@app.route("/api/report/default", methods=["GET"])
@app.route("/api/report/default/<entity_type>/<entity_id>", methods=["GET"])
def get_report_default(entity_type: str = "recipe", entity_id: str = ""):
    """GET endpoint с использованием отчета по умолчанию из настроек (create_default)."""
    req_type = request.args.get("type") or request.args.get("entity_type") or entity_type
    req_id = request.args.get("code") or request.args.get("id") or request.args.get("entity_id") or entity_id
    return _make_report(req_type, req_id, fmt=None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
