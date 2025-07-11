from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Float, Text,TIMESTAMP,text
from sqlalchemy.orm import relationship
import datetime
from db import Base

# Base = declarative_base()


# Admin Table 
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    # Scope (multiple grades, one class, one region)
    grade_scope = Column(String, nullable=False)  
    class_scope = Column(String, nullable=False)  
    region_scope = Column(String, nullable=False) 

    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)






#  Student Table
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    grade = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    region = Column(String, nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

    submissions = relationship("Submission", back_populates="student")
    scores = relationship("QuizScore", back_populates="student")


#  Submission Table 
class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    homework_title = Column(String, nullable=False)
    submitted = Column(Boolean, default=False)
    submission_date = Column(Date)

    student = relationship("Student", back_populates="submissions")


#  Quiz Table
class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True)
    subject = Column(String, nullable=False)
    grade = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    region = Column(String, nullable=False)
    scheduled_date = Column(Date, nullable=False)

    scores = relationship("QuizScore", back_populates="quiz")


#  Quiz Score Table
class QuizScore(Base):
    __tablename__ = "quiz_scores"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    score = Column(Float, nullable=False)

    student = relationship("Student", back_populates="scores")
    quiz = relationship("Quiz", back_populates="scores")


# Queries Table
class Queries(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    sql = Column(Text, nullable=False)
    title = Column(String)
    insights = Column(Text)
    chart_url = Column(String)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

    admin_id=Column(Integer)
