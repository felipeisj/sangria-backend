from sqlalchemy import (
    Column,
    Integer,
    ForeignKey as _ForeignKey,
    create_engine)
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker)
from sqlalchemy.ext.declarative import as_declarative, declared_attr

from core import settings


def tablename(variant):
    return "".join("_" + c.lower() if c.isupper() else c
                   for c in (variant if isinstance(variant, str) \
                             else variant.__name__)).strip("_")


def ForeignKey(variant, fk_kwargs=None, column_kwargs=None):
    fk_kwargs = fk_kwargs if fk_kwargs is not None else {}
    column_kwargs = column_kwargs if column_kwargs is not None else {}
    return Column(
        Integer,
        _ForeignKey(tablename(variant) + ".id", **fk_kwargs),
        **column_kwargs)


engine = create_engine(settings.DATABASE_URI,pool_size=200, max_overflow=0)
session = scoped_session(
    sessionmaker(autoflush=False, autocommit=False, bind=engine))


@as_declarative()
class Base(object):

    @declared_attr
    def __tablename__(cls):
        return tablename(cls)

    id = Column(Integer, primary_key=True)

    query = session.query_property()

    def format(self, attribute):
        value = getattr(self, attribute, None)
        if value is None: return u""
        return value
