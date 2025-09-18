import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Date, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DB_URL = os.getenv("SUPABASE_DB_URL")
if not DB_URL:
    raise RuntimeError("SUPABASE_DB_URL not set")

engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Lead(Base):
    __tablename__ = "leads"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String)
    dob = Column(Date, nullable=False)
    zip_code = Column(String, nullable=False)
    gender = Column(String)
    address = Column(Text, nullable=False)
    consent = Column(Boolean, nullable=False)
    status = Column(String, default="new")  # new | in_chat | agreed | archived
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("Session", back_populates="lead", cascade="all, delete")
    emails = relationship("Email", back_populates="lead", cascade="all, delete")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"))
    session_token = Column(String, unique=True, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    state = Column(JSONB)

    lead = relationship("Lead", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete")
    summaries = relationship("Summary", back_populates="session", cascade="all, delete")
    recommendations = relationship("Recommendation", back_populates="session", cascade="all, delete")

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"))
    role = Column(String)  # user | assistant | system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")

class Summary(Base):
    __tablename__ = "summaries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"))
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="summaries")

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"))
    plan_name = Column(String, nullable=False)
    reasoning = Column(Text)
    citations = Column(JSONB)
    agreed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="recommendations")

class Email(Base):
    __tablename__ = "emails"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"))
    template = Column(String)
    status = Column(String, default="pending")  # pending | sent | failed
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="emails")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
