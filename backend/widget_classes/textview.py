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

import gi,os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
import re
import time
from backend.widget_classes.widget import Widget

class TextViewWidget(Widget):
  def build(self):
    self.tempFP = 'Public/textviewTemp.txt'
    rows = self.db_manager.get_rows("WidgetParams-textview", ["ValueTag"], "WidgetID", self.id)
    try:
      self.substitute_replacements(self.replacements, rows[0])
      self.tag = rows[0]["ValueTag"]
      self.params["ValueTag"] = self.tag
    except (IndexError, KeyError):
      event_msg = "TextViewWidget {} path lookup error".format(self.id)
      self.app.display_event(event_msg)
    self.widget = Gtk.ScrolledWindow(height_request=self.height, width_request=self.width)
    self.text_view = Gtk.TextView(height_request=self.height, width_request=self.width)
    self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
    self.text_view.set_left_margin(10)
    self.text_view.set_top_margin(10)
    self.set_styles(self.text_view)

    self.widget.add(self.text_view)
    self.text_view.connect('key-release-event', self.key_pressed)
    self.text_view.connect('focus-out-event',self.write_to_tag)
    #self.text_view.connect('focus-in-event',self.open_keyboard_action)  #Use this action to open a keyboard if desired
    self.read_from_tag()
    
  def key_pressed(self, widget, key_event):
    self.write_to_tag()

  def set_text(self, text):

    try:
      buff = self.text_view.get_buffer()
      if not text:
        buff.set_text('')
      else:
        buff.set_text(text)
    except (ValueError, KeyError) as e:
      print("Textview set_text error: {}".format(e))
  
  def get_text(self):
    try:
      buff = self.text_view.get_buffer()
      start, end = buff.get_bounds()
      return buff.get_text(start, end, True)
    except (ValueError, KeyError) as e:
      print("Textview update_text error: {}".format(e))

  def set_from_file(self, path, *args):
    try:
      with open(path, "r") as fp:
        text = fp.read()
        self.set_text(text)
    except Exception as e:
      print("Error setting TextView from file: {}".format(e))
    self.write_to_tag()

  def save_to_file(self, fp, *args):
    try:
      tmp = os.path.splitext(fp)[-1].lower()
      if not tmp:
        filename_suffix = ".txt"
        fp=os.path.join(fp + "." + filename_suffix)
      f = open(fp, "w")
      f.write(self.get_text())
      f.close()
    except Exception as e:
      print("Error setting TextView from file: {}".format(e))

  def clear_text(self,*args):
    buff = self.text_view.get_buffer()
    buff.set_text("")
    self.write_to_tag()

  def toggle_disable(self,*args):
    self.textview.set_editable(not self.btn.get_sensitive())
  
  def open_keyboard_action(self,*args):
    pass
    #self.app.open_keypad(self.set_value, self,self.widget ,self.params,self.text_view.get_buffer())

  def write_to_tag(self, *args):
    if self.tag:
      self.write(self.tag, self.get_text())

  def read_from_tag(self, *args):
    if self.tag:
      result = self.read(self.tag)
      if type(result) != type(None) and "Value" in result:
        self.set_text(result["Value"])



  



