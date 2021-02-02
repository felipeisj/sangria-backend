from flask import Blueprint, jsonify, json, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.db.models import Usuario
from core.db.config import session as db_session
from core.utils import row_to_dict, queryLike


usuarios = Blueprint('usuarios', __name__)


@usuarios.route('/api/usuarios/test', methods=['GET'])
def index_proyectos():
    usuario = db_session.query(Usuario) # Llama a todos los usuarios
    datos = list()
    for row in usuario:
        dato = row_to_dict(row, row.__table__.columns.keys())
        datos.append({
            **dato,
            'password': row.password,
            'nombre': row.nombre})

    return jsonify(usuarios=datos), 200