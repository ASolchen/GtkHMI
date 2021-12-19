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


ProjectConfigBase = declarative_base()

class WidgetParams(ProjectConfigBase):
  __tablename__ = 'widget-params-base'
  id = Column(Integer, primary_key=True)
  #see: https://stackoverflow.com/questions/6782133/sqlalchemy-one-to-many-relationship-on-single-table-inheritance-declarative/6782238#6782238
  parent_id = Column(Integer, ForeignKey(id, ondelete='CASCADE'), nullable=True) # integer of parent, if NULL then top level (Display)
  widget_class = Column(String) # widget type
  build_order = Column(Integer)
  x = Column(Integer)
  y = Column(Integer)
  width = Column(Integer)
  height = Column(Integer)
  description = Column(String)
  global_reference = Column(Boolean) # if True, is a global parent and all of its children are part of a global assembly
  

class WidgetParamsAlarmConfig(ProjectConfigBase):
  __tablename__= 'widget-params-alarm-config'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)
  enable_expression = Column(String)
  ctrl_btn_style = Column(String)

class WidgetParamsCheckBox(ProjectConfigBase):
  __tablename__= 'widget-params-check-box'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)
  on_change = Column(String)
  initial_tag = Column(String)

class WidgetParamsControlButton(ProjectConfigBase):
  __tablename__= 'widget-params-ctrl-button'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  label = Column(String)
  image = Column(String)
  on_press = Column(String)
  on_release = Column(String)
  confirm_on_press_msg = Column(String)
  confirm_on_release_msg = Column(String)


class WidgetParamsDisplay(ProjectConfigBase):
  __tablename__= 'widget-params-display'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  overlay = Column(Boolean)
  pollrate = Column(Float)
  on_startup = Column(String)
  on_shutdown = Column(String)

class WidgetParamsEventConfig(ProjectConfigBase):
  __tablename__= 'widget-params-event-config'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)
  enable_expression = Column(String)
  ctrl_btn_style = Column(String)

class WidgetParamsImage(ProjectConfigBase):
  __tablename__= 'widget-params-image'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  file_path = Column(String)

class WidgetParamsLabel(ProjectConfigBase):
  __tablename__= 'widget-params-label'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  label_text = Column(String)
  justify = Column(Integer)

class WidgetParamsListSelect(ProjectConfigBase):
  __tablename__= 'widget-params-list-select'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)
  on_change = Column(String)
  initial_tag = Column(String)
  expression_tag = Column(String)

class WidgetParamsNumDisplay(ProjectConfigBase):
  __tablename__= 'widget-params-num-display'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  initail_num = Column(String)
  value_tag = Column(String)
  color_scheme = Column(String)


class WidgetParamsNumEntry(ProjectConfigBase):
  __tablename__= 'widget-params-num-entry'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  placeholder = Column(String)
  max_char = Column(Integer)
  justify = Column(Integer)
  label_text = Column(String)
  value_tag = Column(String)
  val_min = Column(Float)
  val_max = Column(Float)

class WidgetParamsNumFormat(ProjectConfigBase):
  __tablename__= 'widget-params-num-format'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  format = Column(String)
  left_padding = Column(String)
  decimals = Column(Integer)

class WidgetParamsSettingsConfig(ProjectConfigBase):
  __tablename__= 'widget-params-settings-config'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)
  enable_expression = Column(String)
  ctrl_btn_style = Column(String)


class WidgetParamsCtrlState(ProjectConfigBase):
  __tablename__= 'widget-params-ctrl-state'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)
  confirm_msg = Column(String)


class WidgetParamsStateDisplay(ProjectConfigBase):
  __tablename__= 'widget-params-state-display'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)


class WidgetParamsStringDisplay(ProjectConfigBase):
  __tablename__= 'widget-params-string-display'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  initial_string = Column(String)
  value_tag = Column(String)

class WidgetParamsStringEntry(ProjectConfigBase):
  __tablename__= 'widget-params-string-entry'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)
  placeholder = Column(String)
  max_char = Column(Integer)
  justify = Column(Integer)
  label = Column(String)

class WidgetParamsTextView(ProjectConfigBase):
  __tablename__= 'widget-params-text-view'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)


class WidgetDb():
  def __init__(self) -> None:
    self.widget_parm_models = {
      "base": WidgetParams,
      "alarm-config": WidgetParamsAlarmConfig,
      "check-box": WidgetParamsCheckBox,
      "ctrl-button": WidgetParamsControlButton,
      "display" : WidgetParamsDisplay,
      "event-config": WidgetParamsEventConfig,
      "image": WidgetParamsImage,
      "label": WidgetParamsLabel,
      "list-select": WidgetParamsListSelect,
      "num-display": WidgetParamsNumDisplay,
      "num-entry" : WidgetParamsNumEntry,
      "num-format": WidgetParamsNumFormat,
      "settings-config": WidgetParamsSettingsConfig,
      "ctrl-state": WidgetParamsCtrlState,
      "state-display": WidgetParamsStateDisplay,
      "string-display": WidgetParamsStringDisplay,
      "string-entry": WidgetParamsStringEntry,
      "text-view": WidgetParamsTextView
    }

  def __enter__(self):
    engine = create_engine(f"sqlite:///{os.path.join(os.path.dirname(__file__), 'test_project.db')}") #should create a .db file next to this one
    res = ProjectConfigBase.metadata.create_all(engine) #creates all the tables above
    Session = sessionmaker(bind=engine)
    self.session = Session()
    return self
  
  def __exit__(self, *args):
    self.session.close()


import os
try:
  os.remove('/home/asolchen/Documents/repos/GtkHMI/backend/managers/test_project.db')
except:
  pass

with WidgetDb() as db:
  row = db.widget_parm_models.get("base")(widget_class='display', description="Top Level Display")
  db.session.add(row)
  db.session.commit() # need to commit to get widget's id
  display_id = row.id
  for table in db.widget_parm_models:
    row = db.widget_parm_models.get("base")(parent_id=display_id, widget_class=table, x=10, y=10, width=10, height=10, description="Some description")
    db.session.add(row)
    db.session.commit() # need to commit to get widget's id
    if table =='alarm-config': 
      idx = row.id
      row = db.widget_parm_models.get(table)(id=idx, value_tag="testTag", enable_expression="Test expression", ctrl_btn_style = "TestStyle")
      db.session.add(row)
      db.session.commit()
    if table =='check-box': 
      idx = row.id
      row = db.widget_parm_models.get(table)(id=idx, value_tag="TestTag",  on_change="Test OnChange",  initial_tag="TestInitialTag")
      db.session.add(row)
      db.session.commit()
    if table =='ctrl-button': 
      idx = row.id
      row = db.widget_parm_models.get(table)(id=idx,
                                            label ="Hello",
                                            image = "testImage",
                                            on_press = "on press script",
                                            on_release = "on release script",
                                            confirm_on_press_msg = "Really?",
                                            confirm_on_release_msg = "Are you sure?")
      db.session.add(row)
      db.session.commit()