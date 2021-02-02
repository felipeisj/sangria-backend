import decimal, datetime
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import literal
from sqlalchemy import cast, String, or_
from sqlalchemy.sql.functions import ReturnTypeFromArgs
import simplejson as json


class unaccent(ReturnTypeFromArgs):
	pass


def rut_dv(rut):
	"string -> string"
	return str((range(10) + ['K'])[
		sum(int(x) * y for x, y in
			zip(reversed(rut), (2 * range(9, 3, -1)))) % 11])


def format_int(n):
	"int or None -> string"
	return format(n, ",.0f").replace(",", ".") \
		if n is not None else u""


def format_rut(n):
	"int or None -> string"
	return u"" if n is None else u"{0}-{1}".format(format_int(n), rut_dv(str(n)))


def alchemyencoder(value):
	"""JSON encoder function for SQLAlchemy special classes."""
	new_value = value
	# if isinstance(value, decimal.Decimal):
	#     new_value = float(value)
	if isinstance(value, (datetime.datetime)):
		new_value = value.strftime("%Y-%m-%d %H:%M:%S")
	elif isinstance(value, (datetime.date)):
		new_value = value.strftime("%Y-%m-%d")
	elif isinstance(value, list):
		new_value = []
		for val in value:
			new_value.append(alchemyencoder(val))
	elif callable(value):
		new_value = value()

	return new_value


def row_to_dict(obj, cols):

	data = dict()
	for c in cols:
		data[c] = alchemyencoder(getattr(obj, c))
	return data

def queryLike(query, texto, campos):
	""" Agrega a la query un filtro para buscar todas las palabras en todos los campos

	Arguments:
		query {object} -- Objeto de tipo query sqlalchemy
		texto {string} -- Es el texto a buscar
		campos {array} -- Son los campos de las tablas a buscar

	Returns:
		[type] -- [description]
	"""
	from sqlalchemy.types import String, Text, Integer, Float, Boolean, DateTime, Date, TIMESTAMP

	palabras = texto.split(' ') # Transformamos el texto búsqueda a un array de palabras
	partes = []
	for campo in campos:
		for palabra in palabras:
			# if 'VARCHAR' in str(campo.type): # usar este en caso que se necesite buscar un campo de nombre especial
			# Comprueba si la columna del modelo es de tipo texto, cuando la columna es varchar indica que es string entra al if
			# Este proceso lo hacemos porque no podemos ponerele unaccent a otros campos que no sean de texto
			if isinstance(campo.type, String):
				partes.append(cast(unaccent(campo), String).ilike('%' + unaccent(palabra) + '%'))
			else:
				partes.append(cast(campo, String).ilike('%' + palabra + '%'))
	return query.filter(or_(*partes))
