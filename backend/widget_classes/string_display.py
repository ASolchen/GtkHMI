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

class StringDisplayWidget(Widget):
  def build(self):
    rows = self.db_manager.get_rows("WidgetParams-str-display",
        ["InitialStr","Tag"], "WidgetID", self.id)
    try:
      self.substitute_replacements(self.replacements, rows[0])
      self.placeholder = rows[0]["InitialStr"]
      self.tag = rows[0]["Tag"]
    except (IndexError, KeyError):
      event_msg = "StringDisplayWidget {} path lookup error".format(self.id)
      self.app.display_event(event_msg)
    #add color animations to border
    self.widget = Gtk.Label(width_request=self.width, height_request=self.height)
    if not self.placeholder:
      self.placeholder = "-Unknown-"
    self.widget.set_property("xalign", 0.5)
    self.widget.set_text(self.placeholder)
    self.set_styles(self.widget)

  def class_update(self, factory, subscriber):
    if self.display != subscriber:
      return
    expression_val = self.connection_manager.evaluate_expression(self, self.tag, self.display)
    self.expression_err |= expression_val is None
    if type(expression_val) == type(None):
      expression_val = "----"
    self.widget.set_text("{}".format(expression_val))