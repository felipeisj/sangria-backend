import uuid
import flask
from flask import (
    request,
    redirect,
    url_for,
    session as flask_session)
from core import settings, utils
from core.db.config import session
from core.db import models
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager

app = flask.Flask(__name__)
# Permitir solicitudes cross domain
cors = CORS(app, resources={r"/api/*": {"origins": "*"}, r"/auth/*": {"origins": "*"}})
# TOKE AUTH config
app.config['JWT_SECRET_KEY'] = 'sspuach.2021.21uu3390289#'  # Change this!
jwt = JWTManager(app)

app.secret_key = "5da9b204-7a13-4254-a4f4-565328f42aa1"
# Base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URI
app.config['BASEDIR'] = settings.BASE_DIR
app.config['JSON_AS_ASCII'] = False

from auth import auth
from api.etiquetas import etiquetas
from api.celulas import celulas
from api.muestras import muestras
from api.usuarios import usuarios
from api.categorias import categorias
from api.respuestas import respuestas

app.register_blueprint(auth)
app.register_blueprint(usuarios)
app.register_blueprint(muestras)
app.register_blueprint(celulas)
app.register_blueprint(etiquetas)
app.register_blueprint(categorias)
app.register_blueprint(respuestas)

@app.route("/")
@cross_origin()
def index():
    return "Prueba Modelos"