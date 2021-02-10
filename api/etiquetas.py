from flask import Blueprint, jsonify, json, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.db.models import Etiqueta
from core.db.config import session as db_session
from core.utils import row_to_dict, queryLike
from sqlalchemy import exc


etiquetas = Blueprint('etiquetas', __name__)


@etiquetas.route('/api/etiquetas', methods=['GET'])
def listado_etiquetas():

    query = db_session.query(Etiqueta)    
    texto = request.args.get('texto')
    if texto:
        campos = [Etiqueta.nombre, Etiqueta.ruta_ejemplo, Etiqueta.descripcion]
        query = queryLike(query, texto, campos)
    
    resultado = query.all()
    
    datos = list()
    for row in resultado:
        datos.append({
            'nombre': row.nombre,
            'ruta_ejemplo': row.ruta_ejemplo,
            'descripcion': row.descripcion
        })

    return jsonify(etiquetas=datos), 200

@etiquetas.route('/api/etiquetas/guardar', methods=['POST'])
def guardar_etiqueta():
    jsonData = request.json

    etiqueta = ValorEtiqueta()
    etiqueta.fecha = jsonData["fecha"]
    etiqueta.valor = jsonData["valor"]
    etiqueta.validacion = jsonData["validacion"]

    return jsonify(msg="Etiqueta guardado correctamente"), 200

@etiquetas.route('/api/etiquetas/eliminar/<int:etiqueta_id>', methods=['DELETE'])
def eliminar_etiqueta(etiqueta_id):
    if etiqueta_id == None:
        return jsonify(msg="Debe indicar un id de etiqueta"), 400

    etiqueta = db_session.query(Etiqueta).filter(Etiqueta.id==etiqueta_id).first()
    db_session.delete(etiqueta)
    db_session.commit()
    return jsonify(msg="Etiqueta eliminada correctamente"), 200

# @valor_etiquetas.route('/api/valor_tiquetas', methods=['POST'])
# def etiquetas_post():
#     try:
#         etiqueta = ValorEtiqueta()
#         jsonData = request.json
#         etiqueta.celula_id
