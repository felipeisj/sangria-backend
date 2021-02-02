from flask import Blueprint, jsonify, json, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.db.models import Etiqueta
from core.db.config import session as db_session
from core.utils import row_to_dict, queryLike
from sqlalchemy import exc


etiquetas = Blueprint('etiquetas', __name__)


@etiquetas.route('/api/etiquetas/<int:celula_id>', methods=['GET'])
def etiquetas_proyecto(celula_id):
    query = db_session.query(Etiqueta)
    

    texto = request.args.get('texto')    
    if texto:
        campos = [Etiqueta.id, Etiqueta.celula_id, Etiqueta.valor, Etiqueta.validacion]
        query = queryLike(query, texto, campos)
    
    resultado = query.all()
    
    datos = list()
    for row in resultado:
        datos.append({
            'id': row.id,
            'celula_id': row.celula_id,
            'valor': row.valor,
            'validacion': True
        })

    return jsonify(etiquetas=datos), 200
