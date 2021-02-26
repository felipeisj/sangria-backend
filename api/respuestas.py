from flask import Blueprint, jsonify, json, request, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.db.models import Celula
from core.db.config import session as db_session
from core.utils import row_to_dict, queryLike
from sqlalchemy.sql.expression import func, select
import os

respuestas = Blueprint('respuestas', __name__)