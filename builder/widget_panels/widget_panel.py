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

import gi, os, json
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
from backend.widget_classes.factory import WidgetFactory, WIDGET_TYPES
from backend.widget_classes.widget import Widget




class BuilderToolsWidget(Gtk.Box):
  def __init__(self, app, row):
    super(BuilderToolsWidget, self).__init__()
    self.row = row
    self.app = app
    self.set_property("orientation", Gtk.Orientation.VERTICAL)
    self.set_property("spacing", 10)
    self.build_settings_panel()

  def build_settings_panel(self):
    db_row=self.row

    label = Gtk.Label("Basic Settings")  
    #row 1
    row = 0
    grid = Gtk.Grid(column_spacing=4, row_spacing=4)
    self.pack_start(grid, 0, 0, 0)
    grid.attach(Gtk.Label("ID", width_request=50), 0, row, 1, 1)
    self.id_entry = Gtk.Entry(text=db_row["ID"])
    grid.attach(self.id_entry, 1,row, 3,1)

    #row2
    row+=1
    grid.attach(Gtk.Label("Class", width_request=50), 0, row, 1,1)
    self.class_combo = Gtk.ComboBoxText()
    self.class_combo.append("None", "Group (Base)")
    for w in WIDGET_TYPES:
      self.class_combo.append(w, w)
    if db_row["Class"] in WIDGET_TYPES:
      active = db_row["Class"]
    else:
      active = "None"
    self.class_combo.set_active_id(active)
    grid.attach(self.class_combo, 1,row, 3,1)
    #row 3
    row+=1
    grid.attach(Gtk.Label("Description", width_request=50), 0,row, 1,1)
    self.description_entry = Gtk.Entry(text=db_row["Description"])
    grid.attach(self.description_entry, 1,row, 3,1)
    #row 4
    row+=1
    db_row["X"] = db_row["X"] if db_row["X"] else 0
    grid.attach(Gtk.Label("X", width_request=50), 0, row, 1,1)
    self.x_spin = Gtk.SpinButton(adjustment=Gtk.Adjustment(0, 0, 5000, 1, 10, 0), numeric=True, width_request=150)
    self.x_spin.set_value(db_row["X"])
    grid.attach(self.x_spin, 1,row, 1,1)
    
    db_row["Y"] = db_row["Y"] if db_row["Y"] else 0
    grid.attach(Gtk.Label("Y", width_request=50), 2,row, 1,1)
    self.y_spin = Gtk.SpinButton(adjustment=Gtk.Adjustment(0, 0, 5000, 1, 10, 0), numeric=True, width_request=150)
    self.y_spin.set_value(db_row["Y"])
    grid.attach(self.y_spin, 3,row, 1,1)
    #row 5
    row+=1    
    db_row["Width"] = db_row["Width"] if db_row["Width"] else 1
    grid.attach(Gtk.Label("Width", width_request=50), 0, row, 1, 1)
    self.width_spin = Gtk.SpinButton(adjustment=Gtk.Adjustment(0, 1, 5000, 1, 10, 0), numeric=True, width_request=150)
    self.width_spin.set_value(db_row["Width"])
    grid.attach(self.width_spin, 1, row, 1, 1)
    db_row["Height"] = db_row["Height"] if db_row["Height"] else 1
    grid.attach(Gtk.Label("Height", width_request=50), 2, row, 1, 1)
    self.height_spin = Gtk.SpinButton(adjustment=Gtk.Adjustment(0, 1, 5000, 1, 10, 0), numeric=True, width_request=150)
    self.height_spin.set_value(db_row["Height"])
    grid.attach(self.height_spin, 3, row, 1, 1)
    #row 6
    row+=1
    grid.attach(Gtk.Label("Styles"), 0, row, 1, 1)
    db_row["Styles"] = db_row["Styles"] if db_row["Styles"] else ""
    self.style_entry = Gtk.Entry(text=db_row["Styles"])
    grid.attach(self.style_entry, 1, row, 3, 1)
    #row 7
    row+=1
    grid.attach(Gtk.Label("Parent"), 0, row, 1, 1)
    db_row["ParentID"] = db_row["ParentID"] if db_row["ParentID"] else ""
    self.parent_entry = Gtk.Entry(text=db_row["ParentID"])
    grid.attach(self.parent_entry, 1, row, 3, 1)
    #row 8
    row+=1 
    grid.attach(Gtk.Label("Global Reference"), 0, row, 1, 1)
    db_row["GlobalReference"] = db_row["GlobalReference"] if db_row["GlobalReference"] else ""
    self.global_ref_entry = Gtk.Entry(text=db_row["GlobalReference"])
    grid.attach(self.global_ref_entry, 1, row, 3, 1)
    #row 9
    row+=1
    grid.attach(Gtk.Label("BuildOrder", width_request=50), 0, row, 1, 1)
    self.build_order_spin = Gtk.SpinButton(adjustment=Gtk.Adjustment(0, 0, 5000, 1, 10, 0), numeric=True, width_request=150)
    if db_row["BuildOrder"]:
      self.build_order_spin.set_value(db_row["BuildOrder"])
    grid.attach(self.build_order_spin, 1, row, 1, 1)
    grid.attach(Gtk.Label("(Zero means ignore)"), 2, row, 2, 1)
    #row 10
    row+=1
    btn = Gtk.Button("Update")
    btn.connect("clicked", self.get_params)
    grid.attach(btn, 0, row, 1, 1)
    self.debug_area = Gtk.TextView(height_request=100, width_request=300)
    self.debug_area.set_wrap_mode(Gtk.WrapMode.WORD)
    grid.attach(self.debug_area, 1, row, 3, 3)


  def get_params(self, *args):
    p_list =  ["ID", "ParentID", "X", "Y", "Width", "Height",
    "Class", "Description", "Styles", "GlobalReference", "BuildOrder"]
    parmas = {}
    for p in p_list:
      parmas[p] = None
    parmas["ID"] = self.id_entry.get_text()
    parmas["ParentID"] = self.parent_entry.get_text()
    if not len(parmas["ParentID"]):#make NULL if blank
      parmas["ParentID"] = ''
    parmas["X"] = self.x_spin.get_value_as_int()
    parmas["Y"] = self.y_spin.get_value_as_int()
    parmas["Width"] = self.width_spin.get_value_as_int()
    parmas["Height"] = self.height_spin.get_value_as_int()
    parmas["Class"] = self.class_combo.get_active_text()
    if parmas["Class"] == "Group (Base)":
      parmas["Class"] = ''
    parmas["Description"] = self.description_entry.get_text()
    parmas["Styles"] = self.style_entry.get_text()
    parmas["GlobalReference"] = self.global_ref_entry.get_text()
    if not len(parmas["GlobalReference"]): #make NULL if blank
      parmas["GlobalReference"] = ''
    parmas["BuildOrder"] = self.build_order_spin.get_value_as_int()
    if not parmas["BuildOrder"]: #not zero
      parmas["BuildOrder"] = ''
    self.app.save_widget_base(parmas)
    buff = self.debug_area.get_buffer()
    buff.set_text("Set db with :{}".format(parmas))
    

