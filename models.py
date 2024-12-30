import discord
from discord.ext import commands
from discord import app_commands
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time

Base = declarative_base()

session = None

class reports(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    report_type = Column(String)
    message_id = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)
    reason = Column(String)
    mod_action = Column(String, default="")
    status = Column(String)
    claim_button_id = Column(String, nullable=True)
    claim_button_active = Column(Boolean, default=True)
    resolve_button_id = Column(String, nullable=True)
    resolve_button_active = Column(Boolean, default=True)
    edit_reason_button_id = Column(String, nullable=True)
    edit_reason_button_active = Column(Boolean, default=True)
    claimer_id = Column(Integer, nullable=True)
    resolver_id = Column(Integer, nullable=True)
    reporter_id = Column(Integer)
    embed_message_id = Column(Integer, nullable=True)
    last_updated = Column(Float, nullable=False, default=time.time())
    active = Column(Boolean, default=True)

def get_session():
    global session
    if session is None:
        engine = create_engine("sqlite:///reports.db")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
    return session

def get_report_by_id(report_id: int):
    session = get_session()
    return session.query(reports).filter_by(id=report_id).all()

def get_report_by_message_id(message_id: int):
    session = get_session()
    return session.query(reports).filter_by(message_id=message_id).first()

def get_report_by_user_id(user_id: int):
    session = get_session()
    return session.query(reports).filter_by(user_id=user_id).all()

def get_claim_button_id(report_id: int):
    return f"claim_button_{report_id}"

def get_resolve_button_id(report_id: int):
    return f"resolve_button_{report_id}"

def get_edit_reason_button_id(report_id: int):
    return f"edit_reason_button_{report_id}"