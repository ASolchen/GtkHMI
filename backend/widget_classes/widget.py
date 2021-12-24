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

import ast
import json
import numbers

import gi

gi.require_version('Gtk', '3.0')
import re
import time

from backend.exceptions import GtkHmiError, WidgetParamsError
from backend.managers.database_models.widget_database import WidgetParams
from gi.repository import Gdk, GdkPixbuf, GObject, Gtk


class Widget(GObject.Object):
  orm_model = WidgetParams
  @classmethod
  def get_params_from_orm(cls, result):
    """
    pass in an orm result (database query result) and this will update the params dictionary
    with the table columns. the params object is used to pass into a widget's init
    
    """
    params = {
    "id": result.id,
    "x": result.x,
    "y": result.y,
    "width": result.width,
    "height": result.height,
    "widget_class": result.widget_class,
    "parent_id": result.parent_id,
    "global_reference": result.global_reference,
    "build_order": result.build_order
    }
    return params

  @GObject.Property(type=int, flags=GObject.ParamFlags.READABLE)
  def id(self):
    return self._id 
  @GObject.Property(type=int, flags=GObject.ParamFlags.READWRITE)
  def x(self):
    return self._x  
  @x.setter
  def x(self, value):
    self._x = value
    self.move()
  @GObject.Property(type=int, flags=GObject.ParamFlags.READWRITE)
  def y(self):
    return self._y  
  @y.setter
  def y(self, value):
    self._y = value
    self.move()
  @GObject.Property(type=int, flags=GObject.ParamFlags.READWRITE)
  def width(self):
    return self._width  
  @width.setter
  def width(self, value):
    self._width = value
    self.resize()
  @GObject.Property(type=int, flags=GObject.ParamFlags.READWRITE)
  def height(self):
    return self._height  
  @height.setter
  def height(self, value):
    self._height = value
    self.resize()
  @GObject.Property(type=int, flags=GObject.ParamFlags.READWRITE)
  def build_order(self):
    return self._build_order  
  @build_order.setter
  def build_order(self, value):
    self._build_order = value
    #self.parent.rebuild_children()
  @GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
  def widget_class(self):
    return self._widget_class 
  @GObject.Property(type=bool, default=False, flags=GObject.ParamFlags.READABLE)
  def global_reference(self):
    return self._global_reference


  def __init__(self, factory, params):
    GObject.Object.__init__(self)
    if not hasattr(self, "widget"): # hasn't been set by custom widget class
      self.widget = Gtk.Fixed()
    #private props
    self._id = params['id'] #read-only
    self._global_reference = params['global_reference'] #read-only
    self.parent = params['parent'] #parent widget's layout object. This is what this widget's layout is attached to
    self._build_order = 0
    self._x= 0
    self._y= 0
    self._width = 100
    self._height = 100
    self.factory = factory
    self.app = factory.app
    self.params = params.copy()
    self._builder_mode = self.app.builder_mode
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Warning.png', 40, -1, True) #creating communciation error indicator
    self.error_ind = Gtk.Image(pixbuf=p_buf)
    self.layout = Gtk.Fixed()
    self.content = Gtk.Overlay()
    self.layout.put(self.content, 0,0)
    self.builder_mask = Gtk.EventBox(above_child=True)
    colors = [Gdk.RGBA(1.0, 0.0, 0.0, 0.2),
              Gdk.RGBA(0.0, 1.0, 0.0, 0.2),
              Gdk.RGBA(0.0, 0.0, 1.0, 0.2),
              Gdk.RGBA(1.0, 1.0, 1.0, 0.2),
              Gdk.RGBA(1.0, 0.0, 1.0, 0.2)]
    self.builder_mask.override_background_color(Gtk.StateFlags.NORMAL, colors[params['id']-1])
    self.builder_mask.connect("button-release-event", self.mouse_up)
    self.content.add(self.widget)
    self.signals = [(self.app, self.app.connect("notify::builder-mode", self.initialize_params)),]
    self.connection_manager = factory.app.connection_manager
    self.db_session = factory.project_db.session
    self.tag_ids = {} #TODO < see if this is used
    self.initialize_params()
    #add communication error widget from widget class to
    #self.error_ind = None
    

    self.widget_ids={} #used to ref IDs to Python classes of children
    self.signals.append((self.connection_manager, self.connection_manager.connect("tag_update", self.update))) #listen for tag updates
    self.polling = True
    self.attach_to_parent()
    self.build_children()
    self.count = 0
  
  def __repr__(self):
    return f'GTK HMI {self.__class__.__name__}'

  def __str__(self):
    return f'GTK HMI {self.__class__.__name__}: {self.id}'

  def move(self):
    if self.layout in self.parent.get_children():
      self.parent.move(self.layout, self.x, self.y)
  
  def resize(self):
    self.content.set_property("width_request", self.width)
    self.content.set_property("height_request", self.height)

  def mouse_up(self, e_box, event):
    if event.button == 1:
      print(f"{self} left-click")  
    if event.button == 3:
      print(f"{self} right-click")  


  def initialize_params(self, *args):
    self.animations = []
    self.states = []
    #self.builder_mask.set_property("visible", self.app.builder_mode)
    if not self.app.builder_mode:
      if self.builder_mask in self.content.get_children():
        self.content.remove(self.builder_mask)
      replacements = self.params.get('replacements')
      if replacements:
        self.substitute_replacements(replacements, self.params)
      self.animations = [] if not self.params.get("animations") else self.params.get("animations")
      self.states = [] if not not self.params.get("states") else self.params.get("states")
      # subscribe to tags here
    else:
      self.error_ind.set_property('visible', False)
      if not self.builder_mask in self.content.get_children():
        self.content.add_overlay(self.builder_mask)
        self.content.show_all()
    #private settings
    try:
      self.x= self.params['x']
      self.y= self.params['y']
      self.width = self.params['width']
      self.height = self.params['height']
      self.build_order = 0 if self.params['build_order']==None else self.params['build_order']
    except KeyError as e:
      raise WidgetParamsError(f"Widget initialization failed to find key:{e} in parameters. Parameters: {self.params}")
    self.expression_err = False    
    self.styles = [] if not self.params.get("styles") else self.params.get("styles")
    self._widget_class = self.params.get("widget_class")
    self._global_reference=(self.params.get("global_reference") and self.params["global_reference"])\
                       or (self.parent and hasattr(self.parent, "global_reference") and self.parent.global_reference)
    self.layout.show_all()

  def substitute_replacements(self, replacements, params):
    #pass in a dict to replace all strings in replacements
    #replacements is a list of dicts [{"name": "MOTOR_TAG", "value":"Motor01"},]
    #only try on string types
    for key, val in params.items():
      for replacement in replacements:
        if type(val) == type (u"") or type(val) == type (""):
          params[key] = params[key].replace("#{}#".format(replacement["name"]), "{}".format(replacement["value"]))
      self.replacements = params["replacements"]

  
  def run_cmd(self, cmd):
    try:
      exec(cmd)
    except Exception as e:
      event_msg = 'Error on widget id "{}"\n\tCommand: {}\n\tError: {}'.format(self.id, cmd, e)
      self.app.display_event(event_msg)

  def kill_children(self, level=0):
    """
    disconnects all signals of this widget and all of its children
    removes visual widget and childrens widgets
    this object cannot delete itself so parent of this also needs to del(this_object)
    e.g.
    self.ids['78'].kill_children()
    del(self.ids['78']) 
    """
    for gobject, signal in self.signals:
      gobject.disconnect(signal)
    self.signals = []
    level+=1
    children = list(self.widget_ids)
    for w_id in children:      
      self.widget_ids[w_id].kill_children(level)
      self.widget_ids[w_id].parent.remove(self.widget_ids[w_id].widget)
      del(self.widget_ids[w_id])


  def animate(self, anim_type, val):
    #lookup animations
    if self.app.builder_mode:
      return
    if anim_type=="STATE":
      self.animate_state(val)
    elif type(val) == type(None):
      #For an invalid animation set the error indication flag
      self.expression_err = True
      #TODO show error for other animations?
      return
    if anim_type=="X":
      self.x = val
    if anim_type=="Y":
      self.y = val
    if anim_type=="VIS":
      self.layout.set_property("visible", bool(val))
    if anim_type=="ENBL":
      self.layout.set_property("sensitive", bool(val))
    
  def animate_state(self, val):
    if self.app.builder_mode:
      return
    #override this in child classes if needed
    for state in self.states:
      if state["Style"]:
        if type(val) != type(None): 
          val = int(val)
        if val == state["State"]:
          self.add_style(state["Style"])
        else:
          self.remove_style(state["Style"])
  
  def build(self):
    pass
  
  def set_styles(self,wid):
    sc = wid.get_style_context()
    for items in sc.list_classes():
      #remove all default styles
      sc.remove_class(items)
    for style in self.styles:
      sc.add_class(style)
    if not self.styles:
      #If no styles used, apply default class style
      sc.add_class(self.widget_class)

  def add_error_ind(self):
    #add communication / expression error to each widget if it exists
    if self.app.builder_mode:
      return
    self.parent.put(self.error_ind,self.x,self.y)

  def attach_to_parent(self):
    if not self.widget_class: # base class, add style box
      style_box = Gtk.Box(width_request=self.width, height_request=self.height)
      sc = style_box.get_style_context()
      for style in self.styles:
        sc.add_class(style)
      self.layout.put(style_box, 0,0)
    self.parent.put(self.layout, self.x, self.y)
    self.add_error_ind()
    self.error_ind.set_property('visible',False)

  def build_children(self): #from the database
    params = {}
    if self.global_reference:
      #get the child params of the globals children.
      child_params = self.db_manager.get_rows("Widgets", Widget.base_parmas, "ParentID", self.global_reference, order_by="BuildOrder")
      for c_params in child_params:
        c_params["Replacements"] = self.replacements #this is a decendadant of a global, add replacements
        c_params["Animations"] = self.db_manager.get_rows("WidgetAnimations", ["Type","Expression"], "WidgetID", c_params["ID"])
        c_params["States"] = self.db_manager.get_rows("WidgetStateIndications", ["State","Caption","Style"], "WidgetID", c_params["ID"])
        c_params["GlobalReference"] = c_params["ID"]
        #c_params["ID"] = "{}.{}".format(self.id, c_params["ID"])
    else:
      w_type = Widget
      child_ids = self.db_session.query(w_type.orm_model)\
      .filter(w_type.orm_model.parent_id == self.id)\
      .all()
      for res in child_ids:
        params = None
        w_type = Widget
        base_res = self.db_session.query(w_type.orm_model)\
          .filter(w_type.orm_model.id == res.id)\
          .first()
        params = w_type.get_params_from_orm(base_res)
        if params.get("widget_class") and params["widget_class"] in self.factory.widget_types:
          #look up advanced params
          w_type = self.factory.widget_types[params["widget_class"]]
          class_res = self.db_session.query(w_type.orm_model)\
          .filter(w_type.orm_model.id == res.id)\
          .first()
          if not class_res:
            w_type = None
            raise Exception(f"Misconfigured database, widget id:{res.id} missing config for class params")
          else:
            params.update(w_type.get_params_from_orm(class_res))
        if w_type:
          params["parent"] = self.layout
          self.widget_ids[params["id"]] = self.factory.create_widget(w_type, params)

  def get_widget_by_id(self, id_string):
    if id_string == self.id:
      return self #it's me
    if id_string in self.widget_ids:
      return self.widget_ids[id_string] #it's one of my children 
    if "." in id_string:
      elements = id_string.split(".")
      if not (elements[0] == self.id) or not (elements[1] in self.widget_ids):
        return None #it wasn't for any of my children
      return self.widget_ids[elements[1]].get_widget_by_id(".".join(elements[1:])) # pop off my id and send it to the child references
    return None

  def update(self, factory, subscriber):
    self.expression_err = False #reset and recheck for error
    if self.app.builder_mode:
      return
    #run aninimations for base widgets
    base_animations = {"Visibility": None, "Enable": None, "PositionX": None, "PositionY": None, "State":None}
    #search for and add only the last one found. (Should we warn of multiple?)
    for an_type in base_animations:
      for animation in self.animations:
        if animation["Type"] == an_type:
          base_animations[an_type] = animation["Expression"]
    visible = True #if there is no animation that says otherwise
    if type(base_animations["Visibility"]) != type(None):
      val = self.connection_manager.evaluate_expression(self, base_animations["Visibility"], self.display, return_type="BOOL")
      self.animate("VIS", val)
      visible = bool(val)
    if visible and type(base_animations["Enable"]) != type(None):
      self.animate("ENBL", self.connection_manager.evaluate_expression(self, base_animations["Enable"], self.display, return_type="BOOL"))
    if visible and  type(base_animations["PositionX"]) != type(None):
      self.animate("X", self.connection_manager.evaluate_expression(self, base_animations["PositionX"], self.display, return_type="INT"))
    if visible and  type(base_animations["PositionY"]) != type(None):
      self.animate("Y", self.connection_manager.evaluate_expression(self, base_animations["PositionY"], self.display, return_type="INT"))
    if  visible and type(base_animations["State"]) != type(None):
      self.animate("STATE", self.connection_manager.evaluate_expression(self, base_animations["State"], self.display, return_type="INT"))
    if visible:
      self.class_update(factory, subscriber)
    self.error_ind.set_property('visible', self.expression_err)

  def class_update(self, factory, subscriber):
    pass

  def subscribe(self, tags):
    self.factory.db_manager.add_subscription(tags)

  def add_style(self, style):
    sc = self.layout.get_style_context()
    sc.add_class(style)

  def remove_style(self, style):
    sc = self.layout.get_style_context()
    sc.remove_class(style)
  
  def write(self, tag, val):
    tag = tag.replace("{","").replace("}","") # remove the curley braces
    self.app.connection_manager.write(tag, val)
  
  def read(self, tag):
    conx = re.findall("\[[a-zA-Z0-9_]+\]", tag)
    if len(conx):
      tag = tag.replace(conx[0], "")
    res = self.app.connection_manager.read_once([tag])
    return res[tag]['Value']
    
  def intersect(self, x, y, w, h):
    #checks if any point of a rectangle of self insects with any point of a new rectagle (widget)
    rect = Gdk.Rectangle(height=h, width=w, x=x, y=y)
    return rect.intersect(self.get_allocated())











        



