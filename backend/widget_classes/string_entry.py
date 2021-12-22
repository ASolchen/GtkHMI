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
import time, numbers

from backend.widget_classes.widget import Widget

class StringEntryWidget(Widget):
  def build(self):
    rows = self.db_manager.get_rows("WidgetParams-str-entry",
        ["PlaceHolder", "MaxChar","Justify","Label","ValueTag"], "WidgetID", self.id)
        #MaxChar unused now just divide the width by 12 to get number of chars
    try:
      self.substitute_replacements(self.replacements, rows[0])
      self.place_holder = rows[0]["PlaceHolder"]
      #self.max_char = rows[0]["MaxChar"]
      self.text_justify = rows[0]["Justify"]
      self.label = rows[0]["Label"]
      self.value_tag = rows[0]["ValueTag"]
    except (IndexError, KeyError):
      event_msg = "StringEntryWidget {} path lookup error".format(self.id)
      self.app.display_event(event_msg)

    self.widget = Gtk.Entry(height_request=self.height)  #this only sets minimum height
    self.widget.set_width_chars(int(round(self.width/12)))      #this sets the minimum width in chars
    self.widget.set_placeholder_text(self.place_holder)
    _justify = {"LEFT": 0.0, "CENTER": 0.5, "RIGHT": 1.0}
    x_align = 0.5
    if self.text_justify in _justify:
      x_align = _justify.get(self.text_justify, 0.5)
    self.widget.set_alignment(x_align)
    self.set_styles(self.widget)
    self.widget.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
    self.widget.connect("button-press-event", self.entry_press_action)
    self.widget.set_can_focus(False)
    #self.widget.connect("focus-in-event",self.enable_key_listener) # detects when entry gets focus
    #self.widget.connect("focus-out-event",self.set_value_off_focus) # detects when entry loses focus
    #self.widget.connect("button-press-event",self.entry_press_action)  #detects when entry is clicked

  '''def enable_key_listener(self, *args):
    self.signals.append(self.widget.connect('key-release-event', self.key_pressed))

  def key_pressed(self, widget, event):
    if event.get_keycode().keycode == 13:
      val =self.widget.get_text()
      self.set_value(val)'''

  def entry_press_action(self,*args):
    if self.builder_mode:
      #Don't do actions if in builder mode
      return
    self.app.open_keypad(self.set_value, self,self.widget ,self.params,self.widget.get_text())
  
  def set_value_off_focus(self, entry, event):
    self.set_value(entry.get_text())
  
  def update_value(self,val, *args):
    self.widget.set_text(val)
    self.set_value(val)

  def set_value(self, val,*args):
    self.write(self.value_tag, val)

  def class_update(self, factory, subscriber):
    if self.display != subscriber or self.widget.has_focus():
      return
    if self.value_tag == None:
      #means string isn't updated by a tag if ValueTag is None/NULL
      return
    else:
      expression_val = self.connection_manager.evaluate_expression(self, self.value_tag, self.display)
      self.expression_err |= expression_val is None
    if type(expression_val) == type(None):
      expression_val = "ERROR"
    self.widget.set_text("{}".format(expression_val))
  


