import datetime
import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Text, Date, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from backend.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profile = relationship("LearnerProfile", back_populates="user", uselist=False)
    paths = relationship("LearningPath", back_populates="user")

class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    goal = Column(Text, nullable=True)
    target_role = Column(Text, nullable=True)
    timeframe_weeks = Column(Integer, nullable=True)
    hours_per_week = Column(Integer, nullable=True)
    digital_twin = Column(JSON, nullable=True)
    questions_asked_session = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="profile")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(100), primary_key=True)
    domain = Column(Text, nullable=True)
    name = Column(Text, nullable=False)

class SkillPrerequisite(Base):
    __tablename__ = "skill_prerequisites"

    skill_id = Column(String(100), ForeignKey("skills.id"), primary_key=True)
    prerequisite_id = Column(String(100), ForeignKey("skills.id"), primary_key=True)

class Resource(Base):
    __tablename__ = "resources"

    id = Column(String(100), primary_key=True)
    domain = Column(Text, nullable=True)
    title = Column(Text, nullable=False)
    provider = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    difficulty = Column(Text, nullable=True)
    est_hours = Column(Integer, nullable=True)
    format = Column(Text, nullable=True)  # video | reading | project | quiz
    last_verified = Column(Date, nullable=True)

class ResourceSkill(Base):
    __tablename__ = "resource_skills"

    resource_id = Column(String(100), ForeignKey("resources.id"), primary_key=True)
    skill_id = Column(String(100), ForeignKey("skills.id"), primary_key=True)

class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    path_version = Column(Integer, default=1)
    milestones = Column(JSON, nullable=False)
    change_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="paths")

class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    resource_id = Column(String(100), ForeignKey("resources.id"), nullable=False)
    status = Column(Text, default="not_started")  # not_started | in_progress | done
    quiz_score = Column(Float, nullable=True)
    time_spent_min = Column(Integer, nullable=True)
    est_time_min = Column(Integer, nullable=True)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    resource_id = Column(String(100), ForeignKey("resources.id"), nullable=False)
    raw_text = Column(Text, nullable=False)
    extracted = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    resource_id = Column(String(100), ForeignKey("resources.id"), nullable=False)
    score = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
