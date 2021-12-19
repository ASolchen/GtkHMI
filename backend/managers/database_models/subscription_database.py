import os
import gi, time

from sqlalchemy.sql.expression import table
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base, relationship, backref
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql.sqltypes import Float, Numeric

SubscriptionBase = declarative_base()

class ValuesTable(SubscriptionBase): # this table holds all tag values being subscribed to
  __tablename__ = 'values'
  id = Column(Integer, primary_key=True)
  value = Column(String)
  timestamp = Column(Float)
  datatype = Column(String)

class Subsciptions(SubscriptionBase): # this table holds all tag values being subscribed to
  __tablename__ = 'subscriptions'
  id = Column(Integer, primary_key=True)
  value_id = Column(Integer, ForeignKey(ValuesTable.id))
  widget_id = Column(Integer)
  tag_id = Column(String) #in [Connection]Tag e.g. [PLC1]SomeTag

class SubscriptionDb():
  def __init__(self) -> None:
    self.models = {
      "values": ValuesTable,
    }
    engine = create_engine('sqlite:///:memory:') #should create a .db file next to this one
    res = SubscriptionBase.metadata.create_all(engine) #creates all the tables above
    Session = sessionmaker(bind=engine)
    self.session = Session()

  def close(self, *args):
    self.session.close()

