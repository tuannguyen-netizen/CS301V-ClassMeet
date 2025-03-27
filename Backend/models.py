from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class MembershipRole(enum.Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    
    # Relationships
    created_classes = relationship("Class", back_populates="creator")
    class_memberships = relationship("ClassMembership", back_populates="user")
    meeting_participants = relationship("MeetingParticipants", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")

class Class(Base):
    __tablename__ = 'class'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    creator_id = Column(Integer, ForeignKey('user.id'))
    
    # Relationships
    creator = relationship("User", back_populates="created_classes")
    memberships = relationship("ClassMembership", back_populates="class_")
    meetings = relationship("Meeting", back_populates="class_")

class ClassMembership(Base):
    __tablename__ = 'class_membership'
    
    class_id = Column(Integer, ForeignKey('class.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    joined_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    role = Column(Enum(MembershipRole), default=MembershipRole.student)
    
    # Relationships
    user = relationship("User", back_populates="class_memberships")
    class_ = relationship("Class", back_populates="memberships")

class Meeting(Base):
    __tablename__ = 'meeting'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey('class.id'))
    title = Column(String(100), nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    
    # Relationships
    class_ = relationship("Class", back_populates="meetings")
    participants = relationship("MeetingParticipants", back_populates="meeting")
    chat_messages = relationship("ChatMessage", back_populates="meeting")

class MeetingParticipants(Base):
    __tablename__ = 'meeting_participants'
    
    meeting_id = Column(Integer, ForeignKey('meeting.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    joined_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationships
    meeting = relationship("Meeting", back_populates="participants")
    user = relationship("User", back_populates="meeting_participants")

class ChatMessage(Base):
    __tablename__ = 'chat_message'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey('meeting.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    message = Column(Text, nullable=False)
    sent_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationships
    meeting = relationship("Meeting", back_populates="chat_messages")
    user = relationship("User", back_populates="chat_messages")