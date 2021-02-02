from flask import Blueprint, jsonify, json, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.db.models import Muestra
from core.db.config import session as db_session
from core.utils import row_to_dict, queryLike


muestras = Blueprint('muestras', __name__)


@muestras.route('/api/muestras/<int:usuario_id>', methods=['GET'])
def muestras_proyecto(usuario_id):
    query = db_session.query(Muestra).outerjoin(Muestra.usuario).\
        filter(Muestra.usuario_id == usuario_id).order_by(Muestra.id.asc())
    

    texto = request.args.get('texto')    
    if texto:
        campos = [Muestra.fecha, Muestra.path, Muestra.usuario_id]
        query = queryLike(query, texto, campos)
    
    resultado = query.all()
    
    datos = list()
    for row in resultado:
        datos.append({
            'Muestra.id': row.id,
            'fecha': row.fecha,
            'path': row.path,
            'usuario_id': row.usuario_id
        })

    return jsonify(Muestras=datos), 200
