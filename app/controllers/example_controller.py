from flask import Blueprint, jsonify, request
from ..services.example_service import ExampleService

example_bp = Blueprint('example', __name__)
example_service = ExampleService()

@example_bp.route('/', methods=['GET'])
def get_all():
    data = example_service.get_all()
    return jsonify({'success': True, 'data': data})

@example_bp.route('/<int:id>', methods=['GET'])
def get_one(id):
    data = example_service.get_by_id(id)
    if data:
        return jsonify({'success': True, 'data': data})
    return jsonify({'success': False, 'message': 'Not found'}), 404

@example_bp.route('/', methods=['POST'])
def create():
    data = request.get_json()
    result = example_service.create(data)
    return jsonify({'success': True, 'data': result}), 201

@example_bp.route('/<int:id>', methods=['PUT'])
def update(id):
    data = request.get_json()
    result = example_service.update(id, data)
    if result:
        return jsonify({'success': True, 'data': result})
    return jsonify({'success': False, 'message': 'Not found'}), 404

@example_bp.route('/<int:id>', methods=['DELETE'])
def delete(id):
    result = example_service.delete(id)
    if result:
        return jsonify({'success': True, 'message': 'Deleted successfully'})
    return jsonify({'success': False, 'message': 'Not found'}), 404