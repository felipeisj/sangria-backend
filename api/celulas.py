from flask import Blueprint, jsonify, json, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.db.models import Celula
from core.db.config import session as db_session
from core.utils import row_to_dict, queryLike


celulas = Blueprint('celulas', __name__)

@celulas.route('/api/celulas/<int:muestra_id>', methods=['GET'])



def muestra_celulas(muestra_id):

    query = db_session.query(Celula)
    
    texto = request.args.get('texto')    
    if texto:
        campos = [Celula.id, Celula.fecha, Celula.muestra_id, Celula.path]
        query = queryLike(query, texto, campos)
    
    resultado = query.all()
    
    datos = list()
    for row in resultado:
        dato = row_to_dict(row, row.__table__.columns.keys())
        datos.append({
            'id': row.id,
            'muestra_id': row.muestra_id,
            'path': row.path
        })

    return jsonify(Muestras=datos), 200


'''
@celulas.route('/api/celulas/adjudicados/', methods=['GET'])
def listado_adjudicados():
    datos = listado_celulas()
    return jsonify(celulas=datos), 200


@celulas.route('/api/celulas/seguidos/', methods=['GET'])
def listado_seguidos():
    datos = listado_celulas(seguidos=True)
    return jsonify(celulas=datos), 200
'''