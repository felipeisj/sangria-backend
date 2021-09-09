from flask import Blueprint, jsonify, json, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.db.models import Usuario
from core.db.config import session as db_session
from core.utils import row_to_dict, queryLike


usuarios = Blueprint('usuarios', __name__)

@usuarios.route('/api/usuarios/no-admin', methods=['GET'])
def usuarios_todos():
    usuario = db_session.query(Usuario) # Llama a todos los usuarios
    datos = list()
    for row in usuario:
        if row.academico == False:
            datos.append({
                'nombre': row.nombre,
                'habilitado': row.academico
                })
    return jsonify(usuarios=datos), 200

@usuarios.route('/api/usuarios/<int:usuario_id>', methods=['GET'])
def usuario_individual(usuario_id):
    query = db_session.query(Usuario)
    usuario = query.filter(Usuario.id==usuario_id).first() # Buscar el usuario por id
    datos_usuario = row_to_dict(usuario,['id', 'nombre', 'academico'])
    
    return jsonify(usuario=datos_usuario), 200