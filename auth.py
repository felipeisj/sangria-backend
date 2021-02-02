from functools import wraps
import datetime
from core.db.models import Usuario
from core.db.config import session as db_session
from core.utils import row_to_dict
from flask import Blueprint, request, jsonify
from flask_cors import CORS, cross_origin
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    get_jwt_identity,
    get_jwt_claims,
    verify_jwt_in_request)
from main import jwt
#import simplejson as json
import json

auth = Blueprint('auth', __name__)


@jwt.user_identity_loader
def asignar_usuario(user):
    return user.nombre



@auth.route('/auth/login', methods=['POST'])
def login():

    #username = request.form.get("username")
    #password = request.form.get("password")
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    print(username)
    #return jsonify(access_token="access_token"), 200

    if username == "":
        return jsonify({"msg": "Debe indicar el usuario"}), 400
    if password == "":
        return jsonify({"msg": "Debe indicar el password"}), 400

    salted = Usuario.hash_password(password)
    usuario = db_session.query(Usuario).\
        filter(Usuario.nombre == username,
                Usuario.password == salted).first()
    print("Aqui va el usuario")
    print(usuario.nombre)
    if usuario:
        expires = datetime.timedelta(hours=16)
        print(expires)
        access_token = create_access_token(identity=usuario, expires_delta=expires)
        print(access_token)
        usuario_dict = row_to_dict(usuario, ["id", "nombre"])
        print(usuario_dict)
        return jsonify(access_token=access_token, usuario=usuario_dict), 200
    else:
        return jsonify(msg="Error en el usuario o la contraseña"), 401


@auth.route('/auth/usuario/', methods=['GET'])
def usuario():
    ret = {
        'usuario': get_jwt_identity(),  # test
    }
    return jsonify(ret), 200
