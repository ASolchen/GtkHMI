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
import time, ast
from backend.widget_classes.widget import Widget

class StateIndicationWidget(Widget):
  #NEED TO BUILD UPDATE CLASS METHOD
  def build(self):
    rows = self.db_manager.get_rows("WidgetParams-state-display",
        ["ValueTag"], "WidgetID", self.id)
    try:
      self.substitute_replacements(self.replacements, rows[0])
      self.substitute_replacements(self.replacements, rows[0])
      self.initialState = rows[0]["ValueTag"] #TODO remove from here and db
    except (IndexError, KeyError):
      event_msg = "StateIndicationWidget {} path lookup error".format(self.id)
      self.app.display_event(event_msg)

    self.widget = Gtk.Label(width_request=self.width, height_request=(self.height))
    self.widget.set_property("xalign", 0.5)
    for state in self.states:
      if state["State"] != None:
        self.widget.set_text(state["Caption"])
    self.set_styles(self.widget)

  def animate_state(self, val):
    lbl_sc = self.widget.get_style_context()
    found = False
    for state in self.states:
      if type(val) != type(None):
        val = int(val)
        if val == state["State"]:
          found = True
    if not found:
      val = None
    match_state = None
    for state in self.states:
      if type(val) != type(None):
        val = int(val)
      if val == state["State"]:
        match_state = state
      else:
        lbl_sc.remove_class(state["Style"])
    if match_state:
      lbl_sc.add_class(match_state["Style"])
      self.widget.set_text(match_state["Caption"])

