from flask import Blueprint, jsonify, json, request, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from sqlalchemy.ext.declarative.api import as_declarative
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
        datos.append({
            'id': row.id,
            'muestra_id': row.muestra_id,
            'path': row.path 
        })

    return jsonify(Muestras=datos), 200

@celulas.route('/api/celula', methods=['GET'])
@jwt_required
def get_celula():
    usuario_id = get_jwt_claims()
    celula_id_dataset = request.args.get('celula_id')
    if(celula_id_dataset):
        query = db_session.query(Celula).filter(Celula.id == celula_id_dataset).first()
    else:
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

@celulas.route('/api/celulas-etiquetadas', methods=['GET'])
@jwt_required
def get_celulas_etiquetadas():
    usuario_id = get_jwt_claims()
    estado_mostrar = request.args.get('estado_etiquetar')
    print(estado_mostrar)
    #Consulta a la bd por una célula que haya sido clasificada por estudiantes
    celula_id_sin_validar = db_session.execute("""
        select c5.celula_id, c5.valor, c5.count, c5.nombre, c5.id, c5.path, validacion from(
	select celula_id, valor, count, c4.nombre, etiqueta.id, path from (
	select celula_id, valor, count, nombre, path from (select valor_etiqueta.celula_id, valor, count(valor) from (
            select * from
                (select distinct celula_id, validacion from valor_etiqueta, respuesta where respuesta.id = valor_etiqueta.respuesta_id  and respuesta.usuario_id <> 1 ) as c1
            )  as c2, valor_etiqueta where valor_etiqueta.celula_id = c2.celula_id group by valor_etiqueta.celula_id, valor) as c3, celula
			where c3.celula_id = celula.id) as c4, etiqueta where c4.valor = etiqueta.nombre) as c5 JOIN valor_etiqueta
			ON c5.celula_id = valor_etiqueta.celula_id and c5.id = valor_etiqueta.etiqueta_id where validacion=false
            """.format(usuario_id))
    
    contador_celula_id = db_session.execute("""
        select c5.celula_id, c5.valor, c5.count, c5.nombre, c5.id, c5.path, validacion from(
	select celula_id, valor, count, c4.nombre, etiqueta.id, path from (
	select celula_id, valor, count, nombre, path from (select valor_etiqueta.celula_id, valor, count(valor) from (
            select * from
                (select distinct celula_id, validacion from valor_etiqueta, respuesta where respuesta.id = valor_etiqueta.respuesta_id  and respuesta.usuario_id <> 1 ) as c1
            )  as c2, valor_etiqueta where valor_etiqueta.celula_id = c2.celula_id group by valor_etiqueta.celula_id, valor) as c3, celula
			where c3.celula_id = celula.id) as c4, etiqueta where c4.valor = etiqueta.nombre) as c5 JOIN valor_etiqueta
			ON c5.celula_id = valor_etiqueta.celula_id and c5.id = valor_etiqueta.etiqueta_id
            """)
    if (estado_mostrar):
        resultado = celula_id_sin_validar.fetchall()
    else:
        resultado = contador_celula_id.fetchall()
    datos = list()
    
    for row in resultado:
        url = request.url_root + "api/celula/imagen/"+row.path+row.nombre
        existe = False
        for dato in datos:
            if(row.celula_id == dato["id"] and row.valor != dato["valor"]):
                x = dato["otros_valores"]
                x.append({
                    'id': row.celula_id,
                    'valor': row.valor,
                    'contador': row.count,
                    'nombre': row.nombre,
                    'etiqueta_id': row.id,
                    'path': row.path,
                    'validacion': row.validacion,
                    'url_imagen': url
                    })
                dato["otros_valores"] = x
            if row.celula_id == dato["id"]:
                existe = True
        if(existe == False):
            datos.append({
                'id': row.celula_id,
                'valor': row.valor,
                'contador': row.count,
                'nombre': row.nombre,
                'etiqueta_id': row.id,
                'path': row.path,
                'validacion': row.validacion,
                'url_imagen': url,
                'otros_valores': list()
                })
        
    return jsonify(celulas=datos), 200
  
@celulas.route('/api/celula/imagen/<string:carpeta>/<string:nombre>', methods=['GET'])
def get_imagen(carpeta, nombre):
    cwd = os.getcwd() + "/core/generated/"+carpeta
    return send_from_directory(cwd, nombre)    