class AdvancedBuilderToolsWidget(Gtk.Box):
  def __init__(self, app, row):
    super(AdvancedBuilderToolsWidget, self).__init__()
    self.row = row
    self.app = app
    self.db_manager = app.db_manager
    self.set_property("orientation", Gtk.Orientation.VERTICAL)
    self.set_property("spacing", 10)
    self.build_settings_panel()
    properties = self.db_manager.get_rows("WidgetPropertyBuilder", ["BuildIt"])
    for p in range(len(properties)):
      print(type(properties[p]["BuildIt"]),properties[p]["BuildIt"])
      res = json.loads(properties[p]["BuildIt"])
      print(type(res),res)

  def build_settings_panel(self):
    db_row=self.row
    if db_row["Class"] != '':
      widget_class = "WidgetParams-"+db_row["Class"]
      #advanaced_props = self.db_manager.get_rows(widget_class)
      row = self.db_manager.get_row_by_id(widget_class, "WidgetID", db_row["ID"])
      if len(row) != 0:
        print('Whose Row',row)
      else:
        print('No Advanced Properties')
    else:
      print('No Advanced Properties')

    label = Gtk.Label("Advanced Settings")  
    #row 1
    row = 0
    grid = Gtk.Grid(column_spacing=4, row_spacing=4)
    self.pack_start(grid, 0, 0, 0)
    grid.attach(Gtk.Label("ID", width_request=50), 0, row, 1, 1)
    self.id_entry = Gtk.Entry(text=db_row["ID"])
    grid.attach(self.id_entry, 1,row, 3,1)
    


