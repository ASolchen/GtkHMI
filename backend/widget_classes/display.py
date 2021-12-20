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
from backend.managers.database_models.widget_database import WidgetParamsDisplay

class DisplayWidget(Widget):

  orm_model = WidgetParamsDisplay
  @classmethod
  def get_params_from_orm(cls, result):
    params = {
      "pollrate": result.pollrate,
      "overlay": result.overlay,
      "on_startup": result.on_startup,
      "on_shutdown": result.on_shutdown,
    }
    return params

  def __init__(self, factory, params):
    self.widget = Gtk.Fixed()
    super(DisplayWidget, self).__init__(factory, params)
    self.overlay = params.get("overlay") #if overlay, this is a popup display
    self.pollrate = params.get("pollrate")
    self.startup_script = params.get("on_startup")
    self.shutdown_script = params.get("on_shutdown")
    self.widget.set_property("width_request", self.width)
    self.widget.set_property("height_request", self.height)
    self.polling = True
    self.startup()

  def update_tags(self):
    if self.builder_mode:
      return
    self.connection_manager.emit("tag_update", self.id) #just let widgets know to update
    return self.polling

  def startup(self):
    if self.builder_mode:
      return
    self.db_manager.clear_tag_subs(self.id)
    GObject.timeout_add(self.pollrate* 1000, self.update_tags)
    if self.startup_script:
      exec(self.startup_script)
  
  def shutdown(self):
    if self.builder_mode:
      return
    self.polling = False
    self.db_manager.clear_tag_subs(self.id)
    if self.shutdown_script:
      exec(self.shutdown_script)



class PopupDisplayWidget(DisplayWidget):
  def __init__(self, factory, params):
    self.window = PopupWindow(factory.app.root)
    self.window.set_default_size(params["Width"], params["Height"])
    self.window.set_border_width(1)
    self.window.set_keep_above(True)
    self.window.set_decorated(False)
    self.widget = self.window.layout
    params["parent"] = self.widget
    super(PopupDisplayWidget, self).__init__(factory, params)
    self.window.show_all()


  def build(self):
    rows = self.db_manager.get_rows("WidgetParams-display",
    ["Overlay", "Pollrate", "StartupScript", "ShutdownScript"], "WidgetID", self.id)
    try:
      self.substitute_replacements(self.replacements, rows[0])
      self.overlay = rows[0]["Overlay"] #if overlay, this is a popup display
      self.pollrate = rows[0]["Pollrate"]
      self.startup_script = rows[0]["StartupScript"]
      self.shutdown_script = rows[0]["ShutdownScript"]
    except (IndexError, KeyError):
      print("DisplayWidget {} path lookup error".format(self.id))
    self.widget = Gtk.Fixed(width_request=self.width, height_request=self.height)
    sc = self.window.get_style_context()
    for style in self.styles:
      sc.add_class(style)
    self.polling = True
    self.startup()
    
  def kill_it(self):
    self.kill_children() #clean up listeners on display and all children
    self.window.destroy()

class PopupWindow(Gtk.Dialog):
  def __init__(self, parent):
    Gtk.Dialog.__init__(self, "", parent, Gtk.DialogFlags.MODAL,
                        )
    self.layout = Gtk.Fixed()
    c = self.get_content_area()
    c.add(self.layout)