from flask import Blueprint, jsonify, json, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.db.models import Categoria
from core.db.config import session as db_session
from core.utils import row_to_dict, queryLike


categorias = Blueprint('categorias', __name__)

@categorias.route('/api/categorias', methods=['GET'])
def categorias_etiquetas():

    query = db_session.query(Categoria)
    resultado = query.filter(Categoria.alteracion==False, Categoria.dependencia_id==None)
    
    datos = list()
    for row in resultado:
        dato = row_to_dict(row, row.__table__.columns.keys())
        datos.append({
            'id': row.id,
            'nombre': row.nombre,
            'alteracion': row.alteracion,
            'descripcion': row.descripcion,
            'dependencia_id' : row.dependencia_id,
            'ejemplo': row.ejemplo
        })

    return jsonify(categorias=datos), 200

@categorias.route('/api/categorias/alteraciones', methods=['GET'])
def mostrar_alteraciones():
    query = db_session.query(Categoria)
    alteracion = request.args.get('categoria_id')
    query = query.filter(Categoria.alteracion == True)    
    if alteracion:
        query = query.filter(Categoria.dependencia_id==alteracion)
    query = query.all()    
    datos = list()
    for row in query:
        dato = row_to_dict(row, row.__table__.columns.keys())
        datos.append({
            'id': row.id,
            'nombre': row.nombre
        })
    return jsonify(alteraciones = datos), 200
