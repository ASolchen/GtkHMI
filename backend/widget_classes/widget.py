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

import json , numbers, ast
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
import re
import time

"""
TODO
            compare all widget types for commonalities
            connection Modbus connection parameters to proper table
            use datatypes for Tags table and connections
            finish events writing to widget to fix busting out of thread (add signal to get it to write memory db)
DONE>>>>>>  add control for autoconnect option in communication driver
DONE>>>>>>  add popup from home icon button for zeroing or setting value (maybe just use calculator popup)
DONE>>>>>>  create event widget and way to pass internal alarms to it
DONE>>>>>>  add way to clear events out of table wiht buttons
DONE>>>>>>  update and store serial port settings to mill.db
DONE>>>>>>  pass in stored serial port to drop down and then update when a new one is selected use the one in the box to connect so need to pass it in
DONE>>>>>>  display saved serial port not just first item listed
DONE>>>>>>  add machine home button to AUX control box
DONE>>>>>>  add small num display for machine position display
            connect all of the widget tags to PLC / GRBL
            add hardcoded Modbus connection to PLC
            add code in PLC that when homing it disables end of travel drive disable
            add functionality to builder to be able to add rows to db
            have builder create /build the page requested to be able to move items around on screen
            add connections configuration screens to builder
            add communication tags / internal tags database with adding/removing items
DONE>>>>>>  verify window size 1280 x 720
DONE>>>>>>  create settings widget
DONE>>>>>>  widget state indications 
DONE>>>>>> 	state always an int
DONE>>>>>>  need z axis for putting buttons on top of each other
DONE>>>>>> 	when pulling from database return in order of z index to build one on top of other
DONE>>>>>>  remove bool indicator widget
DONE>>>>>>  remove toggle widget
DONE>>>>>>  remove indicator tag column from button
DONE>>>>>> 	Can do it with a box on top of a button
DONE>>>>>>  Remove all blink functions
DONE>>>>>>  remove gcode widget
DONE>>>>>>  create keyboard
DONE>>>>>>  create num pad popup
DONE>>>>>>  create string display
DONE>>>>>>  create string entry that pops up keyboard
DONE>>>>>>  update numeric display / numeric entry to account for number formatting
DONE>>>>>>  create save function for gcode textview
DONE>>>>>>  save textview when switching screens
DONE>>>>>>  move textview to separate popup
DONE>>>>>>  move all fonts to specific css pages
DONE>>>>>>  finish keyboard for typing on actual keyboard
DONE>>>>>>  move all colors to specific css pages
DONE>>>>>>  create triangle for invalid values / read on widget class
DONE>>>>>>  clean-up building children
DONE>>>>>>  add way to save com port selection to mill.db
DONE>>>>>>  create displays for alarm and events
DONE>>>>>>  create settings rows (treeview) for changing and updating settings (checkbox/entry) Have 5 buttons(open/save/send all/send one/refresh)
DONE>>>>>>  Discuss state indicator / label / string display widgets.  Which ones we need
DONE>>>>>>  add default controls to alarm_event widget
DONE>>>>>>  Finish connection tab so that it reads the available USB ports as well as shows a connection indicaiton
"""

