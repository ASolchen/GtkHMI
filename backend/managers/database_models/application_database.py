import os
from sqlalchemy.sql.expression import table
from gi.repository import GObject
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base, relationship, backref
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql.operators import ColumnOperators
from sqlalchemy.sql.sqltypes import Float, Numeric


AppConfigBase = declarative_base()

class AlarmEventConfig(AppConfigBase):
    __tablename__ = 'alarm-event-config'
    id = Column(Integer, primary_key=True)
    severity = Column(Integer)
    enable = Column(Boolean)
    indications = Column(String)

class AlarmEvents(AppConfigBase):
    __tablename__ = 'alarm-events'
    id = Column(Integer, primary_key=True)
    severity = Column(Integer)
    enable = Column(Boolean)
    message = Column(String)
    state = Column(Integer)
    event_on_timestamp = Column(Float)
    event_of_timestamp = Column(Float)
    ack_state = Column(Integer)
    ack_timestamp = Column(Float)

class EventLog(AppConfigBase):
    __tablename__ = 'event-log'
    id = Column(Integer, primary_key=True)
    msg = Column(String)

class ApplicationSettings(AppConfigBase):
    __tablename__ = 'application-settings'
    id = Column(Integer, primary_key=True)
    style_sheet = Column(String)
    width = Column(Integer, default=640)
    height = Column(Integer, default=480)
    dark_theme = Column(Boolean)
    startup_display = Column(Integer, nullable=False) #widget id of the display




class AppDb():
    models = {
        "alarm_event_config": AlarmEventConfig,
        "event-log": EventLog,
        "alarm_events":AlarmEvents,
        "application-settings": ApplicationSettings,
    }

    @classmethod
    def open(cls, engine):
        AppConfigBase.metadata.create_all(engine) #creates all the tables above using the provided engine
    
