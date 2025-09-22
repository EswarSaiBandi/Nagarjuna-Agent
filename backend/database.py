from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()


import dj_database_url
from dotenv import load_dotenv
load_dotenv()

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv("POSTGRES_URL")
    )
}

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("POSTGRES_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)




# Database URL
# DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/sales_agent_db")
DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql://hosteladmin:hostel123@localhost:5432/sales_agent_db")

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Database Models
class Salesperson(Base):
    __tablename__ = "salespersons"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    region = Column(String(50), nullable=False)
    gps_location = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    total_revenue = Column(Numeric(12, 2), default=0)
    monthly_target = Column(Numeric(12, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    meetings = relationship("Meeting", back_populates="salesperson")
    leads = relationship("Lead", back_populates="assigned_salesperson")
    login_sessions = relationship("SalespersonLoginSession", back_populates="salesperson")
    sales_records = relationship("SalesRecord", back_populates="salesperson")

class Dealer(Base):
    __tablename__ = "dealers"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    location = Column(String(100))
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    meetings = relationship("Meeting", back_populates="dealer")

class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    salesperson_id = Column(PostgresUUID(as_uuid=True), ForeignKey("salespersons.id"), nullable=False)
    dealer_id = Column(PostgresUUID(as_uuid=True), ForeignKey("dealers.id"), nullable=True)
    notes = Column(Text)
    outcome = Column(String(50))
    follow_up_date = Column(DateTime)
    location = Column(String(100))
    duration_minutes = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    salesperson = relationship("Salesperson", back_populates="meetings")
    dealer = relationship("Dealer", back_populates="meetings")

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    company = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    location = Column(String(100))
    source = Column(String(50))
    status = Column(String(20), default="new")
    score = Column(Integer, default=50)
    notes = Column(Text)
    assigned_to = Column(PostgresUUID(as_uuid=True), ForeignKey("salespersons.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assigned_salesperson = relationship("Salesperson", back_populates="leads")

class SalespersonLoginSession(Base):
    __tablename__ = "salesperson_login_sessions"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    salesperson_id = Column(PostgresUUID(as_uuid=True), ForeignKey("salespersons.id"), nullable=False)
    login_time = Column(DateTime, nullable=False)
    logout_time = Column(DateTime, nullable=True)
    session_duration_minutes = Column(Integer, nullable=True)
    location = Column(String(100), nullable=True)
    device_info = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    salesperson = relationship("Salesperson", back_populates="login_sessions")

class SalesRecord(Base):
    __tablename__ = "sales_records"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    salesperson_id = Column(PostgresUUID(as_uuid=True), ForeignKey("salespersons.id"), nullable=False)
    sale_amount = Column(Numeric(12, 2), nullable=False)
    product_name = Column(String(100), nullable=False)
    customer_name = Column(String(100), nullable=False)
    sale_date = Column(DateTime, nullable=False)
    commission_rate = Column(Numeric(5, 4), default=0.1)
    commission_amount = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    salesperson = relationship("Salesperson", back_populates="sales_records")

class ConversationHistory(Base):
    __tablename__ = "conversation_history"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(100), nullable=False)
    user_message = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    agent_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session  
def get_db():
    try:
        db = SessionLocal()
        yield db
        db.close()
    except Exception as e:
        yield None

# Simple database session function (non-generator)
def get_simple_db():
    try:
        return SessionLocal()
    except Exception as e:
        return None