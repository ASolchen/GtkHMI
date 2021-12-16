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

class StateControlWidget(Widget):
  def build(self):
    rows = self.db_manager.get_rows("WidgetParams-state-ctrl",
        ["ValueTag","ConfirmMessage"], "WidgetID", self.id)
    try:
      self.substitute_replacements(self.replacements, rows[0])
      self.value_tag = rows[0]["ValueTag"] #TODO remove from here and db
      self.confirm_msg = rows[0]["ConfirmMessage"]
    except (IndexError, KeyError):
      event_msg = "StateControlWidget {} path lookup error".format(self.id)
      self.app.display_event(event_msg)
    self.widget =Gtk.ComboBoxText(width_request=self.width, height_request=self.height, popup_fixed_width=True)
    self.widget.connect("changed", self.write_state_val)
    self.label = Gtk.Label()
    self.widget.add(self.label)
    self.widget.show_all()
    self.null_state_label = None
    for state in self.states:
      if state["State"] != None:
        self.widget.append(str(state["State"]), state["Caption"])
    self.set_styles(self.widget)

  def write_state_val(self, combo):
    val = combo.get_active()    
    if self.confirm_msg:
      #Confirmation Type Button
      self.app.confirm(self.write_confirm_callback, "{} {}".format(self.confirm_msg, combo.get_active_text()), [val])
    else:
      self.write_confirm_callback(val)

  def write_confirm_callback(self, val):
    self.write(self.value_tag, val)

  def animate_state(self, val):
    lbl_sc = self.label.get_style_context()
    combo_sc = self.widget.get_style_context()
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
        #combo_sc.remove_class(state["Style"])
    if match_state:
      lbl_sc.add_class(match_state["Style"])
      #combo_sc.add_class(state["Style"])
      self.label.set_text(match_state["Caption"])

    



 
