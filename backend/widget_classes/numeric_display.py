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

class NumericDisplayWidget(Widget):
  #add restrictions if the number is to be integer / floating point / how many decimal places required
  def build(self):    
    dispay_rows = self.db_manager.get_rows("WidgetParams-num-display",
        ["InitialNum","ValueTag","ColorScheme"], "WidgetID", self.id)
    format_rows = self.db_manager.get_rows("WidgetParams-num-format",
        ["Format",	"LeftPadding", "Decimals"], "WidgetID", self.id)
    if not len(format_rows):
      format_rows.append({"Format": "Integer",
                          "LeftPadding": 0,
                          "Decimals": 0},) #use some defaults
    try:
      self.substitute_replacements(self.replacements, dispay_rows[0])
      self.init_num = dispay_rows[0].get("InitialNum", "**.**")
      self.indication = dispay_rows[0].get("ValueTag")
      self.color_scheme = dispay_rows[0].get("ColorScheme") 
      self.substitute_replacements(self.replacements, format_rows[0])
      self.num_format = format_rows[0].get("Format", "Integer")
      self.left_padding = format_rows[0].get("LeftPadding", 0)
      self.decimals = format_rows[0].get("Decimals",0)      
    except (IndexError, KeyError):
      event_msg = "NumericDisplayWidget {} path lookup error".format(self.id)
      self.app.display_event(event_msg)
    
    self.widget = Gtk.Fixed(width_request=self.width, height_request=self.height)
    self.lbl = Gtk.Label(width_request=self.width, height_request=self.height)
    self.widget.put(self.lbl,0,0)
    if not self.init_num:
      self.init_num = "-Unknown-"
    self.lbl.set_property("xalign", 0.5)
    self.lbl.set_text(self.init_num)
    self.set_styles(self.lbl)


  def class_update(self, factory, subscriber):
    if self.display != subscriber:
      return
    expression_val = self.connection_manager.evaluate_expression(self, self.indication, self.display)
    self.expression_err |= expression_val is None
    if type(expression_val) == type(None):
      expression_val = "**.**"
      self.expression_err = True
      return
    if self.num_format == "Float":
      text = ""
      dec = "" if type(self.decimals) == type(None) else int(self.decimals)
      pad = "" if type(self.left_padding) == type(None) else int(self.left_padding)
      line = """text = '{:"""+str(pad)+"."+str(dec)+"""f}'.format(expression_val)"""
      locs = locals()
      exec(line, globals(), locs)
      text = locs["text"]
      if pad:
        sign = ""
        if text.startswith("-"):
          sign = text[0]
          text = text[1:]
        whole_len = len(text.split(".")[0])
        add_chars = pad - whole_len
        if add_chars > 0:
          text = text.rjust(len(text)+add_chars, "0")
        text = sign + text
      self.lbl.set_text(text)
      return
    if self.num_format == "Hex":
      self.lbl.set_text("0x{:X}".format(expression_val))
      return
    if self.num_format == "Integer":
      pad = "" if type(self.left_padding) == type(None) else int(self.left_padding)
      self.lbl.set_text("{}".format(int(expression_val)))
      if pad:
        whole_len = len(text)
        add_chars = pad - whole_len
        if add_chars > 0:
          text = text.rjust(len(text)+add_chars, "0")
      return
    #No formatting, let python decide
    self.lbl.set_text("{}".format(expression_val))


    