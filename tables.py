from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Table, Text
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Metadatum(Base):
    __tablename__ = 'metadata'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    description = Column(Text)


# t_sqlite_sequence = Table(
#     'sqlite_sequence', metadata,
#     Column('name', NullType),
#     Column('seq', NullType)
# )


class Measurement(Base):
    __tablename__ = 'measurement'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    temperature = Column(Float)
    measurement_run = Column(ForeignKey('metadata.id'))

    metadatum = relationship('Metadatum')
