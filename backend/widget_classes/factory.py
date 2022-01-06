# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Jason Engman <jengman@testtech-solutions.com>
# Copyright (c) 2021 Adam Solchenberger <asolchenberger@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
import re
import time
from backend.widget_classes.widget import Widget
from backend.widget_classes.numeric_display import NumericDisplayWidget
from backend.widget_classes.string_display import StringDisplayWidget
from backend.widget_classes.display import DisplayWidget, PopupDisplayWidget
from backend.widget_classes.numeric_entry import NumericEntryWidget
from backend.widget_classes.string_entry import StringEntryWidget
from backend.widget_classes.image import ImageWidget
from backend.widget_classes.button import ButtonWidget
from backend.widget_classes.label import LabelWidget
from backend.widget_classes.state_indicator import StateIndicationWidget
from backend.widget_classes.textview import TextViewWidget
from backend.widget_classes.state_control import StateControlWidget
from backend.widget_classes.alarm_viewer import AlarmViewWidget
from backend.widget_classes.Event_viewer import EventViewWidget
from backend.widget_classes.settings import SettingsWidget
from backend.widget_classes.list_select import ListSelectionWidget
from backend.widget_classes.checkbox import CheckBoxWidget
from backend.managers.database_models.widget_database import WidgetAnimations, WidgetStateIndications, GlobalObjectParameterValues

class UnknownWidgetError(KeyError):
  pass

class GladeIdMissing(KeyError):
  pass

WIDGET_TYPES = {
  "base": Widget,
  "ctrl-button": ButtonWidget,
  "num-entry":NumericEntryWidget,      
  "string-entry":StringEntryWidget,
  "label": LabelWidget,
  "image": ImageWidget,
  "text-view":TextViewWidget,
  "num-display":NumericDisplayWidget,
  "string-display":StringDisplayWidget,
  "state-display":StateIndicationWidget,
  "ctrl-state":StateControlWidget,
  "list-select":ListSelectionWidget,
  "check-box":CheckBoxWidget,
  "alarm-view": AlarmViewWidget,
  "event-log-view":EventViewWidget,
  "settings-config": SettingsWidget,
  "display": DisplayWidget
  }
    
class WidgetFactory(GObject.Object):

  @GObject.Property(type=bool, default=True, flags=GObject.ParamFlags.READWRITE)
  def builder_mode(self):
    return self._builder_mode  
  @builder_mode.setter
  def builder_mode(self, value):
    self._builder_mode = value
    #TODO do stuff here when builder mode is changed
  
  def __init__(self, app):
    super(WidgetFactory, self).__init__()
    self.app = app
    self.widgets = {}
    self.project_db = app.db_manager.project_db
    self.widget_config = self.project_db.widget_config
    self._builder_mode = app.builder_mode
    sig = app.connect('notify::builder-mode', self.on_app_builder_mode)
    self.widget_types = WIDGET_TYPES
    self.displays = {} #used to ref id to Python class of the open displays

  def on_app_builder_mode(self, app, signal):
    self.builder_mode = app.builder_mode 

  def open_display(self, widget_id, replacements=[]):
    session = self.project_db.session
    base_result, display_result = session.query(Widget.orm_model, DisplayWidget.orm_model)\
      .filter(Widget.orm_model.id == DisplayWidget.orm_model.id)\
      .filter(DisplayWidget.orm_model.id == widget_id)\
      .first()
    if not display_result:
      raise Exception("Display id {widget_id} not in project database")
    params = Widget.get_params_from_orm(base_result)
    params.update(DisplayWidget.get_params_from_orm(display_result))
    if params["overlay"]: 
      self.displays[params["id"]] = self.create_widget(PopupDisplayWidget, params)
      self.displays[params["id"]].window.show_all()     
    else: #if not a popup only, check for intersect and delete if nessasary
      hitlist = []
      for display in self.displays:
        if self.displays[display].intersect(base_result):
          hitlist.append(display)
      for display in hitlist:
        self.displays[display].kill_children()
        self.displays[display].widget.destroy()
        self.displays[display].shutdown()
        del(self.displays[display])
      params["parent"] = self.app.hmi_layout
      id = params["id"]
      self.displays[id] = self.create_widget(params)
      self.displays[id].widget.show_all()
  
  def create_widget(self, params):
    widget_class = WIDGET_TYPES[params['widget_class']]
    #lookup animations, states, replacements
    id = params.get("id")
    if not id:
      raise Exception("Cannot create widget without id")
    if params.get("parent"):
      if not params.get("replacements"):
        params["replacements"] = []
      if hasattr(params["parent"], "replacements"):
        params["replacements"] += params["parent"].replacements[:]
    session = self.project_db.session
    globals_result = session.query(GlobalObjectParameterValues).filter(GlobalObjectParameterValues.widget_id==id).all()
    if len(globals_result):
      if not params.get("replacements"):
        params["replacements"] = []
      for res in globals_result:
        params["replacements"].append({"name": res.name, "value": res.value})
    animation_result = session.query(WidgetAnimations).filter(WidgetAnimations.widget_id==id).all()
    if len(animation_result):
      if not params.get("animations"):
        params["animations"] = []
      for res in animation_result:
        if params.get("replacements"):
          for replacement in params["replacements"]:
            res.expression = res.expression.replace(f'#{replacement["name"]}#', replacement["value"])
        params["animations"].append({"type": res.type, "expression": res.expression})
    states_result = session.query(WidgetStateIndications).filter(WidgetStateIndications.widget_id==id).all()
    if len(states_result):
      if not params.get("states"):
        params["states"] = []
      for res in states_result:
        if params.get("replacements"):
          for replacement in params["replacements"]:
            res.style = res.style.replace(f'#{replacement["name"]}#', replacement["value"])
            res.caption = res.caption.replace(f'#{replacement["name"]}#', replacement["value"])
        params["states"].append({"state": res.state, "style": res.style, "caption": res.caption})
    self.widgets[params['id']] = widget_class(self, params)
    return self.widgets[params['id']]


  def close_display(self, widget_id):
    params = self.db_manager.get_rows("Widgets", Widget.base_parmas, "ID", widget_id)[0]
    self.displays[params["ID"]].kill_it()

  def get_widget_by_id(self, widget_id):
    display_id = widget_id.split('.')[0]
    if display_id in self.displays:
      return self.displays[display_id].get_widget_by_id(widget_id)
    return None

  def kill_all(self):
    display_dict = self.displays.copy()
    for display in display_dict:
      self.displays[display].kill_children()
      del(self.displays[display])
    for c in self.app.hmi_layout.get_children():
      self.app.hmi_layout.remove(c)


