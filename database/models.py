"""
Database models for Mawney Partners API
Supports both PostgreSQL (production) and SQLite (development)
"""
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings
import os

Base = declarative_base()

# Database setup
if settings.DATABASE_URL:
    # Use PostgreSQL (production)
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
elif settings.USE_SQLITE:
    # Use SQLite (development)
    db_path = settings.SQLITE_PATH
    engine = create_engine(f'sqlite:///{db_path}', connect_args={'check_same_thread': False})
else:
    # Fallback to in-memory SQLite (not recommended for production)
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    """User model"""
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)  # bcrypt hash
    roles = Column(JSON, default=['user'])  # ['user', 'admin', 'read-only']
    mfa_secret = Column(String, nullable=True)  # TOTP secret
    mfa_enabled = Column(Boolean, default=False)
    backup_codes = Column(JSON, nullable=True)  # List of backup codes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)  # Soft delete for GDPR

class Compensation(Base):
    """Compensation data model (encrypted fields)"""
    __tablename__ = 'compensations'
    
    id = Column(String, primary_key=True)
    user_email = Column(String, nullable=False, index=True)
    # Encrypted fields (will be encrypted before storage)
    base_salary = Column(Text, nullable=True)  # Encrypted
    base_salary_currency = Column(Text, nullable=True)  # Encrypted
    bonus = Column(Text, nullable=True)  # Encrypted
    bonus_currency = Column(Text, nullable=True)  # Encrypted
    equity = Column(Text, nullable=True)  # Encrypted
    # Non-sensitive fields
    country = Column(String, nullable=True)
    role = Column(String, nullable=True)
    company = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

class CallNote(Base):
    """Call note model (encrypted transcript/summary)"""
    __tablename__ = 'call_notes'
    
    id = Column(String, primary_key=True)
    user_email = Column(String, nullable=False, index=True)
    # Encrypted fields
    transcript = Column(Text, nullable=True)  # Encrypted
    summary = Column(Text, nullable=True)  # Encrypted
    notes = Column(Text, nullable=True)  # Encrypted
    # Non-sensitive fields
    title = Column(String, nullable=True)
    date = Column(DateTime, nullable=True)
    participants = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

class AuditLog(Base):
    """Audit log model (immutable)"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    email = Column(String, nullable=True, index=True)
    endpoint = Column(String, nullable=True)
    method = Column(String, nullable=True)
    status = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)

class RefreshToken(Base):
    """Refresh token storage (for rotation)"""
    __tablename__ = 'refresh_tokens'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    token_hash = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_revoked = Column(Boolean, default=False)

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"⚠️ Database initialization note: {e}")
        # Tables might already exist, which is fine

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
