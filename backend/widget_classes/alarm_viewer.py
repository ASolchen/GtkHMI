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
import gi, os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
import re
import time, datetime

from backend.widget_classes.widget import Widget


class AlarmViewWidget(Widget):
  
  def build(self):
    rows = self.db_manager.get_rows("WidgetParams-alarm-config",
    ["ValueTag","EnableExpression","CtrlBtnstyle"], "WidgetID", self.id)
    try:
      self.expression = rows[0]["EnableExpression"]
      if not rows[0]["CtrlBtnstyle"]:
        self.ctrl_btn_style = []
      elif not "," in rows[0]["CtrlBtnstyle"]:
        self.ctrl_btn_style = [rows[0]["CtrlBtnstyle"],]
      else:
        self.ctrl_btn_style = rows[0]["CtrlBtnstyle"].split(",")
    except (IndexError, KeyError):
      event_msg = "Settings Configuration {} path lookup error".format(self.id)
      self.app.display_event(event_msg)
    self.widget = Gtk.Box(width_request=self.width,
    height_request=self.height, orientation=Gtk.Orientation.VERTICAL)
    lbl = Gtk.Label("Alarm Summary")
    self.widget.pack_start(lbl,0,0,10)
    self.btn_box = Gtk.Box(width_request=self.width,height_request=50, orientation=Gtk.Orientation.HORIZONTAL)
    ctrl_btns_names = ['ACK','ACK ALL','EXPORT']
    self.ctrl_btns = {} #hold reference to control buttons
    for item in ctrl_btns_names:
      btn = Gtk.Button(width_request=100,height_request=50, label = item)
      self.btn_box.pack_start(btn,False,True,10)
      btn.connect("pressed",self.button_pressed,item)
      self.ctrl_btns[item] = btn  #hold reference to control buttons
      sc = btn.get_style_context()
      for sty in self.ctrl_btn_style:
        sc.add_class(sty)

    self.widget.pack_start(self.btn_box,False,False,2)
    self.cols = ["ID","Message","Severity","State","EventOnTimestamp","EventOffTimestamp","AckState","AckTimestamp"]
    
    #for displays only rows = self.db_manager.get_rows("Widgets", cols, match_col="Class", match="display", order_by="ID")
    self.alm_list = Gtk.ListStore(int, str,int,int,str,str,int,str)
    #self.alm_list.set_sort_func(0, compare, None)    ##allows for a custom sort function to be called "compare"
    self.alm_tree = Gtk.TreeView(self.alm_list) # put the list in the Treeview
    self.alm_tree.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
    for i, col_title in enumerate(self.cols):
      renderer = Gtk.CellRendererText()
      if i: # to hide the ID column
        #create column
        col = Gtk.TreeViewColumn(col_title, renderer, text=i)
        col.set_sort_column_id(i)
        self.alm_tree.append_column(col)
    self.alm_tree.connect("button_press_event", self.alm_clicked)
    #add to window
    scroll = Gtk.ScrolledWindow()
    scroll.set_margin_left(10)
    scroll.set_margin_right(10)
    scroll.add(self.alm_tree)
    self.widget.pack_start(scroll,1,1,10)
    sc = self.widget.get_style_context()
    sc_tree = self.widget.get_style_context()
    sc.add_class(self.widget_class)
    for style in self.styles:
        sc.add_class(style)
        sc_tree.add_class(style)
    sc = lbl.get_style_context()
    sc.add_class('font-24') #Sets the alarm sumary header text size only
    self.class_update(self.factory, "__ALARM_AND_EVENT_HANDLER__") #trigger an initial read

  def class_update(self, factory, subscriber):
    if subscriber != "__ALARM_AND_EVENT_HANDLER__":
      return
    rows = self.db_manager.run_query(
      'SELECT {} FROM [AlarmsEvents] WHERE [State] = 1 AND [Severity] > 100 ORDER BY [EventOnTimestamp] DESC;'.format(", ".join(self.cols)))
    self.alm_list.clear()
    #add new alarms
    for row in rows:
      l = [int(row[0]), row[1], row[2], row[3], self.format_ts(row[4]), self.format_ts(row[5]), row[6], self.format_ts(row[7])]
      self.alm_list.append(l)
    if self.expression != None:
      self.enable_ctrl_btns(self.connection_manager.evaluate_expression(self,self.expression,self.display,str))

  def button_pressed(self,widget,name,*args):
    if name == 'EXPORT':
      self.app.save_file(self.export_alm_events,file_hint=None,filter_pattern = [])
    elif name == 'ACK ALL':
      rows = self.db_manager.ack_all_events()
    elif name == 'ACK':
      #check if any row selected
      selection = self.alm_tree.get_selection()
      model,pathlist = selection.get_selected_rows()
      if pathlist !=None:
        for path in pathlist :
            tree_iter = model.get_iter(path)
            ID = model.get_value(tree_iter,0)
            rows = self.db_manager.ack_sel_events(ID)
    self.class_update(self.factory, "__ALARM_AND_EVENT_HANDLER__") #update items displayed
  
  def alm_clicked(self, treeview,event,*args):
    if event.button == 1: #left click
      pthinfo = treeview.get_path_at_pos(event.x, event.y)
      if pthinfo != None:
        path,col,cellx,celly = pthinfo
        treeview.grab_focus()
        treeview.set_cursor(path,col,0)
    
  def format_ts(self, ts):
    if not ts:
      return("N/A")
    return "{}.{}".format(str(datetime.datetime(*time.localtime(ts)[:7]))[:19], str(ts%1.0)[2:5])
  
  def export_alm_events(self, fp, *args):
    rows = self.db_manager.run_query(
      'SELECT {} FROM [AlarmsEvents] WHERE [State] = 1 AND [Severity] > 100 ORDER BY [EventOnTimestamp] DESC;'.format(", ".join(self.cols)))
    try:
      tmp = os.path.splitext(fp)[-1].lower()
      if not tmp:
        filename_suffix = ".txt"
        fp=os.path.join(fp + "." + filename_suffix)
      f = open(fp, "w")
      for item in self.cols:
        f.write(item + ',')
      f.write("\n")
      for row in rows:
        for item in row:
          f.write(str(item) + ',')
        f.write("\n")
      f.close()
    except Exception as e:
      event_msg = "Error setting TextView from file: {}".format(e)
      self.app.display_event(event_msg)

  def enable_ctrl_btns(self,en,*args):
    for key in self.ctrl_btns:
      self.ctrl_btns[key].set_sensitive(en)
  