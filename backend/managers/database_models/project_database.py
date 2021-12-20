from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from backend.managers.database_models.subscription_database import SubscriptionDb
from backend.managers.database_models.widget_database import WidgetDb
from backend.managers.database_models.connection_database import ConnectionDb
from backend.managers.database_models.application_database import AppDb



class ProjectDatabase():
  def __init__(self):
    self.widget_config = WidgetDb
    self.connection_config = ConnectionDb
    self.app_config = AppDb
    self.engine = None
    self.session = None
  
  def open(self, path):
    if self.session:
      self.close()
    self.engine = create_engine(f"sqlite:///{path}") #should create a .db file next to this one
    AppDb.open(self.engine) #creates all the tables in app config tables
    WidgetDb.open(self.engine) #creates all the tables in widgets
    ConnectionDb.open(self.engine) #creates all the tables in widgets
    Session = sessionmaker(bind=self.engine)
    self.session = Session()
  
  def close(self):
    if self.session:
      self.session.close()
    self.session = None
    self.engine = None
