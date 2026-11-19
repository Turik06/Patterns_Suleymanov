from flask import jsonify, request
import connexion

from Src.Dtos.report_type_enum import report_type_enum
from Src.Dtos.filter_dto import filter_dto
from Src.Logics.report_factory import report_factory
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.convertor import convertor
from Src.Logics.entity_service import entity_service
from Src.Logics.prototype import prototype

api = connexion.FlaskApp(__name__, specification_dir="./")
app = api.app
app.json.ensure_ascii = False

# Инициализация синглтонов хранилища и настроек
settings = settings_manager()
try:
    settings.load()
except Exception:
    pass

storage = storage_manager()
storage.first_start()
service = entity_service(storage)
factory = report_factory(settings=settings.settings)

# Конвертор
worker = convertor()


"""
Получить отчет в формате по умолчанию
"""
@api.route("/api/get_default_report", methods=["GET"])
def get_default_report():
    try:
        key = request.args.get('entity') 
        unique_code = request.args.get('unique_code')

        items = storage.data[ key ]
        item = next((obj for obj in items if hasattr(obj, 'unique_code') and obj.unique_code == unique_code), None)

        report_type = factory.create_default()
        report_instance = report_type() if isinstance(report_type, type) else report_type
        result = report_instance.build( item )
        
        output = result.text if result.text else (bytes(result.binary).decode("utf-8") if result.binary else "")
        return output, 200, {'Content-Type': getattr(result, 'format', 'text/plain')}
    except Exception as ex:
        return f"Ошибка: {ex}!", 500


"""
Получить список доменных сущностей
"""
@api.route("/api/get_entities", methods=["GET"])
def get_entities():
    source = storage.domains()
    result = worker.serialize( source )
    return result, 200, {'Content-Type': 'text/json'}


@app.route("/api/reports/formats", methods=["GET"])
def get_report_formats():
    """Список поддерживаемых форматов отчетов"""
    formats = [item.name for item in report_type_enum]
    return jsonify(formats), 200


@app.route("/api/entity/<entity_type>/<unique_code>", methods=["GET"])
def get_domain_entity(entity_type: str, unique_code: str):
    """Получить сущность по коду"""
    try:
        entity = service.get_entity(entity_type, unique_code)
        serialized = worker.serialize(entity)
        data = serialized.get("result", serialized) if isinstance(serialized, dict) else serialized
        return jsonify(data), 200
    except ValueError as ex:
        return jsonify({"error": str(ex)}), 400
    except LookupError as ex:
        return jsonify({"error": str(ex)}), 404


@app.route("/api/entity/<entity_type>", methods=["PUT", "POST"])
def create_domain_entity(entity_type: str):
    """Создать сущность"""
    payload = request.get_json(silent=True)
    if not payload or not isinstance(payload, dict):
        return jsonify({"error": "Ожидается JSON"}), 400

    try:
        model = service.create_entity(entity_type, payload, worker=worker)
        serialized = worker.serialize(model)
        data = serialized.get("result", serialized) if isinstance(serialized, dict) else serialized
        return jsonify(data), 201
    except ValueError as ex:
        return jsonify({"error": str(ex)}), 400


@app.route("/api/entity/<entity_type>/<unique_code>", methods=["PATCH", "POST"])
def update_domain_entity(entity_type: str, unique_code: str):
    """Обновить сущность"""
    payload = request.get_json(silent=True)
    if not payload or not isinstance(payload, dict):
        return jsonify({"error": "Ожидается JSON"}), 400

    try:
        entity = service.update_entity(entity_type, unique_code, payload)
        serialized = worker.serialize(entity)
        data = serialized.get("result", serialized) if isinstance(serialized, dict) else serialized
        return jsonify(data), 200
    except LookupError as ex:
        return jsonify({"error": str(ex)}), 404
    except PermissionError as ex:
        ref_names = ex.args[1] if len(ex.args) > 1 else []
        return jsonify({"error": str(ex.args[0]), "referrers": ref_names}), 409
    except ValueError as ex:
        return jsonify({"error": str(ex)}), 400


@app.route("/api/entity/<entity_type>/<unique_code>", methods=["DELETE"])
def delete_domain_entity(entity_type: str, unique_code: str):
    """Удалить сущность"""
    try:
        service.delete_entity(entity_type, unique_code)
        return jsonify({"result": "success", "deleted": unique_code}), 200
    except ValueError as ex:
        return jsonify({"error": str(ex)}), 400
    except LookupError as ex:
        return jsonify({"error": str(ex)}), 404
    except PermissionError as ex:
        ref_names = ex.args[1] if len(ex.args) > 1 else []
        return jsonify({"error": str(ex.args[0]), "referrers": ref_names}), 409


create_domain_entity_post = create_domain_entity
update_domain_entity_post = update_domain_entity


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


@app.route("/api/filter/<domain_type>", methods=["POST"])
def filter_domain_entities(domain_type: str):
    category = storage.resolve_category(domain_type)
    if not category or category not in storage.data:
        return jsonify({"error": f"Неизвестный тип сущности '{domain_type}'"}), 400

    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({"error": "Ожидается JSON объект параметров фильтрации"}), 400

    f_dto = filter_dto.from_dict(payload)
    items = storage.data[category]
    filtered_pr = prototype(items).clone(f_dto)

    serialized = worker.serialize(filtered_pr.data)
    data = serialized.get("result", serialized) if isinstance(serialized, dict) else serialized
    return jsonify(data), 200


@app.route("/api/osv", methods=["POST"])
@app.route("/api/turnarounds", methods=["POST"])
def get_osv_report():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        payload = {}

    f_dto = filter_dto.from_dict(payload)
    transactions = storage.data.get(storage.transaction_key(), [])
    filtered_pr = prototype(transactions).clone(f_dto)
    osv_pr = filtered_pr.create_osv()

    rows = [row.to_dict() for row in osv_pr.data]
    return jsonify(rows), 200


api.add_api('openapi.yaml')

if __name__ == "__main__":
    api.run(host="0.0.0.0", port=8080)

