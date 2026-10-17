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

KNOWN_ENTITY_TYPES = {
    "recipe", "рецепт", "recipes", "рецепты",
    "nomenclature", "номенклатура", "nomenclatures",
    "range", "единица измерения", "единица_измерения", "единицы_измерения", "единица", "ranges", "unit", "units",
}

KNOWN_FORMATS = {
    "txt", "text", "csv", "md", "markdown", "xml", "html", "rtf"
}


def normalize_entity_type(raw_type: str = "") -> str:
    """Нормализация строкового обозначения типа сущности."""
    cleaned = (raw_type or "").strip().lower()
    if cleaned in ("nomenclature", "номенклатура", "nomenclatures"):
        return "nomenclature"
    if cleaned in ("range", "единица измерения", "единица_измерения", "единицы_измерения", "единица", "ranges", "unit", "units"):
        return "range"
    if cleaned in ("recipe", "рецепт", "рецепты", "recipes", ""):
        return "recipe"
    return cleaned


def find_entity(entity_type: str = "recipe", entity_id: str = ""):
    """
    Поиск сущности указанного типа (Номенклатура, Единица измерения, Рецепт)
    в хранилище по уникальному коду, наименованию или индексу.
    """
    etype = normalize_entity_type(entity_type)
    if etype == "recipe":
        catalog = storage.recipes
        type_label = "Рецепт"
    elif etype == "nomenclature":
        catalog = storage.nomenclatures
        type_label = "Номенклатура"
    elif etype == "range":
        catalog = storage.ranges
        type_label = "Единица измерения"
    else:
        return None, f"Неизвестный тип сущности '{entity_type}'. Поддерживаются: 'nomenclature' (Номенклатура), 'range' (Единица измерения), 'recipe' (Рецепт)."

    if not catalog:
        return None, f"Хранилище для '{type_label}' пусто."

    clean_id = (entity_id or "").strip()
    if not clean_id:
        return list(catalog.values())[0], None

    if clean_id in catalog:
        return catalog[clean_id], None

    for item in catalog.values():
        if (
            getattr(item, "unique_code", None) == clean_id
            or getattr(item, "id", None) == clean_id
            or getattr(item, "name", "").lower() == clean_id.lower()
        ):
            return item, None

    if clean_id.isdigit():
        idx = int(clean_id)
        items = list(catalog.values())
        if 0 <= idx < len(items):
            return items[idx], None

    return None, f"Сущность типа '{type_label}' с кодом/именем '{entity_id}' не найдена."


def find_recipe(recipe_id: str = ""):
    """Поиск рецепта (обратная совместимость)."""
    return find_entity("recipe", recipe_id)


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


def _make_report(entity_type: str = "recipe", entity_id: str = "", fmt: str = None) -> Response:
    """
    Единая логика построения отчета по указанной сущности и формату.
    """
    entity, err = find_entity(entity_type, entity_id)
    if err:
        status_code = 404 if "не найдена" in err or "пусто" in err else 400
        return Response(err, status=status_code, mimetype="text/plain; charset=utf-8")

    try:
        report = factory.create(fmt) if fmt is not None else factory.create_default()
    except argument_exception as ex:
        return Response(str(ex), status=400, mimetype="text/plain; charset=utf-8")

    result = report.build(entity)
    return format_response(report, result, getattr(entity, "name", "report"))


@app.route("/")
@app.route("/api/get_report", methods=["GET"])
def get_report():
    """Отчет по первому доступному рецепту в формате TXT (базовый эндпоинт)."""
    return _make_report("recipe", "", fmt="txt")


@app.route("/api/report", methods=["GET"])
@app.route("/api/report/<param1>/<param2>", methods=["GET"])
@app.route("/api/report/<entity_type>/<entity_id>/<report_format>", methods=["GET"])
def get_report_by_format(
    param1: str = None,
    param2: str = None,
    entity_type: str = None,
    entity_id: str = None,
    report_format: str = None,
):
    """
    GET метод формирования отчета в указанном формате (Markdown, XML, CSV, HTML, RTF, TXT)
    для указанного типа (Номенклатура, Единица измерения, Рецепт) и кода сущности.
    """
    q_type = request.args.get("entity_type") or request.args.get("type")
    q_id = (
        request.args.get("code")
        or request.args.get("id")
        or request.args.get("recipe_id")
    )
    q_format = request.args.get("format") or request.args.get("report_format")

    if entity_type is not None and entity_id is not None and report_format is not None:
        target_type = q_type or entity_type
        target_id = q_id or entity_id
        target_format = q_format or report_format
    elif param1 is not None and param2 is not None:
        p1_lower = param1.strip().lower()
        p2_lower = param2.strip().lower()
        if p1_lower in KNOWN_ENTITY_TYPES and p2_lower in KNOWN_FORMATS:
            target_type = q_type or param1
            target_id = q_id or ""
            target_format = q_format or param2
        elif p1_lower in KNOWN_ENTITY_TYPES:
            target_type = q_type or param1
            target_id = q_id or param2
            target_format = q_format or "txt"
        else:
            target_type = q_type or "recipe"
            target_id = q_id or param1
            target_format = q_format or param2
    else:
        target_type = q_type or "recipe"
        target_id = q_id or ""
        target_format = q_format or "txt"

    return _make_report(target_type, target_id, fmt=target_format)


@app.route("/api/report/default", methods=["GET"])
@app.route("/api/report/default/<param1>", methods=["GET"])
@app.route("/api/report/default/<entity_type>/<entity_id>", methods=["GET"])
def get_report_default(
    param1: str = None,
    entity_type: str = None,
    entity_id: str = None,
):
    """
    GET метод формирования данных для указанного типа (Номенклатура, Единица измерения, Рецепт)
    и кода сущности с использованием метода create_default (формат из настроек settings_manager).
    """
    q_type = request.args.get("entity_type") or request.args.get("type")
    q_id = (
        request.args.get("code")
        or request.args.get("id")
        or request.args.get("recipe_id")
    )

    if entity_type is not None and entity_id is not None:
        target_type = q_type or entity_type
        target_id = q_id or entity_id
    elif param1 is not None:
        if param1.strip().lower() in KNOWN_ENTITY_TYPES:
            target_type = q_type or param1
            target_id = q_id or ""
        else:
            target_type = q_type or "recipe"
            target_id = q_id or param1
    else:
        target_type = q_type or "recipe"
        target_id = q_id or ""

    return _make_report(target_type, target_id, fmt=None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
