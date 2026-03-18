import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


def _normalize_database_url() -> str:
    url = os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = _normalize_database_url()

engine_kwargs = {}
if not DATABASE_URL.startswith("sqlite"):
    if "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
        engine_kwargs["connect_args"] = {"sslmode": "require"}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PlanArtifact(Base):
    __tablename__ = "bwa_plan_artifacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    source_text = Column(Text, nullable=False)
    active_scenario = Column(String(30), nullable=False, default="baseline")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    snapshots = relationship("PlanSnapshot", back_populates="artifact", cascade="all, delete-orphan")


class PlanSnapshot(Base):
    __tablename__ = "bwa_plan_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    artifact_id = Column(Integer, ForeignKey("bwa_plan_artifacts.id"), nullable=False, index=True)
    scenario = Column(String(30), nullable=False)
    summary = Column(Text, nullable=False, default="")
    items_json = Column(Text, nullable=False, default="[]")
    score = Column(Integer, nullable=False, default=60)
    assumptions_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    artifact = relationship("PlanArtifact", back_populates="snapshots")

    def items(self):
        try:
            return json.loads(self.items_json)
        except Exception:
            return []

    def assumptions(self):
        try:
            return json.loads(self.assumptions_json)
        except Exception:
            return []
