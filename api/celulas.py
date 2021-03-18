from flask import Blueprint, jsonify, json, request, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from core.db.models import Celula, Usuario, ValorEtiqueta, Respuesta
from core.db.config import session as db_session
from core.utils import row_to_dict, queryLike
from sqlalchemy.sql.expression import func, select
import os

celulas = Blueprint('celulas', __name__)

@celulas.route('/api/celulas', methods=['GET'])
@jwt_required
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
@jwt_required
def get_celula():
    #1 obtener token usuario
    #2 Con token obtener usuario bd
    #3 Consultar si es profesor
    #4 Si es profesor, mostrar imagen que haya sido respondida, si no, random.
    usuario_id = get_jwt_claims()
    #consulta si es académico
    academico = query = db_session.query(Usuario).filter(Usuario.id == usuario_id, Usuario.academico == True).first()
    if academico:
        #Consulta a la bd por una célula que haya sido clasificada por estudiantes
        academico_celula_id = db_session.execute("""
            SELECT * FROM (
                select * from 
	                (select distinct celula_id from valor_etiqueta, respuesta where respuesta.id = valor_etiqueta.respuesta_id AND respuesta.usuario_id <> 1 ) as c1
                    where c1.celula_id NOT IN (select celula_id from valor_etiqueta, respuesta where respuesta.id = valor_etiqueta.respuesta_id AND respuesta.usuario_id = 1)
                ) as c2
                ORDER BY RANDOM()
                LIMIT 1
                """.format(usuario_id)).fetchone()
        if academico_celula_id is not None:
            query = db_session.query(Celula).filter(Celula.id == academico_celula_id["celula_id"]).first()
        else:
            return jsonify(msg="No hay fotos para etiquetar"), 200
    else:# Si no es académico
        #Consulta que busca una célula que no haya sido respondida por el estudiante
        estudiante_celula_id = db_session.execute("""
            SELECT * FROM (
                select * from 
	                (select distinct celula.id from celula where celula.id NOT IN (select celula_id from valor_etiqueta, respuesta where valor_etiqueta.respuesta_id = respuesta.id AND respuesta.usuario_id = {0})) as c1
                ) as c2
                ORDER BY RANDOM()
                LIMIT 1
                """.format(usuario_id)).fetchone()
        if estudiante_celula_id is not None:
            query = db_session.query(Celula).filter(Celula.id == estudiante_celula_id["id"]).first()
        else:
            return jsonify(celula={},msg="No hay fotos para etiquetar"), 200
    url = request.url_root + "api/celula/imagen/"+query.path+query.nombre
    data = row_to_dict(query,['id', 'nombre', 'path'])
    data["url_imagen"] = url
    return jsonify(celula=data), 200
  
@celulas.route('/api/celula/imagen/<string:carpeta>/<string:nombre>', methods=['GET'])
def get_imagen(carpeta, nombre):
    cwd = os.getcwd() + "/core/generated/"+carpeta
    return send_from_directory(cwd, nombre)    