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
from backend.managers.database_models.widget_database import WidgetParamsControlButton

class ButtonWidget(Widget):
  orm_model = WidgetParamsControlButton
  @classmethod
  def get_params_from_orm(cls, result):
    params = {
      "label": result.label,
      "image": result.image,
      "on_press": result.on_press,
      "on_release": result.on_release,
      "confirm_on_press_msg": result.confirm_on_press_msg,
      "confirm_on_release_msg": result.confirm_on_release_msg,
    }
    return params

  @GObject.Property(type=str, flags=GObject.ParamFlags.READWRITE)
  def label(self):
    return self._label 
  @label.setter
  def label(self, value):
    self._label = value
    self.widget.set_property('label', value)

  @GObject.Property(type=str, flags=GObject.ParamFlags.READWRITE)
  def image(self):
    return self._image 
  @image.setter
  def image(self, value):
    self._image = value
    for c in self.widget.get_children():
      self.widget.remove(c)
    if value:
      img = GdkPixbuf.Pixbuf.new_from_file_at_size(self.image, self.width-20, self.height-20)
      image = Gtk.Image.new_from_pixbuf(img)
      self.widget.add(image)
      self.widget.show_all()

  @GObject.Property(type=str, flags=GObject.ParamFlags.READWRITE)
  def on_press(self):
    return self._on_press 
  @on_press.setter
  def on_press(self, value):
    self._on_press = value

  @GObject.Property(type=str, flags=GObject.ParamFlags.READWRITE)
  def on_release(self):
    return self._on_release 
  @on_release.setter
  def on_release(self, value):
    self._on_release = value

  @GObject.Property(type=str, flags=GObject.ParamFlags.READWRITE)
  def confirm_on_press_msg(self):
    return self._confirm_on_press_msg 
  @confirm_on_press_msg.setter
  def confirm_on_press_msg(self, value):
    self._confirm_on_press_msg = value

  @GObject.Property(type=str, flags=GObject.ParamFlags.READWRITE)
  def confirm_on_release_msg(self):
    return self._confirm_on_release_msg 
  @confirm_on_release_msg.setter
  def confirm_on_release_msg(self, value):
    self._confirm_on_release_msg = value

  def __init__(self, factory, params):
    self.widget = Gtk.Button()
    super(ButtonWidget, self).__init__(factory, params)
    self.resize()
    self.on_press= params['on_press']
    self.on_release = params['on_release']
    self.confirm_on_press_msg = params['confirm_on_press_msg']
    self.confirm_on_release_msg = params['confirm_on_release_msg']
    self.label = '' if not params.get("label") else params['label']
    self.btn_active = None      
    self.widget.connect("pressed",self.btn_press_action)
    self.widget.connect("released",self.btn_release_action)
    self.set_styles(self.widget)

  def animate_state(self, val):
    #override this in child classes if needed
    for state in self.states:
      sc = self.widget.get_style_context()
      if type(val) != type(None): val = int(val)
      if val == state["State"]:
        sc.add_class(state["Style"])
        if state["Caption"]:
          self.label = state["Caption"]
      else:
        sc.remove_class(state["Style"])

  def btn_press_action(self,*args):
    if self.confirm_on_press_msg:
      #Confirmation Type Button
      self.app.confirm(self.on_press_callback, self.confirm_on_press_msg)
    else:
      self.on_press_callback()
    
  def on_press_callback(self):
    exec(self.on_press)

    
  def btn_release_action(self,*args):
    if self.confirm_on_release_msg:
      #Confirmation Type Button
      self.app.confirm(self.on_release_callback,self.confirm_on_release_msg)
    else:
      self.on_release_callback()

  def on_release_callback(self):
    exec(self.on_release)
