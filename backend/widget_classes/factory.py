# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Jason Engman <jengman@testtech-solutions.com>
# Copyright (c) 2021 Adam Solchenberger <asolchenberger@testtech-solutions.com>
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

class UnknownWidgetError(KeyError):
  pass

class GladeIdMissing(KeyError):
  pass

WIDGET_TYPES = {
      "ctrl-button": ButtonWidget,
      "num-entry":NumericEntryWidget,      
      "str-entry":StringEntryWidget,
      "label": LabelWidget,
      "image": ImageWidget,
      "textview":TextViewWidget,
      "num-display":NumericDisplayWidget,
      "str-display":StringDisplayWidget,
      "state-display":StateIndicationWidget,
      "state-control":StateControlWidget,
      "list-select":ListSelectionWidget,
      "check-box":CheckBoxWidget,
      "alarm-view": AlarmViewWidget,
      "event-log-view":EventViewWidget,
      "settings-config": SettingsWidget
    }
    
class WidgetFactory(GObject.Object):
  
  def __init__(self, app):
    super(WidgetFactory, self).__init__()
    self.app = app
    self.db_manager = app.db_manager
    self.builder_mode = False
    self.widget_types = WIDGET_TYPES
    self.displays = {} #used to ref id to Python class of the open displays   

  def open_display(self, widget_id, replacements=[]):
    params = self.db_manager.get_rows("Widgets", Widget.base_parmas, "ID", widget_id)[0]
    if not params["Class"] == u"display":
      return
    params.update(self.db_manager.get_rows("WidgetParams-display", ["Overlay"], "WidgetID", widget_id)[0])
    if params["Overlay"]: 
      params["Display"] = params["ID"] #this widget is the parent display
      self.displays[params["ID"]] = PopupDisplayWidget(self, params, replacements)
      self.displays[params["ID"]].window.show_all()     
    else: #if not a popup only, check for intersect and delete if nessasary
      hitlist = []
      for display in self.displays:
        if self.displays[display].intersect(params["X"], params["Y"], params["Width"], params["Height"]):
          hitlist.append(display)
      for display in hitlist:
        self.displays[display].kill_children()
        self.displays[display].widget.destroy()
        self.displays[display].shutdown()
        del(self.displays[display])
      params["Display"] = params["ID"] #this widget is the parent display
      self.displays[params["ID"]] = DisplayWidget(self, self.app.layout, params, replacements)
      self.displays[params["ID"]].widget.show_all()
  
  def close_display(self, widget_id):
    params = self.db_manager.get_rows("Widgets", Widget.base_parmas, "ID", widget_id)[0]
    self.displays[params["ID"]].kill_it()

  def get_widget_by_id(self, widget_id):
    display_id = widget_id.split('.')[0]
    if display_id in self.displays:
      return self.displays[display_id].get_widget_by_id(widget_id)
    return None

