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
from sqlalchemy.sql.expression import true
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf


class BuildMask(Gtk.EventBox):
  def __init__(self, widget):
    super().__init__(above_child=True)
    self.hmi_widget = widget    
    self.connect("button-release-event", self.mouse_up)
    self.builder = None
    self.build_mode_changed()


  
  def mouse_up(self, e_box, event):
    if not self.builder:
      return
    if self.hmi_widget.widget_class == "display" and not self.hmi_widget.overlay:
      self.builder.none_selected()
      return
    ctrl = bool(event.state & Gdk.ModifierType.CONTROL_MASK) #ctrl button held?
    if event.button == 1: # left click
      if ctrl:
        self.builder.append_selected(self.hmi_widget)
      else:
        self.builder.new_selected(self.hmi_widget)
    if event.button == 3:
      print(f"{self} right-click") 

  def build_mode_changed(self, *args):
    if self.hmi_widget.app.builder_mode and self.hmi_widget.app.builder:
      self.builder = self.hmi_widget.app.builder
    else:
      self.builder = None

  def select(self):
    self.override_background_color(Gtk.StateFlags.NORMAL, 
                                    Gdk.RGBA(1.0, 1.0, 0.0, 0.2))

  def deselect(self):
    self.override_background_color(Gtk.StateFlags.NORMAL, 
                                    Gdk.RGBA(0.0, 0.0, 0.0, 0.0))

