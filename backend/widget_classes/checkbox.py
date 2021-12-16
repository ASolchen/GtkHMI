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

class CheckBoxWidget(Widget):
  def build(self):
    rows = self.db_manager.get_rows("WidgetParams-check-box",
        ["ValueTag","OnChange","InitialTag"], "WidgetID", self.id)
    try:
      self.substitute_replacements(self.replacements, rows[0])
      self.value_tag = rows[0]["ValueTag"] #TODO remove from here and db
      self.on_change_cmd = rows[0]["OnChange"]
      self.initialTag = rows[0]["InitialTag"]
    except (IndexError, KeyError):
      event_msg = "CheckBoxWidget {} path lookup error".format(self.id)
      self.app.display_event(event_msg)

    self.widget =Gtk.ToggleButton(width_request=self.width, height_request=self.height)
    self.widget.connect("toggled", self.on_change)
    self.set_styles(self.widget)
    img = GdkPixbuf.Pixbuf.new_from_file_at_size('./Public/images/Check.png', self.width, self.height)
    self.img_checked = Gtk.Image.new_from_pixbuf(img)
    self.initial_val = ''
    self.set_initial_val()

  def class_update(self, factory, subscriber):
    if self.display != subscriber:
      return

  def set_initial_val(self,*args):
    expression_val = self.connection_manager.evaluate_expression(self, self.initialTag, self.display)
    if expression_val != None:
      self.initial_val = expression_val
      self.widget.set_active(bool(expression_val))
      if expression_val:
        self.widget.add(self.img_checked)
  
  def update_img(self,*args):
    temp = self.widget.get_children()
    for i in temp:
      self.widget.remove(i)
    if self.widget.get_active():
      self.widget.add(self.img_checked)
      self.widget.show_all()

  def on_change(self,*args):
    if self.builder_mode:
      return
    if not self.initial_val:  # prevents updating db with already saved Value
      self.update_img()
      self.run_cmd()
    self.initial_val = ''

  def return_status(self,*args):
    return self.widget.get_active()
  
  def run_cmd(self,*args):
    cmd = self.on_change_cmd
    if cmd:
      try:
        exec(cmd)
      except Exception as e:
        event_msg = 'Error on widget id "{}"\n\tCommand: {}\n\tError: {}'.format(self.id, cmd, e)
        self.app.display_event(event_msg)

  
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