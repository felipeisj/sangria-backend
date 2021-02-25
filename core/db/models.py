import hashlib
from sqlalchemy import (
    Date,
    DateTime,
    Column,
    Boolean,
    Integer,
    BigInteger,
    String,
    DateTime,
    Numeric,
    Text,
    UnicodeText,
    JSON)
from sqlalchemy.orm import (
    relationship,
    backref,
    validates)
from core import settings
from core.db.config import Base, ForeignKey, session


class Usuario(Base):
    # SALT estático para todos los usuarios
    STATIC_SALT = u"".join(chr(c) for c in [
        33, 37, 121, 113, 108, 117, 118, 33, 101, 56, 94, 43,
        49, 103, 113, 56, 120, 41, 54, 36, 41, 56, 95, 41, 95])
    password = Column(String(500), nullable=False)
    nombre = Column(String(200))
    habilitado = Column(Boolean(), nullable=False, default=True)
    @staticmethod
    def hash_password(password):
        return hashlib.sha512(
            (Usuario.STATIC_SALT + password).encode('utf-8')).hexdigest()

class Muestra(Base):
    fecha = Column(DateTime())
    path = Column(UnicodeText())
    usuario_id = ForeignKey(Usuario)
    usuario = relationship('Usuario', backref=backref('muestras'))

class Celula(Base):
    muestra_id = ForeignKey(Muestra)
    nombre = Column(String(200))
    muestra = relationship('Muestra', backref=backref('celulas'))
    path = Column(String(200))

class Categoria(Base):
    nombre = Column(String(200))
    dependencia_id = Column(Integer)
    alteracion = Column(Boolean, default = False)
    descripcion = Column(String(200))
    ejemplo = Column(String(200))

class Etiqueta(Base):
    categoria_id = ForeignKey(Categoria)
    nombre = Column(String(200))
    ejemplo = Column(String(200))
    descripcion = Column(String(400))

class ValorEtiqueta(Base):
    celula_id = ForeignKey(Celula)
    celula = relationship('Celula', backref=backref('valor_etiquetas'))
    etiqueta_id = ForeignKey(Etiqueta)
    etiqueta = relationship('Etiqueta', backref=backref('valor_etiquetas'))
    valor = Column(String(200))
    validacion = Column(Boolean, default=False)

class Respuesta(Base):
     usuario_id = ForeignKey(Usuario)
     fecha = Column(DateTime())





