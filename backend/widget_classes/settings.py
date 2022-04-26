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


class SettingsWidget(Widget):
    
    def build(self):
        rows = self.db_manager.get_rows("WidgetParams-settings-config",
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
        lbl = Gtk.Label("System Settings")
        self.widget.pack_start(lbl,0,0,10)
        self.btn_box = Gtk.Box(width_request=self.width,height_request=50, orientation=Gtk.Orientation.HORIZONTAL)
        self.ctrl_btns = {} #hold reference to control buttons
        ctrl_btns_names = ['SEND','SEND ALL','SAVE NEW','SAVE CURRENT','EXPORT','STORE','REFRESH']
        for item in ctrl_btns_names:
            btn = Gtk.Button(width_request=100,height_request=50, label = item)
            self.btn_box.pack_start(btn,False,True,10)
            btn.connect("pressed",self.button_pressed,item)
            self.ctrl_btns[item] = btn    #hold reference to control buttons
            sc = btn.get_style_context()
            for sty in self.ctrl_btn_style:
                sc.add_class(sty)
        self.widget.pack_start(self.btn_box,False,False,2)
        
        #get db headers
        head = self.db_manager.run_query('SELECT * FROM [Tags-SettingsWidget] LIMIT 1') #only need one to get the header
        self.all_cols = head[0].keys()
        #find index value of certain columns in list
        self.newValue_pos = self.all_cols.index('NewValue')
        self.saveValue_pos = self.all_cols.index('SavedValue')
        self.currentValue_pos = self.all_cols.index('CurrentValue')
        self.total_cols = len(self.all_cols)

        self.cols = ["Description","SavedValue","NewValue","CurrentValue","ValMin","ValMax"]
        #['ID', 'Use', 'ReadWrite', 'ValueTag', 'ConnectionID', 'Description', 'DataType', 'SavedValue', 'NewValue', 'Timestamp', 'DefaultValue', 'CurrentValue' , 'ValMin', 'ValMax', 'Units','Label',forground_color','background_color']
        self.settings_list = Gtk.ListStore(str,bool,bool,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str)
        #self.settings_list.set_sort_func(0, compare, None)        ##allows for a custom sort function to be called "compare"
        self.settings_tree = Gtk.TreeView(self.settings_list) # put the list in the Treeview
        self.settings_tree.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        self.iter_keys = {} #stores the iter for each row by its tagname, need to rebuild anytime rows are added or removed

        for i, col_title in enumerate(self.all_cols):
            renderer = Gtk.CellRendererText()
            toggle_renderer = Gtk.CellRendererToggle()
            if i == 8:
                renderer.connect("edited", self.text_edited)
                col = Gtk.TreeViewColumn(col_title, renderer, text=i,editable = 2,background = (self.total_cols),foreground = (self.total_cols+1)    )
            else:
                col = Gtk.TreeViewColumn(col_title, renderer, text=i)    
                
            if col_title != "Description":
                renderer.set_property("xalign",0.5)     #sets column data to center
            ##Hides all non used columns
            if col_title not in self.cols:
                col.set_property("visible",False)
            
            col.set_property("expand",True)                 #allows columns to expand to proper size to fill space
            col.set_alignment(xalign=0.5)                     #Align header text to center
            col.set_sort_column_id(i)
            self.settings_tree.append_column(col)
        #add hidden color columns
        ls = ["background","Foreground"]
        for cn in ls:
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(cn, renderer)
            col.set_property("visible",False)
            self.settings_tree.append_column(col)

        #self.settings_tree.get_selection().connect("changed", self.row_clicked)
        self.settings_tree.connect("button_press_event", self.row_clicked)
        #add to window
        scroll = Gtk.ScrolledWindow()
        scroll.set_margin_left(10)
        scroll.set_margin_right(10)
        scroll.add(self.settings_tree)
        self.widget.pack_start(scroll,1,1,10)
        sc = self.widget.get_style_context()
        sc_tree = self.widget.get_style_context()
        sc.add_class(self.widget_class)
        for style in self.styles:
                sc.add_class(style)
                sc_tree.add_class(style)
        sc = lbl.get_style_context()
        sc.add_class('font-20')
        self.load_liststore()

    def load_liststore(self):
        self.settings_list.clear()
        self.iter_keys = {}
        rows = self.db_manager.run_query('SELECT * FROM [Tags-SettingsWidget]')
        data = []
        l = []
        for row in rows:
            temp = dict(row)
            data.append(temp)
        iter_row = 0
        for grp in data:
            for item in self.all_cols:
                if item == 'Use' or item == 'ReadWrite':
                    l.append(bool(grp[item]))
                else:
                    l.append(str(grp[item]))
            if grp['ReadWrite']:
                #filling in hidden color columns
                l.append(str("white"))
                l.append(str("black"))
            else:
                l.append(str("#303030"))
                l.append(str("white"))
            if grp['Use']:
                self.settings_list.append(l)
                self.iter_keys[grp['ValueTag']] =    self.settings_list.get_iter(iter_row)
                iter_row += 1
            l = []

    def text_edited(self, cellren, path, val):
        treeiter = self.settings_list.get_iter(path)
        # Get widget ID
        w_id = self.settings_list.get_value(treeiter, 0)
        set_row = self.get_setting_row(w_id) #get column data
        if self.check_limits(val,set_row['ValMin'],set_row['ValMax']):
            self.settings_list[path][self.newValue_pos] = str(val)
            #update database with accepted value
            self.update_db_val('NewValue',w_id,val)

    def update_value(self,val,params,*args):
        if self.check_limits(val,float(params['ValMin']),float(params['ValMax'])):
            self.settings_list[int(params['ID'])-1][self.newValue_pos] = str(val)
            self.update_db_val('NewValue',params['ID'],val)

    def update_db_val(self, table, w_id, val):
        self.db_manager.set_db_val_by_id('Tags-SettingsWidget',table,w_id,val)

    def check_limits(self, val,min_val,max_val):
        try:
            val = float(val)
        except ValueError:
            return False
        if not type(min_val) == type(None) and val < min_val:
            return False        
        if not type(max_val) == type(None) and val > max_val:
            return False
        return True

    def class_update(self, factory, subscriber):
        if subscriber != self.display:
            return
        tags = list(self.iter_keys)
        temp =[]
        for t in tags:
            t = t[1:-1]
            temp.append(t)
        tags = temp
        update = self.connection_manager.read(tags,self.display)
        for key,iter_obj in self.iter_keys.items():
            self.settings_list[iter_obj][self.currentValue_pos] = str(update[key[1:-1]]['Value'])
        if self.expression != None:
            self.enable_ctrl_btns(self.connection_manager.evaluate_expression(self,self.expression,self.display,str))
    
    def get_setting_row(self,w_id,*args):
        rows = self.db_manager.run_query('SELECT * FROM [Tags-SettingsWidget] WHERE [ID] = ? ',(str(w_id),))
        data = {}
        for row in rows:
            data = dict(row)
        return data

    def save_config_settings(self, ID_list,req_column,*args):
        for i in range(len(ID_list)):
            val = self.settings_list[i][req_column]    #get value in specified Column
            self.settings_list[i][self.saveValue_pos] = val #write value to settings widget in SavedValue Column
            self.update_db_val('SavedValue',(i+1),val)
            #self.db_manager.set_db_val_by_id('Tags-SettingsWidget','SavedValue',(i+1),val)
        
    def button_pressed(self,widget,name,*args):
        if self.builder_mode:
            #Don't do actions if in builder mode
            return
        if name == 'EXPORT':
            self.app.save_file(self.export_settings,file_hint=None,filter_pattern = [])
        elif name == 'SEND ALL':
            rows = self.db_manager.run_query('SELECT [ID] FROM [Tags-SettingsWidget]')
            self.confirm_send_all(rows)
        elif name == 'SEND':
            #check if any row selected
            selection = self.settings_tree.get_selection()
            model,pathlist = selection.get_selected_rows()
            if pathlist !=None:
                for path in pathlist :
                        tree_iter = model.get_iter(path)
                        ID = model.get_value(tree_iter,0)
                        self.confirm_send(ID)
        elif name == 'SAVE NEW':
            rows = self.db_manager.run_query('SELECT [ID] FROM [Tags-SettingsWidget]')
            self.save_config_settings(rows,self.newValue_pos)
        elif name == 'SAVE CURRENT':
            rows = self.db_manager.run_query('SELECT [ID] FROM [Tags-SettingsWidget]')
            self.save_config_settings(rows,self.CurrentValue_pos)
        elif name == 'STORE':
            self.confirm_store()
        elif name == 'REFERSH':
            self.connection_manager.update_sub_tags() 
        self.class_update(self.factory, "__CONFIGURATION_SETTINGS__") #update items displayed
    
    def row_clicked(self, treeview,event,*args):
        if self.builder_mode:
            #Don't do actions if in builder mode
            return
        if event.button == 1: #left click
            pthinfo = treeview.get_path_at_pos(event.x, event.y)
            if pthinfo != None:
                path,col,cellx,celly = pthinfo
                treeview.grab_focus()
                treeview.set_cursor(path,col,0)
                selection = treeview.get_selection()

                (model, iter) = selection.get_selected()
                row_data = []
                for item in model[iter]:
                    row_data.append(item)
                row_dic = {self.all_cols[i]: row_data[i] for i in range(len(self.all_cols))}
                col_name = col.get_title()    #detects the name of the column clicked
                #print(model[iter][0],col.get_title()) #provides row data
                if col_name == 'NewValue':
                    if row_dic['DataType'] == 'BOOL':
                        self.app.set_reset(self.update_value, self,self.widget ,row_dic,row_dic['NewValue'])
                    elif row_dic['DataType'] == 'INT' or row_dic['DataType'] == 'REAL':
                        #update this to just be the numpad
                        self.app.open_keypad(self.update_value, self,self.widget ,row_dic,row_dic['NewValue'])
                    elif row_dic['DataType'] == 'STR':
                        self.app.open_keypad(self.update_value, self,self.widget ,row_dic,row_dic['NewValue'])
        elif event.button == 3: #right click]
            if (self.connection_manager.evaluate_expression(self,self.expression,self.display,str)):
                rect = Gdk.Rectangle()
                rect.x = event.x
                rect.y = event.y + 20
                rect.width = rect.height = 1
                selection = treeview.get_selection()
                tree_model, tree_iter = selection.get_selected()
                if tree_iter is None:
                    return
                w_id = tree_model[tree_iter][0]
                popover = Gtk.Popover(width_request = 200)
                vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                send_btn = Gtk.ModelButton(label="Send Setting", name=w_id)
                cb = lambda btn: self.confirm_send(w_id)
                send_btn.connect("clicked", cb)
                vbox.pack_start(send_btn, False, True, 10)
                popover.add(vbox)
                popover.set_position(Gtk.PositionType.RIGHT)
                popover.set_relative_to(treeview)
                popover.set_pointing_to(rect)
                popover.show_all()
                sc = popover.get_style_context()
                sc.add_class('popover-bg')
                sc.add_class('font-16')
            else:
                event_msg = "Unable to send setting not connected to device"
                self.app.display_event(event_msg)

    def confirm_store(self,*args):
        self.app.confirm(self.store_settings, "Are you sure you want to overwrite database settings")

    def store_settings(self, *args):
        self.db_manager.copy_table("Tags-SettingsWidget")

    def confirm_send(self, w_id, *args):
        self.app.confirm(lambda:self.sendValue(w_id), "Are you sure you want to send setting")
    
    def confirm_send_all(self, ID_list, *args):
        self.app.confirm(lambda:self.send_all(ID_list), "Send all settings?")
    
    def send_all(self, ID_list):
        for row in ID_list:
            self.sendValue(row[0])
    
    def sendValue(self,w_id,*args):
        set_row = self.get_setting_row(w_id) #get column data
        self.write(set_row['ValueTag'], set_row['NewValue'])

    def export_settings(self, fp, *args):
        rows = self.db_manager.run_query('SELECT {} FROM [Tags-SettingsWidget] DESC;'.format(", ".join(self.cols)))
        data = {}
        for row in rows:
            data = dict(row)
        try:
            tmp = os.path.splitext(fp)[-1].lower()
            if not tmp:
                filename_suffix = ".txt"
                fp=os.path.join(fp + "." + filename_suffix)
            f = open(fp, "w")
            for item in data:
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
