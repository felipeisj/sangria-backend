from flask import Blueprint, jsonify, json, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.db.models import Categoria
from core.db.config import session as db_session
from core.utils import row_to_dict, queryLike


categorias = Blueprint('categorias', __name__)

@categorias.route('/api/categorias', methods=['GET'])



def categorias_etiquetas():

    query = db_session.query(Categoria)
    
    texto = request.args.get('texto')    
    if texto:
        campos = [Categoria.id, Categoria.descripcion, Categoria.ejemplo]
        query = queryLike(query, texto, campos)
    
    resultado = query.all()
    
    datos = list()
    for row in resultado:
        dato = row_to_dict(row, row.__table__.columns.keys())
        datos.append({
            'id': row.id,
            'descripcion': row.descripcion,
            'ejemplo': row.ejemplo
        })

    return jsonify(Categorias=datos), 200
