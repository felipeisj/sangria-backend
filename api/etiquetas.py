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
from core.db.models import ValorEtiqueta, Respuesta
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
    # almacena respuesta
    respuesta = Respuesta()
    respuesta.fecha = datetime.datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
    verify_jwt_in_request()
    usuario = db_session.query(Usuario).filter(Usuario.nombre==get_jwt_identity()).first()
    respuesta.usuario_id = usuario.id
    db_session.add(respuesta)
    db_session.flush()
    print(respuesta.id)

    # almacenando registro de etiqueta
    jsonData = request.json
    print(jsonData)
    etiqueta = ValorEtiqueta()
    etiqueta.valor = jsonData["valor_etiqueta"]
    etiqueta.celula_id = jsonData["celula_id"]
    etiqueta.etiqueta_id = jsonData["etiqueta_id"]
    etiqueta.respuesta_id = respuesta.id
    db_session.add(etiqueta)
    db_session.flush()

    # almacenando registro de alteracion
    if(jsonData["alteracion_id"] != "" and jsonData["alteracion_id"] is not None):
        print("------- entramos -----")
        alteracion = ValorEtiqueta()
        # alteracion.valor = jsonData["valor_alteracion"]
        alteracion.celula_id = jsonData["celula_id"]
        alteracion.valor = jsonData["valor_alteracion"]
        alteracion.etiqueta_id = jsonData["alteracion_id"]
        alteracion.respuesta_id = respuesta.id
        respuesta.fecha = datetime.datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
        respuesta.usuario_id = usuario.id
        db_session.add(alteracion, respuesta)
        db_session.flush()
    
    respuesta.fecha = datetime.datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
    respuesta.usuario_id = usuario.id
    db_session.add( respuesta)
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