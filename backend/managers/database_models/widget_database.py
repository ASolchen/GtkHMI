import os
from sqlalchemy.sql import expression
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
from sqlalchemy.sql.type_api import INDEXABLE


WidgetConfigBase = declarative_base()

class WidgetParams(WidgetConfigBase):
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
  

class WidgetParamsAlarmConfig(WidgetConfigBase):
  __tablename__= 'widget-params-alarm-config'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)
  enable_expression = Column(String)
  ctrl_btn_style = Column(String)

class WidgetParamsCheckBox(WidgetConfigBase):
  __tablename__= 'widget-params-check-box'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)
  on_change = Column(String)
  initial_tag = Column(String)

class WidgetParamsControlButton(WidgetConfigBase):
  __tablename__= 'widget-params-ctrl-button'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  label = Column(String)
  image = Column(String)
  on_press = Column(String)
  on_release = Column(String)
  confirm_on_press_msg = Column(String)
  confirm_on_release_msg = Column(String)


class WidgetParamsDisplay(WidgetConfigBase):
  __tablename__= 'widget-params-display'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  overlay = Column(Boolean)
  pollrate = Column(Float)
  on_startup = Column(String)
  on_shutdown = Column(String)

class WidgetParamsEventConfig(WidgetConfigBase):
  __tablename__= 'widget-params-event-config'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)
  enable_expression = Column(String)
  ctrl_btn_style = Column(String)

class WidgetParamsImage(WidgetConfigBase):
  __tablename__= 'widget-params-image'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  file_path = Column(String)

class WidgetParamsLabel(WidgetConfigBase):
  __tablename__= 'widget-params-label'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  label_text = Column(String)
  justify = Column(Integer)

class WidgetParamsListSelect(WidgetConfigBase):
  __tablename__= 'widget-params-list-select'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)
  on_change = Column(String)
  initial_tag = Column(String)
  expression_tag = Column(String)

class WidgetParamsNumDisplay(WidgetConfigBase):
  __tablename__= 'widget-params-num-display'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  initail_num = Column(String)
  value_tag = Column(String)
  color_scheme = Column(String)


class WidgetParamsNumEntry(WidgetConfigBase):
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

class WidgetParamsNumFormat(WidgetConfigBase):
  __tablename__= 'widget-params-num-format'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  format = Column(String)
  left_padding = Column(String)
  decimals = Column(Integer)

class WidgetParamsSettingsConfig(WidgetConfigBase):
  __tablename__= 'widget-params-settings-config'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)
  enable_expression = Column(String)
  ctrl_btn_style = Column(String)


class WidgetParamsCtrlState(WidgetConfigBase):
  __tablename__= 'widget-params-ctrl-state'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)
  confirm_msg = Column(String)


class WidgetParamsStateDisplay(WidgetConfigBase):
  __tablename__= 'widget-params-state-display'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)


class WidgetParamsStringDisplay(WidgetConfigBase):
  __tablename__= 'widget-params-string-display'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  initial_string = Column(String)
  value_tag = Column(String)

class WidgetParamsStringEntry(WidgetConfigBase):
  __tablename__= 'widget-params-string-entry'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)
  placeholder = Column(String)
  max_char = Column(Integer)
  justify = Column(Integer)
  label = Column(String)

class WidgetParamsTextView(WidgetConfigBase):
  __tablename__= 'widget-params-text-view'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  value_tag = Column(String)

class GlobalObjectParameterValues(WidgetConfigBase):
  __tablename__= 'global-object-params'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, primary_key=True)
  widget_id = Column(String, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  description = Column(String)
  name = Column(String, nullable=False)
  value = Column(String, nullable=False)

class WidgetAnimations(WidgetConfigBase):
  __tablename__= 'widget-animations'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, primary_key=True)
  type = Column(String, nullable=False)
  widget_id = Column(String, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  description = Column(String)
  expression = Column(String, nullable=False)

class WidgetStateIndications(WidgetConfigBase):
  __tablename__= 'widget-state-indications'
  relationship('WidgetParams', backref=backref('children', passive_deletes=True))
  id = Column(Integer, primary_key=True)
  widget_id = Column(String, ForeignKey(WidgetParams.id, ondelete='CASCADE'), primary_key=True)
  state = Column(Integer)
  caption = Column(String)
  style = Column(String)


class WidgetDb():
  models = {
    "widget-params-base": WidgetParams,
    "widget-params-alarm-config": WidgetParamsAlarmConfig,
    "widget-params-check-box": WidgetParamsCheckBox,
    "widget-params-ctrl-button": WidgetParamsControlButton,
    "widget-params-display": WidgetParamsDisplay,
    "widget-params-event-config": WidgetParamsEventConfig,
    "widget-params-image": WidgetParamsImage,
    "widget-params-label": WidgetParamsLabel,
    "widget-params-list-select": WidgetParamsListSelect,
    "widget-params-num-display": WidgetParamsNumDisplay,
    "widget-params-num-entry": WidgetParamsNumEntry,
    "widget-params-num-format": WidgetParamsNumFormat,
    "widget-params-settings-config": WidgetParamsSettingsConfig,
    "widget-params-ctrl-state": WidgetParamsCtrlState,
    "widget-params-state-display": WidgetParamsStateDisplay,
    "widget-params-string-display": WidgetParamsStringDisplay,
    "widget-params-string-entry": WidgetParamsStringEntry,
    "widget-params-text-view": WidgetParamsTextView,
    "global-object-params": GlobalObjectParameterValues,
    "widget-animations": WidgetAnimations,
    "widget-state-indications": WidgetStateIndications,
  }


  @classmethod
  def open(cls, engine):
    WidgetConfigBase.metadata.create_all(engine) #creates all the tables above using the provided engine
  

