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
import gi, cairo
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
import re
import time

from backend.widget_classes.widget import Widget

class ButtonWidget(Widget):
  def build(self):
    rows = self.db_manager.get_rows("WidgetParams-ctrl-button",
    ["Label","Image","OnPress","OnRelease","Confirm_onpress_msg","Confirm_onrelease_msg"], "WidgetID", self.id)
    try:
      self.substitute_replacements(self.replacements, rows[0])
      self.label_text = rows[0]["Label"]
      self.image = rows[0]["Image"]
      self.on_press_cmd = rows[0]["OnPress"]
      self.on_release_cmd = rows[0]["OnRelease"]
      self.confirm_press_action_msg = rows[0]["Confirm_onpress_msg"]
      self.confirm_release_action_msg = rows[0]["Confirm_onrelease_msg"]
    except (IndexError, KeyError):
      event_msg = "ButtonWidget {} path lookup error".format(self.id)
      self.app.display_event(event_msg)
    self.btn_active = None
    self.widget = Gtk.Button(width_request=self.width, height_request=self.height)
    if self.label_text:
      self.widget.set_label(self.label_text)
    if self.image: #image on top of button
      img = GdkPixbuf.Pixbuf.new_from_file_at_size(self.image, self.width-20, self.height-20)
      image = Gtk.Image.new_from_pixbuf(img)
      #image = Gtk.Image(width_request=self.width-20, height_request=self.height-20)
      #image.set_from_file(self.image)
      self.widget.add(image)
    self.set_styles(self.widget)
    if not self.builder_mode:
      if self.on_press_cmd and not self.builder_mode:
        self.widget.connect("pressed",self.btn_press_action)
      if self.on_release_cmd  and not self.builder_mode:
        self.widget.connect("released",self.btn_release_action)

  def animate_state(self, val):
    #override this in child classes if needed
    for state in self.states:
      sc = self.widget.get_style_context()
      if type(val) != type(None): val = int(val)
      if val == state["State"]:
        sc.add_class(state["Style"])
        if state["Caption"]:
          self.widget.set_label(state["Caption"])
      else:
        sc.remove_class(state["Style"])

  def btn_press_action(self,*args):
    if self.confirm_press_action_msg:
      #Confirmation Type Button
      self.app.confirm(self.on_press_callback, self.confirm_press_action_msg)
    else:
      self.on_press_callback()
    
  def on_press_callback(self):
    exec(self.on_press_cmd)

    
  def btn_release_action(self,*args):
    if self.confirm_release_action_msg:
      #Confirmation Type Button
      self.app.confirm(self.on_release_callback,self.confirm_release_action_msg)
    else:
      self.on_release_callback()

  def on_release_callback(self):
    exec(self.on_release_cmd)
