from flask import Blueprint, jsonify, json, request, send_from_directory, current_app
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    get_jwt_identity,
    get_jwt_claims,
    verify_jwt_in_request
)
from core.db.models import Etiqueta
from core.db.models import Usuario
from core.db.config import session as db_session
from core.db.models import ValorEtiqueta
from core.utils import row_to_dict, queryLike
from sqlalchemy import exc
import datetime
import os

etiquetas = Blueprint('etiquetas', __name__)


@etiquetas.route('/api/etiquetas', methods=['GET'])
def listado_etiquetas():

    query = db_session.query(Etiqueta)
    print(query)    
    categoria = request.args.get('categoria_id')
    url = request.url_root + "api/etiquetas/imagen/"
    print(url)
    if categoria:
        query = query.filter(Etiqueta.categoria_id==categoria)

    resultado = query.all()
    datos = list()
    for row in resultado:
        datos.append({
            'id': row.id,
            'nombre': row.nombre,
            'ejemplo': (url + str(row.ejemplo)) if row.ejemplo else ""
        })
    return jsonify(etiquetas=datos), 200

  
@etiquetas.route('/api/etiquetas/imagen/<string:nombre>', methods=['GET'])
def get_imagen(nombre):
    cwd = os.getcwd() + "/core/fotos_etiquetas/"
    print(cwd)
    print(nombre)
    return send_from_directory(cwd, nombre)     


@etiquetas.route('/api/valor-etiqueta', methods=['POST'])
def guardar_etiqueta():
    jsonData = request.json
    etiqueta = ValorEtiqueta()
    etiqueta.valor_categoria = jsonData["categoria_nombre"]
    etiqueta.valor_etiqueta = jsonData["valor_etiqueta"]
    etiqueta.celula_id = jsonData["celula_id"]
    etiqueta.etiqueta_id = jsonData["etiqueta_id"]
    etiqueta.fecha = datetime.datetime.now().strftime('%d/%m/%Y, %H:%M:%S')

    verify_jwt_in_request()
    usuario = db_session.query(Usuario).filter(Usuario.nombre==get_jwt_identity()).first()
    etiqueta.usuario_id = usuario.id
    db_session.add(etiqueta)
    db_session.commit()

    return jsonify(mensaje="info almacenada"), 200

@etiquetas.route('/api/etiquetas/eliminar/<int:etiqueta_id>', methods=['DELETE'])
def eliminar_etiqueta(etiqueta_id):
    if etiqueta_id == None:
        return jsonify(msg="Debe indicar un id de etiqueta"), 400

    etiqueta = db_session.query(Etiqueta).filter(Etiqueta.id==etiqueta_id).first()
    db_session.delete(etiqueta)
    db_session.commit()
    return jsonify(msg="Etiqueta eliminada correctamente"), 200



