from flask import Blueprint, jsonify, json, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.db.models import ValorEtiqueta
from core.db.config import session as db_session
from core.utils import row_to_dict, queryLike
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    get_jwt_identity,
    get_jwt_claims,
    verify_jwt_in_request)

valor_etiquetas = Blueprint('valor_etiquetas', __name__)

@valor_etiquetas.route('/api/valor-tiquetas', methods=['GET'])
def etiquetas_get():

    query = db_session.query(ValorEtiqueta)
    
    texto = request.args.get('texto')    
    if texto:
        campos = [ValorEtiqueta.id, ValorEtiqueta.celula_id, ValorEtiqueta.usuario_id,
            ValorEtiqueta.fecha, ValorEtiqueta.valor, ValorEtiqueta.validacion]
        query = queryLike(query, texto, campos)
    
    resultado = query.all()
    
    datos = list()
    for row in resultado:
        dato = row_to_dict(row, row.__table__.columns.keys())
        datos.append({
            'id': row.id,
            'celula_id': row.celula_id,
            'usuario_id': row.usuario_id,
            'fecha': row.fecha,
            'valor': row.valor,
            'validacion': row.validacion
        })

    return jsonify(ValorEtiquetas=datos), 200


@jwt.user_identity_loader
def asignar_usuario(user):
    return user.nombre



@valor_etiquetas.route('/api/valor_tiquetas', methods=['POST'])
def etiquetas_post():
    try:
        etiqueta = ValorEtiqueta()
        jsonData = request.json
        etiqueta.celula_id

    #return jsonify(access_token="access_token"), 200

    

@auth.route('/auth/usuario/', methods=['GET'])
def usuario():
    ret = {
        'usuario': get_jwt_identity(),  # test
    }
    return jsonify(ret), 200
