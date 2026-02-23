from flask import Blueprint
from models.service import Service
from models.state import State

public_bp = Blueprint('public', __name__)

@public_bp.route('/services', methods=['GET'])
def get_services():
    services = Service.query.filter_by(is_active=True).all()
    return {"services": [s.to_dict() for s in services]}

@public_bp.route('/states', methods=['GET'])
def get_states():
    states = State.query.all()
    return {"states": [{"id": s.id, "name": s.name} for s in states]}