class Widget(GObject.Object):
  base_parmas = ["ID","Description", "ParentID","X", "Y", "Width", "Height", "Class", "Styles", "GlobalReference", "BuildOrder"]
  class_params = {}
  
  def __init__(self, factory, parent, params):
    self.factory = factory
    self.app = factory.app
    self.connection_manager = factory.app.connection_manager
    self.db_manager = factory.db_manager
    self.builder_mode = factory.builder_mode
    self.animations = [] if not "Animations" in params else params["Animations"]
    self.states = [] if not "States" in params else params["States"]
    self.replacements = []
    if "Replacements" in params:
      self.replacements = params["Replacements"]
      if len(self.replacements):
        self.substitute_replacements(self.replacements, params)
        for animation in self.animations:
          self.substitute_replacements(self.replacements, animation)
    self.params = params
    self.display = params["Display"]
    self.tag_ids = {}
    self.signals = []
    self.x = self.params["X"]
    self.y = self.params["Y"]
    self.id = self.params["ID"]
    #add communication error widget from widget class to
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Warning.png', 40, -1, True) #creating communciation error indicator
    self.error_ind = Gtk.Image(pixbuf=p_buf)
    #self.error_ind = None
    self.expression_err = False
    self.global_reference = self.params["GlobalReference"]
    if not params["Styles"]:
      self.styles = []
    elif not "," in params["Styles"]:
      self.styles = [params["Styles"],]
    else:
      self.styles = params["Styles"].split(",")
    self.widget_class = None
    self.parent = parent
    self.width = self.params["Width"]
    self.height = self.params["Height"]
    self.widget_class = self.params["Class"]
    self.widget = None #this is the Gtk.Widget children are built on, overwrite in build meth of custom widget if needed
    self.widget_ids={} #used to ref IDs to Python classes of children
    self.signals.append(self.connection_manager.connect("tag_update", self.update)) #listen for tag updates
    self.polling = True
    self.build()
    self.attach_to_parent()
    self.build_children()
    self.count = 0
  
  def __repr__(self):
    return f'GTK HMI {self.__class__.__name__}(factory, parent, params)'

  def __str__(self):
    return f'GTK HMI {self.__class__.__name__}: {self.params.get("ID")}'

  def substitute_replacements(self, replacements, values):
    #pass in a dict to replace all strings in replacements
    #replacements is a list of dicts {"Name": "", "Value":""}
    for key, val in values.items():
      for replacement in replacements:
        if type(val) == type (u"") or type(val) == type (""):
          values[key] = values[key].replace("#{}#".format(replacement["Name"]), "{}".format(replacement["Value"]))

  
  def run_cmd(self, cmd):
    try:
      exec(cmd)
    except Exception as e:
      event_msg = 'Error on widget id "{}"\n\tCommand: {}\n\tError: {}'.format(self.id, cmd, e)
      self.app.display_event(event_msg)

  def kill_children(self, level=0):
    for signal in self.signals:
      self.connection_manager.disconnect(signal)
    self.signals = []
    level+=1
    children = list(self.widget_ids)
    for w_id in children:      
      self.widget_ids[w_id].kill_children(level)
      del(self.widget_ids[w_id])

  def animate(self, anim_type, val):
    #lookup animations
    if self.builder_mode:
      return
    if anim_type=="STATE":
      self.animate_state(val)
    elif type(val) == type(None):
      #For an invalid animation set the error indication flag
      self.expression_err = True
      #TODO show error for other animations?
      return
    if anim_type=="X":
      self.x = val + self.params["X"]
      self.parent.move(self.widget, self.x, self.y)
    if anim_type=="Y":
      self.y = val + self.params["Y"]
      self.parent.move(self.widget, self.x, self.y)
    if anim_type=="VIS":
      self.widget.set_property("visible", bool(val))
    if anim_type=="ENBL":
      self.widget.set_property("sensitive", bool(val))
    
  def animate_state(self, val):
    if self.builder_mode:
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
    if self.builder_mode:
      return
    self.parent.put(self.error_ind,self.x,self.y)

  def attach_to_parent(self):
    if not self.widget: # hasn't been set by custom widget class
      self.widget = Gtk.Fixed()
    if not self.widget_class: # base class, add style box
      style_box = Gtk.Box(width_request=self.width, height_request=self.height)
      sc = style_box.get_style_context()
      for style in self.styles:
        sc.add_class(style)
      self.widget.put(style_box, 0,0)
    self.parent.put(self.widget, self.x, self.y)
    self.add_error_ind()
    self.error_ind.set_property('visible',False)

  def build_children(self): #from the database
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
      child_params = self.db_manager.get_rows("Widgets", Widget.base_parmas, "ParentID", self.id, order_by="BuildOrder")
      for c_params in child_params:
        c_params["Animations"] = self.db_manager.get_rows("WidgetAnimations", ["Type","Expression"], "WidgetID", c_params["ID"])
        c_params["States"] = self.db_manager.get_rows("WidgetStateIndications", ["State","Caption","Style"], "WidgetID", c_params["ID"])
        c_params["Replacements"] = self.replacements #pass down existing replacements
        if c_params["GlobalReference"]: #this is a global, lookup and add replacements to existing ones
          global_replacements = self.db_manager.get_rows("GlobalObjectParameterValues",
          ["Name", "Value"], "WidgetID", c_params["ID"])
          c_params["Replacements"] = global_replacements + self.replacements[:]
          pass
    for params in child_params:
      #lookup params for base widget
      if params["GlobalReference"]: # this is a global,
        #lookup the global's params and swap out wildcards
        temp = {"ID": params["ID"], "ParentID": params["ParentID"], "Replacements": params["Replacements"],
                "X": params["X"], "Y":params["Y"], "GlobalReference": params["GlobalReference"],
                "Animations": params["Animations"],
                "States": params["States"],}#hold this widgets id and location
        params = self.db_manager.get_rows("Widgets", Widget.base_parmas, "ID", params["GlobalReference"])[0]
        params.update(temp)
      if params["Class"]: # custom widget
        w_class = self.factory.widget_types[params["Class"]]
      else: #base widget
        w_class = Widget
      params["Display"] = self.display #all widgets hold a ref to what display they are on
            
      self.widget_ids[params["ID"]] = w_class(self.factory, self.widget, params)

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
    if self.builder_mode:
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
    sc = self.widget.get_style_context()
    sc.add_class(style)

  def remove_style(self, style):
    sc = self.widget.get_style_context()
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
    result = False
    def point_inside(x,y,left,bottom,right,top):
      return (left<=x<=right) and (top<=y<=bottom)
    #check if self corners are in other rect 
    result |= point_inside(self.x, self.y, x,y+h,x+w,y) #self top left
    result |= point_inside(self.x, self.y+self.height, x,y+h,x+w,y) #self bottom left
    result |= point_inside(self.x+self.width, self.y+self.height, x,y+h,x+w,y) #self bottom right
    result |= point_inside(self.x+self.width, self.y, x,y+h,x+w,y) #self top right
    #check if new rect corners are in self rect
    result |= point_inside(x, y, self.x,self.y+self.height,self.x+self.width,self.y) #rect top left
    result |= point_inside(x, y+h,  self.x,self.y+self.height,self.x+self.width,self.y) #rect bottom left
    result |= point_inside(x+w, y+h, self.x,self.y+self.height,self.x+self.width,self.y) #rect bottom right
    result |= point_inside(x+w, y, self.x,self.y+self.height,self.x+self.width,self.y) #rect top right
    return result











        



