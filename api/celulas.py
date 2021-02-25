from flask import Blueprint, jsonify, json, request, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.db.models import Celula
from core.db.config import session as db_session
from core.utils import row_to_dict, queryLike
from sqlalchemy.sql.expression import func, select
import os

celulas = Blueprint('celulas', __name__)

@celulas.route('/api/celulas', methods=['GET'])
def muestra_celulas():

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

@celulas.route('/api/celula', methods=['GET'])
def get_celula():
    query = db_session.query(Celula).order_by(func.random()).first()
    url = request.url_root + "api/celula/imagen/" + query.nombre
    data = row_to_dict(query,['id', 'nombre', 'path'])
    data["url_imagen"] = url
    return jsonify(celula=data), 200
  
@celulas.route('/api/celula/imagen/<string:nombre>', methods=['GET'])
def get_imagen(nombre):
    cwd = os.getcwd() + "/core/generated/50HD0037.JPG/"
    return send_from_directory(cwd, nombre)

# @celulas.route('/api/celula/imagen/ejemplo/<string:nombre>', methods=['GET'])
# def get_imagen(nombre):
#     cwd = os.getcwd() + "/core/fotos_etiquetadas/"
#     print(cwd)
#     return send_from_directory(cwd, nombre)