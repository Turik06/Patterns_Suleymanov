import sys
from pathlib import Path
from flask import Flask, jsonify, request

repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager

app = Flask(__name__)
app.json.ensure_ascii = False

# Инициализация синглтонов хранилища и настроек
settings = settings_manager()
try:
    settings.load()
except Exception:
    pass

storage = storage_manager()
storage.first_start()
factory = report_factory(settings=settings.settings)


@app.route("/", methods=["GET"])
@app.route("/api/get_report", methods=["GET"])
def get_report():
    """
    Базовый проверочный эндпоинт.
    """
    return "success"


@app.route("/api/report", methods=["GET"])
@app.route("/api/report/<param1>", methods=["GET"])
@app.route("/api/report/<param1>/<param2>", methods=["GET"])
@app.route("/api/report/<param1>/<param2>/<param3>", methods=["GET"])
def get_entity_report(param1: str = None, param2: str = None, param3: str = None):
    """
    Формирование отчета по указанному формату, типу сущности и ее идентификатору.
    """
    q_type = request.args.get("type") or request.args.get("entity_type")
    q_id = request.args.get("code") or request.args.get("id") or request.args.get("recipe_id")
    q_format = request.args.get("format")

    if param1 and param2 and param3:
        target_type = q_type or param1
        target_id = q_id or param2
        target_format = q_format or param3
    elif param1 and param2:
        is_p1_type = bool(storage.resolve_category(param1))
        if is_p1_type:
            target_type = q_type or param1
            target_id = q_id or param2
            target_format = q_format or ""
        else:
            target_type = q_type or "recipe"
            target_id = q_id or param1
            target_format = q_format or param2
    elif param1:
        is_p1_type = bool(storage.resolve_category(param1))
        if is_p1_type:
            target_type = q_type or param1
            target_id = q_id or ""
            target_format = q_format or ""
        else:
            target_type = q_type or "recipe"
            target_id = q_id or param1
            target_format = q_format or ""
    else:
        target_type = q_type or "recipe"
        target_id = q_id or ""
        target_format = q_format or ""

    category = storage.resolve_category(target_type)
    if not category or category not in storage.data:
        return jsonify({"error": f"Неизвестный тип сущности '{target_type}'"}), 400

    entity = storage.get_by_type_and_id(target_type, target_id)
    if not entity:
        return jsonify({"error": f"Сущность типа '{target_type}' с идентификатором '{target_id}' не найдена"}), 404

    try:
        format_enum = (
            report_type_enum.from_string(target_format)
            if target_format
            else settings.settings.response_format
        )
    except Exception as ex:
        return jsonify({"error": f"Некорректный формат отчета: {ex}"}), 400

    report = factory.create(format_enum, target_type)
    result_dto = report.build(entity)
    return report.create_response(result_dto, f"{target_type}_{target_id}")


@app.route("/api/report/default", methods=["GET"])
@app.route("/api/report/default/<param1>", methods=["GET"])
@app.route("/api/report/default/<param1>/<param2>", methods=["GET"])
def get_default_entity_report(param1: str = None, param2: str = None):
    """
    Формирование отчета с использованием формата по умолчанию (create_default).
    """
    q_type = request.args.get("type") or request.args.get("entity_type")
    q_id = request.args.get("code") or request.args.get("id") or request.args.get("recipe_id")

    if param1 and param2:
        target_type = q_type or param1
        target_id = q_id or param2
    elif param1:
        is_p1_type = bool(storage.resolve_category(param1))
        if is_p1_type:
            target_type = q_type or param1
            target_id = q_id or ""
        else:
            target_type = q_type or "recipe"
            target_id = q_id or param1
    else:
        target_type = q_type or "recipe"
        target_id = q_id or ""

    category = storage.resolve_category(target_type)
    if not category or category not in storage.data:
        return jsonify({"error": f"Неизвестный тип сущности '{target_type}'"}), 400

    entity = storage.get_by_type_and_id(target_type, target_id)
    if not entity:
        return jsonify({"error": f"Сущность типа '{target_type}' с идентификатором '{target_id}' не найдена"}), 404

    report = factory.create_default(target_type)
    result_dto = report.build(entity)
    return report.create_response(result_dto, f"{target_type}_{target_id}_default")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
