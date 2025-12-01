"""
Database setup using SQLAlchemy for persistent storage
"""
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class QuestionClusterDB(Base):
    """Question cluster table"""
    __tablename__ = 'question_clusters'
    
    cluster_id = Column(String, primary_key=True)
    representative_question = Column(Text, nullable=False)
    similar_questions = Column(Text, nullable=False)  # JSON array
    count = Column(Integer, nullable=False)
    artifact = Column(String, nullable=True)
    section = Column(String, nullable=True)
    canonical_answer_id = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, nullable=False)

class CanonicalAnswerDB(Base):
    """Canonical answer table"""
    __tablename__ = 'canonical_answers'
    
    answer_id = Column(String, primary_key=True)
    cluster_id = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    answer_markdown = Column(Text, nullable=False)
    citations = Column(Text, nullable=False)  # JSON array
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    is_published = Column(Boolean, default=False)

class QuestionLogDB(Base):
    """Question log table"""
    __tablename__ = 'question_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    artifact = Column(String, nullable=True)
    section = Column(String, nullable=True)
    confidence = Column(Float, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_url='sqlite:///openta.db'):
        """Initialize database"""
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def reset_demo_data(self):
        """Clear all data for fresh demo"""
        session = self.get_session()
        try:
            session.query(QuestionClusterDB).delete()
            session.query(CanonicalAnswerDB).delete()
            session.query(QuestionLogDB).delete()
            session.commit()
            print("🗑️  Database cleared for fresh demo data")
        finally:
            session.close()

# Global database instance
db_manager = DatabaseManager()
