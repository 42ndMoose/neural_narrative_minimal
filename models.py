
from sqlalchemy import (
    create_engine, Column, String, Float, Integer, Text, ForeignKey, Enum
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.types import JSON as SAJSON

Base = declarative_base()

class Statement(Base):
    __tablename__ = "statements"
    id = Column(String, primary_key=True)  # ULID or any stable string id
    slug = Column(String, unique=True, nullable=True)
    text = Column(Text, nullable=False)
    type = Column(String, default="claim")  # claim/event/policy/definition/explanation/equation_step/takeaway/counterpoint
    scope = Column(String, nullable=True)
    time_as_of = Column(String, nullable=True)  # ISO date str
    time_from = Column(String, nullable=True)
    time_to = Column(String, nullable=True)
    actors_json = Column(Text, nullable=True)  # JSON-encoded list of actors
    status = Column(String, default="live")
    confidence = Column(Float, default=1.0)
    version = Column(Integer, default=1)
    prev_version_id = Column(String, nullable=True)
    tags_json = Column(Text, nullable=True)    # JSON-encoded list of tags

    outgoing = relationship("Edge", foreign_keys="Edge.from_id", back_populates="from_stmt", cascade="all, delete-orphan")
    incoming = relationship("Edge", foreign_keys="Edge.to_id", back_populates="to_stmt", cascade="all, delete-orphan")

class Edge(Base):
    __tablename__ = "edges"
    id = Column(String, primary_key=True)
    from_id = Column(String, ForeignKey("statements.id"), nullable=False)
    to_id = Column(String, ForeignKey("statements.id"), nullable=False)
    relation = Column(String, nullable=False)  # supports/contradicts/depends_on/derived_from/refines/same_as/illustrates/summarizes
    note = Column(Text, nullable=True)

    from_stmt = relationship("Statement", foreign_keys=[from_id], back_populates="outgoing")
    to_stmt = relationship("Statement", foreign_keys=[to_id], back_populates="incoming")

class Container(Base):
    __tablename__ = "containers"
    id = Column(String, primary_key=True)
    slug = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    intro = Column(Text, nullable=True)
    root_ids_json = Column(Text, nullable=True)      # JSON array of statement ids
    default_path_json = Column(Text, nullable=True)  # JSON array of statement ids

class ContainerStatement(Base):
    __tablename__ = "container_statements"
    id = Column(String, primary_key=True)
    container_id = Column(String, ForeignKey("containers.id"), nullable=False)
    statement_id = Column(String, ForeignKey("statements.id"), nullable=False)

    container = relationship("Container")
    statement = relationship("Statement")


def make_engine(db_url="sqlite:///kg.db"):
    return create_engine(db_url, future=True, echo=False)

def make_session(db_url="sqlite:///kg.db"):
    engine = make_engine(db_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()
