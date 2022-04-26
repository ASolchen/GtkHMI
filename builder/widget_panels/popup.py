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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject
from backend.widget_classes.factory import WIDGET_TYPES
from backend.widget_classes.widget import Widget
from builder.widget_panels.widget_panel import BuilderToolsWidget , AdvancedBuilderToolsWidget
import re

class WidgetSettingsPopup(Gtk.Dialog):
    def __init__(self, parent, app, db_manager, w_id):
        Gtk.Dialog.__init__(self, "{} Settings".format(w_id), parent, Gtk.DialogFlags.MODAL,
                                                (Gtk.STOCK_CLOSE, Gtk.ResponseType.ACCEPT)
                                                )
        self.db_manager = db_manager
        self.app = app
        self.w_id = w_id
        self.set_default_size(1024, 840)
        self.set_border_width(30)
        self.set_keep_above(True)
        sc = self.get_style_context()
        sc.add_class("dialog-border")
        c = self.get_content_area()
        self.notebook = Gtk.Notebook() 
        c.add(self.notebook)
        sc = self.notebook.get_style_context()
        sc.add_class('text-white-color')
        sc.add_class('font-14')
        self.build_base()
        #Add style to dialog buttons
        a = self.get_action_area()
        b = a.get_children()
        for but in b:
            sc = but.get_style_context()
            sc.add_class("dialog-buttons")
            sc.add_class("font-16")
        self.show_all()


    def build_base(self):
        rows = self.db_manager.get_rows("Widgets", Widget.base_parmas, "ID", self.w_id)
        self.page1 = Gtk.Box() 
        self.page1.set_border_width(50)
        if len(rows):
            row = rows[0]
            self.page1.add(BuilderToolsWidget(self.app, row))
            self.notebook.append_page(self.page1, Gtk.Label("Basic")) 
            self.page2 = Gtk.Box() 
            self.page2.set_border_width(50) 
            self.page2.add(AdvancedBuilderToolsWidget(self.app, row)) 
            self.notebook.append_page(self.page2, Gtk.Label("Advanced"))


class CreateWidgetWindow(Gtk.Window):
    def __init__(self, parent, app, db_manager,wid_type,parent_id):
        #adding widget:wid_type = New and parent_id=where to put widget
        #adding display:wid_type = 'display' and parent_id = None
        super(CreateWidgetWindow, self).__init__()
        self.db_manager = db_manager
        self.app = app
        self.wid_type = wid_type
        self.parent_id = parent_id
        self.set_property('window-position', Gtk.WindowPosition.CENTER)
        self.set_title('Widgets')
        self.set_border_width(30)
        self.set_default_size(700, 700)
        self.set_keep_above(True)
        self.connect("delete_event", lambda *args: self.destroy())
        self.set_keep_above(True)
        self.window_area = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)

        '''______Header_____'''
        header = Gtk.Box()
        p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Widget.png', 40, -1, True)
        icon = Gtk.Image(pixbuf=p_buf)
        header.pack_start(icon, 0, 0, 0)
        label = Gtk.Label('Create Widget')
        self.add_style(label,['text-white-color','font-20','font-bold'])
        header.pack_start(label, 1, 1, 0)
        self.window_area.pack_start(header, False, False, 0)
        
        bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, height_request =30,homogeneous = True)
        label = Gtk.Label('Select Widget: ', height_request =30)
        self.add_style(label,['text-white-color','font-18','font-bold'])
        bx.pack_start(label, 0, 0, 0)
        self.widget_combo = Gtk.ComboBoxText(width_request = 100)
        self.add_style(self.widget_combo,["font-12","font-bold"])
        key = WIDGET_TYPES.keys()
        if self.wid_type != 'display':
            self.widget_combo.append_text('None')
            for k in key:
                self.widget_combo.append_text(k)
            self.widget_combo.set_active(0)
        else:
            self.widget_combo.append_text('display')
            self.widget_combo.set_active(0)
        self.widget_combo.connect("changed", self.rebuild_widget_settings)
        bx.pack_start(self.widget_combo, 0, 0, 0)
        header.pack_end(bx, 0, 0, 0)
        if self.parent_id != None:
            par_str = 'Add Item To: '+str(self.parent_id)
            par_create = Gtk.Label(par_str)
            bx.pack_start(par_create, 0, 0, 0)

        div = Gtk.Separator()
        div.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(120,120,120,1))
        self.window_area.pack_start(div, False, False, 0)
 

        '''____Filling the Content Area____'''
        self.content_area = Gtk.Box(spacing = 10,orientation=Gtk.Orientation.VERTICAL)
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_size_request(1000, 400)
        self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scroll.add(self.content_area)
        self.window_area.pack_start(self.scroll, True, True, 0)
        self.notebook = Gtk.Notebook() 
        self.content_area.add(self.notebook)
        sc = self.notebook.get_style_context()
        sc.add_class('text-white-color')
        sc.add_class('font-14')
        self.build_base()

        '''______Footer_____'''
        div = Gtk.Separator()
        div.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(120,120,120,1))
        self.window_area.pack_start(div, False, False, 0)
        footer = Gtk.Box(homogeneous = True,halign =Gtk.Align.END )

        self.close_btn_box = Gtk.Box(halign = Gtk.Align.CENTER)
        but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Close.png', 40, -1, True)
        icon = Gtk.Image(pixbuf=p_buf)
        but_box.pack_start(icon, 0, 0, 0)
        label = Gtk.Label("Close")
        but_box.pack_start(label, 1, 0, 10)
        close_btn = Gtk.Button(width_request = 150, height_request = 50)
        close_btn.set_tooltip_text('Click to close popup')
        self.add_style(close_btn,["ctrl-button","font-16","font-bold"])
        close_btn.add(but_box)
        close_btn.connect("clicked", lambda btn: self.destroy())
        self.close_btn_box.pack_start(close_btn, 0, 0, 0)
        footer.pack_end(self.close_btn_box, 0, 0, 1)

        self.create_btn_box = Gtk.Box(halign = Gtk.Align.CENTER)
        but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Create.png', 40, -1, True)
        icon = Gtk.Image(pixbuf=p_buf)
        but_box.pack_start(icon, 0, 0, 0)
        label = Gtk.Label("Create")
        but_box.pack_start(label, 1, 0, 10)
        close_btn = Gtk.Button(width_request = 150, height_request = 50)
        close_btn.set_tooltip_text('Click to create widget')
        self.add_style(close_btn,["ctrl-button","font-16","font-bold"])
        close_btn.add(but_box)
        close_btn.connect("clicked", lambda btn: self.destroy())
        self.create_btn_box.pack_start(close_btn, 0, 0, 0)
        footer.pack_end(self.create_btn_box, 0, 0, 1)

        self.window_area.pack_start(footer, False, False, 0)
        self.add(self.window_area)
        self.show_all()

    def build_base(self):
        if self.parent_id != None:
            rows = self.db_manager.get_rows("Default-WidgetParams", Widget.base_parmas, "Class", 'display')
            #Need to be able to create all widgets here not just display
        else:
            rows = self.db_manager.get_rows("Default-WidgetParams", Widget.base_parmas, "Class", 'display')
        self.page1 = Gtk.Box() 
        self.page1.set_border_width(50)
        if len(rows):
            row = rows[0]
            self.page1.add(BuilderToolsWidget(self.app, row))
            self.notebook.append_page(self.page1, Gtk.Label("Basic")) 
            self.page2 = Gtk.Box() 
            self.page2.set_border_width(50) 
            self.page2.add(Gtk.Label("Need to put class stuff here")) 
            self.notebook.append_page(self.page2, Gtk.Label("Advanced"))

            ############Add a create button
            ############be able to create displays
            ############when creating widets add basic style and put on screen so it can be moved
            ############Add widget advanced settings

    
    def rebuild_widget_settings(self,*args):
        print(self.wid_type)
        print(self.widget_combo.get_active_text())

    def add_style(self, wid, style):
        #style should be a list
        sc = wid.get_style_context()
        for sty in style:
            sc.add_class(sty)

class ConnectionListWindow(Gtk.Window):
    def __init__(self, parent, app, db_manager):
        super(ConnectionListWindow, self).__init__()
        self.db_manager = db_manager
        self.app = app
        self.conx_Typedata = {}
        for item in self.db_manager.run_query('SELECT * FROM [ConnectionTypes]'):
            self.conx_Typedata[item[0]]= item[1]
        self.set_property('window-position', Gtk.WindowPosition.CENTER)
        self.set_title('Connections')
        self.set_border_width(30)
        self.set_default_size(1000, 700)
        self.set_keep_above(True)
        self.connect("delete_event", lambda *args: self.destroy())
        self.set_keep_above(True)
        self.window_area = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)

        '''______Header_____'''
        header = Gtk.Box()
        p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Connection.png', 40, -1, True)
        icon = Gtk.Image(pixbuf=p_buf)
        header.pack_start(icon, 0, 0, 0)
        label = Gtk.Label('Connections')
        self.add_style(label,['text-white-color','font-20','font-bold'])
        header.pack_start(label, 1, 1, 0)
        self.window_area.pack_start(header, False, False, 0)
        
        '''______Fill Header_____'''
        box = Gtk.Box(homogeneous = True)
        for l in ['Delete/Create', 'Name', 'Type', 'Driver Settings']:
            header_lbl = Gtk.Label(l)
            box.pack_start(header_lbl, True, True, 0)
            self.add_style(header_lbl,['text-white-color','font-18','font-bold'])
        self.window_area.pack_start(box, False, False, 0)
        div = Gtk.Separator()
        div.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(120,120,120,1))
        self.window_area.pack_start(div, False, False, 0)
 

        '''____Filling the Content Area____'''
        self.content_area = Gtk.Box(spacing = 10,orientation=Gtk.Orientation.VERTICAL)
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_size_request(1000, 400)
        self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scroll.add(self.content_area)
        self.window_area.pack_start(self.scroll, True, True, 0)
        self.build()

        '''______Footer_____'''
        div = Gtk.Separator()
        div.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(120,120,120,1))
        self.window_area.pack_start(div, False, False, 0)
        footer = Gtk.Box(homogeneous = True,halign =Gtk.Align.END )

        self.close_btn_box = Gtk.Box(halign = Gtk.Align.CENTER)
        but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Close.png', 40, -1, True)
        icon = Gtk.Image(pixbuf=p_buf)
        but_box.pack_start(icon, 0, 0, 0)
        label = Gtk.Label("Close")
        but_box.pack_start(label, 1, 0, 10)
        close_btn = Gtk.Button(width_request = 150, height_request = 50)
        close_btn.set_tooltip_text('Click to close popup')
        self.add_style(close_btn,["ctrl-button","font-16","font-bold"])
        close_btn.add(but_box)
        close_btn.connect("clicked", lambda btn: self.destroy())
        self.close_btn_box.pack_start(close_btn, 0, 0, 0)
        footer.pack_end(self.close_btn_box, 0, 0, 1)

        self.window_area.pack_start(footer, False, False, 0)
        self.add(self.window_area)
        self.show_all()

    
    def build(self):
        self.add_conn_box = Gtk.Box(halign = Gtk.Align.CENTER,hexpand = True)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/New.png', 40, -1, True)
        icon = Gtk.Image(pixbuf=p_buf)
        box.pack_start(icon, 0, 0, 0)
        label = Gtk.Label("Add Connection")
        box.pack_start(label, 0, 0, 0)
        add_conn_btn = Gtk.Button(width_request = 180, height_request = 50)
        self.add_style(add_conn_btn,["ctrl-button","font-16","font-bold"])
        add_conn_btn.add(box)
        add_conn_btn.connect("clicked", self.new_row , None)
        self.add_conn_box.pack_start(add_conn_btn, 0, 0, 0)
        self.content_area.pack_start(self.add_conn_box, 0, 0, 0)
        #Add all existing connections to box
        conn_rows = self.db_manager.run_query('SELECT ID FROM [Connections]')
        for c_id in conn_rows:
            self.new_row(None,c_id[0])
    
    def new_row(self, button,c_id):
        row = ConnectionListRow(conx_id=c_id, db=self.db_manager, parent = self , content_area = self.content_area,conntype_dic = self.conx_Typedata, app = self.app)
        self.content_area.remove(self.add_conn_box)
        self.content_area.pack_start(row, 0, 0, 0)
        self.content_area.pack_start(self.add_conn_box, 0, 0, 0)
        adjust = self.scroll.get_vadjustment()
        self.show_all()
        GObject.timeout_add(50, self.scroll_to_bottom, adjust)
        return True
    
    def scroll_to_bottom(self, adjust):
        max = adjust.get_upper()
        adjust.set_value(max)
        self.scroll.set_vadjustment(adjust)
        return False

    def add_style(self, wid, style):
        #style should be a list
        sc = wid.get_style_context()
        for sty in style:
            sc.add_class(sty)

class TagsListWindow(Gtk.Window):
    def __init__(self, conx_id = None, app = None, db = None):
        super(TagsListWindow, self).__init__()
        self.db_manager = db
        self.app = app
        self.available_conx = {}
        self.conx_id = conx_id
        '''________Window Setup_______'''
        self.set_property('window-position', Gtk.WindowPosition.CENTER)
        self.set_title('Tags')
        self.set_border_width(10)
        self.set_default_size(1000, 900)
        self.set_keep_above(True)
        self.connect("delete_event", lambda *args: self.destroy())
        self.set_keep_above(True)
        self.window_area = Gtk.Box(spacing=1, orientation=Gtk.Orientation.VERTICAL)
        '''________Gather Data_______'''
        sql = self.db_manager.run_query('SELECT * FROM [Connections]')
        if sql != None:
            for item in sql:
                self.available_conx[item[0]]= item[1]
            if self.conx_id == None:
                self.conx_id = sql[0][0]
     #get connection specific tag data
        c_data = self.db_manager.run_query('''SELECT Connection,ConnectionTypeID From Connections WHERE ID = ?;''',(self.conx_id,))
        self.conx_user_name = c_data[0][0]
        self.conx_type_id = c_data[0][1]
        c_type = self.db_manager.run_query('''SELECT ConnectionType From ConnectionTypes WHERE ID =?;''',(self.conx_type_id,))
        self.conx_type_name = (c_type[0][0])
        self.tag_params_db_name = self.conx_type_name+'TagParams'

        '''______Header_____'''
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, height_request =30)
        p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Tag.png', 30, -1, True)
        icon = Gtk.Image(pixbuf=p_buf)
        header.pack_start(icon, 0, 0, 0)
        label = Gtk.Label('Tags', height_request =30)
        self.add_style(label,['text-white-color','font-20','font-bold'])
        header.pack_start(label, 1, 1, 0)
        self.window_area.pack_start(header, False, False, 0)

        bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, height_request =30)
        label = Gtk.Label('Connection: ', height_request =30)
        self.add_style(label,['text-white-color','font-16','font-bold'])
        bx.pack_start(label, 0, 0, 0)
        self.conx_combo = Gtk.ComboBoxText(width_request = 100)
        self.add_style(self.conx_combo,["font-12","font-bold"])
        if self.conx_id !=None:
            key = self.available_conx.keys()
            temp = 0
            for k in key:
                self.conx_combo.append_text(self.available_conx[k])
                if self.conx_user_name == self.available_conx[k]:
                    self.conx_combo.set_active(temp)
                temp += 1
            #self.conx_combo.set_active(0)
        self.conx_combo.connect("changed", self.update_tags)
        bx.pack_start(self.conx_combo, 0, 0, 0)
        header.pack_end(bx, 0, 0, 0)
        
        '''______Fill Header_____'''
        box = Gtk.Box(homogeneous = True, height_request =40)
        for l in ["ID","Tag","Description","Address","Button"]:
            if l == "Button":
                btn_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL,height_request = 25)
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/New.png', 25, -1, True)
                icon = Gtk.Image(pixbuf=p_buf)
                btn_box.pack_start(icon, 0, 0, 0)
                lbl = Gtk.Label("Add New Tag")
                btn_box.pack_start(lbl, 0, 0, 0)
                add_tag_btn = Gtk.Button(height_request = 25)
                add_tag_btn.connect("clicked", self.open_tag_settings,None)
                self.add_style(add_tag_btn,["compress-button","font-14","font-bold"])
                add_tag_btn.add(btn_box)
                box.pack_end(add_tag_btn,0,0,0)
            else:
                header_lbl = Gtk.Label(l)
                box.pack_start(header_lbl, True, True, 0)
                self.add_style(header_lbl,['text-white-color','font-14','font-bold'])
        self.window_area.pack_start(box, False, False, 0)
        div = Gtk.Separator()
        div.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(120,120,120,1))
        self.window_area.pack_start(div, False, False, 0)
 

        '''____Filling the Content Area____'''
        self.content_area = Gtk.Box(spacing = 4,orientation=Gtk.Orientation.VERTICAL)
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_size_request(1000, 400)
        self.scroll.set_margin_left(10)
        self.scroll.set_margin_right(10)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        self.scroll.set_overlay_scrolling(False)
        self.scroll.add(self.content_area)
        self.window_area.pack_start(self.scroll, True, True, 0)
        if self.conx_id != None:
            self.build()

        '''______Footer_____'''
        div = Gtk.Separator()
        div.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(120,120,120,1))
        self.window_area.pack_start(div, False, False, 0)
        footer = Gtk.Box(homogeneous = True,halign =Gtk.Align.END, height_request =40 )

        self.back_btn_box = Gtk.Box(halign = Gtk.Align.CENTER, height_request =35)
        but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Refresh.png', 30, -1, True)
        icon = Gtk.Image(pixbuf=p_buf)
        but_box.pack_start(icon, 0, 0, 0)
        label = Gtk.Label("Back")
        but_box.pack_start(label, 1, 0, 10)
        back_btn = Gtk.Button(width_request = 100, height_request = 30)
        back_btn.set_tooltip_text('Click to go to connections settings')
        self.add_style(back_btn,["ctrl-button","font-16","font-bold"])
        back_btn.add(but_box)
        back_btn.connect("clicked", self.open_connection_settings)
        self.back_btn_box.pack_end(back_btn, 0, 0, 0)
        footer.pack_start(self.back_btn_box, 0, 0, 1)

        self.close_btn_box = Gtk.Box(halign = Gtk.Align.CENTER, height_request =35)
        but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Close.png', 30, -1, True)
        icon = Gtk.Image(pixbuf=p_buf)
        but_box.pack_start(icon, 0, 0, 0)
        label = Gtk.Label("Close")
        but_box.pack_start(label, 1, 0, 10)
        close_btn = Gtk.Button(width_request = 100, height_request = 30)
        close_btn.set_tooltip_text('Click to close popup')
        self.add_style(close_btn,["ctrl-button","font-16","font-bold"])
        close_btn.add(but_box)
        close_btn.connect("clicked", lambda btn: self.destroy())
        self.close_btn_box.pack_start(close_btn, 0, 0, 0)
        footer.pack_end(self.close_btn_box, 0, 0, 1)

        self.window_area.pack_start(footer, False, False, 0)
        self.add(self.window_area)
        self.show_all()
    
    def build(self,*args):
        ts = TagsListRow(self.conx_id,db = self.db_manager,window = self,app = self.app, parent = self)
        self.content_area.pack_start(ts, 1,1,0)
    
    def update_tags(self,*args):
        if self.content_area:
            child_list = self.content_area.get_children()
            for c in child_list:
                self.content_area.remove(c)
            val = self.conx_combo.get_active_text()
            keys = list(self.available_conx.keys())
            values = list(self.available_conx.values())
            position = values.index(val)
            self.conx_id = keys[position]
            self.build()
            self.resize(1000, 900)
            self.show_all()

    def open_tag_settings(self, button,idx):
            Ntag = False
            if not idx:
                idx = self.create_new_tag()
                Ntag = True
            popup = TagSettingsWindow(idx, self.conx_id    , db = self.db_manager, app = self.app, new_tag = Ntag )
            self.destroy()
    
    def create_new_tag(self,*args):
            self.tag_db_name = 'Tags'
            self.tag_db_columns = ['Tag','Description','DataType','ConnectionID']
            col_name_str = '('
            for i in self.tag_db_columns:
                col_name_str += "'"+str(i) +"',"
            col_name_str = col_name_str[:-1]    #remove extra comma
            col_name_str += ')'
            new_tagid = self.db_manager.add_item_to_table(self.tag_db_name,col_name_str,['New','', 'BOOL',self.conx_id])
            self.db_manager.copy_table(self.tag_db_name)
            self.db_manager.add_default_param_item(self.tag_params_db_name,new_tagid)
            self.db_manager.copy_table(self.tag_params_db_name)
            return new_tagid
 
    def scroll_to_bottom(self, adjust):
        max = adjust.get_upper()
        adjust.set_value(max)
        self.scroll.set_vadjustment(adjust)
        return False

    def add_style(self, wid, style):
        #style should be a list
        sc = wid.get_style_context()
        for sty in style:
            sc.add_class(sty)

    def close_popup(self,*args):
            self.destroy()
    
    def open_connection_settings(self, *args):
        popup = ConnectionSettingsWindow(self.conx_id, db = self.db_manager, app = self.app )
        self.close_popup()

class TagsListRow(Gtk.Box):
        def __init__(self,conx_id,db=None,window=None,app = None, parent = None):
                super(TagsListRow, self).__init__()
                self.db_manager = db
                self.conx_id = conx_id
                self.window = window
                self.app = app
                self.parent = parent
                self.cols = ["ID","Tag","Description","Address"]

                #get connection specific tag data
                c_data = self.db_manager.run_query('''SELECT Connection,ConnectionTypeID From Connections WHERE ID = ?;''',(self.conx_id,))
                self.conx_user_name = c_data[0][0]
                self.conx_type_id = c_data[0][1]
                c_type = self.db_manager.run_query('''SELECT ConnectionType From ConnectionTypes WHERE ID =?;''',(self.conx_type_id,))
                self.conx_type_name = (c_type[0][0])
                self.tag_params_db_name = self.conx_type_name+'TagParams'
                self.list_box_data()

        def open_tag_settings(self, button,idx):
            Ntag = False
            if not idx:
                idx = self.create_new_tag()
                Ntag = True
            popup = TagSettingsWindow(idx, self.conx_id    , db = self.db_manager, app = self.app, new_tag = Ntag )
            self.window.destroy()
        
        def delete_tag(self, btn,id_num, row, *args):
            confirmed = self.app.confirm(None, 'Are you sure you want to delete the tag', [])
            if confirmed:
                self.db_manager.delete_item_from_table('Tags','ID',id_num)
                self.db_manager.delete_item_ext_table("public/mill.db",'Tags','ID',id_num)
                self.db_manager.delete_item_from_table(self.tag_params_db_name,'ID',id_num)
                self.db_manager.delete_item_ext_table("public/mill.db",self.tag_params_db_name,'ID',id_num)
                self.listbox.remove(row)
        
        def create_new_tag(self,*args):
            self.tag_db_name = 'Tags'
            self.tag_db_columns = ['Tag','Description','DataType','ConnectionID']
            col_name_str = '('
            for i in self.tag_db_columns:
                col_name_str += "'"+str(i) +"',"
            col_name_str = col_name_str[:-1]    #remove extra comma
            col_name_str += ')'
            new_tagid = self.db_manager.add_item_to_table(self.tag_db_name,col_name_str,['New','', 'BOOL',self.conx_id])
            self.db_manager.copy_table(self.tag_db_name)
            self.db_manager.add_default_param_item(self.tag_params_db_name,new_tagid)
            self.db_manager.copy_table(self.tag_params_db_name)
            return new_tagid

        def scroll_to_bottom(self, adjust):
            max = adjust.get_upper()
            adjust.set_value(max)
            self.scroll.set_vadjustment(adjust)
            return False

        def list_box_data(self):
            t_list = self.cols.copy()
            for idx, item in enumerate(t_list):
                if item == 'Address':
                    t_list[idx] = str(self.tag_params_db_name)+'.'+item
                else:
                    t_list[idx] = 'Tags.'+item
            inner_join = str(self.tag_params_db_name)+'.ID = Tags.ID'
            self.listbox = Gtk.ListBox(halign =Gtk.Align.FILL,valign = Gtk.Align.FILL)
            self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
            sc = self.listbox.get_style_context()
            self.parent.add_style(self.listbox,['config-list-box'])
            self.pack_start(self.listbox, 0, 0, 0)
            col_list = ','.join(self.cols)
            column_list = ','.join(t_list)
            #rows = self.db_manager.run_query('SELECT {lst} FROM [{tbl}]'.format(lst =col_list, tbl = self.tag_conx_db_name,)) 
            sql = "SELECT {lst} FROM [{tbl}] INNER JOIN {tbl2} ON {ij} WHERE Tags.ConnectionID = ?;".format( lst =column_list,tbl = self.tag_params_db_name,tbl2 = 'Tags',ij = inner_join)
            rows = self.db_manager.run_query(sql,[self.conx_id,])
            data = []
            for row in rows:
                temp = dict(row)
                data.append(temp)
            even_row = False
            for line in data:
                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous = True,height_request = 30)
                row.add(hbox)
                for col in self.cols:
                    lbl = Gtk.Label(label=line[col], xalign=0.5, yalign = 0.5)
                    hbox.pack_start(lbl, True, True, 0)
                    self.parent.add_style(lbl,['font-14','font-bold'])
                if even_row:
                    self.parent.add_style(row,['list-box-even-row'])
                    even_row = False
                else:
                    self.parent.add_style(row,['list-box-odd-row'])
                    even_row = True
                btn_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL,height_request = 25,spacing = 10)
                bx = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL,height_request = 25)
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/settings.png', 25, -1, True)
                icon = Gtk.Image(pixbuf=p_buf)
                lbl = Gtk.Label("Tag Settings")
                bx.pack_start(lbl, 1, 0, 10)
                bx.pack_start(icon, 0, 0, 0)
                settings_btn = Gtk.Button( height_request = 25, width_request = 25)
                settings_btn.connect("clicked", self.open_tag_settings,line['ID'])
                self.parent.add_style(settings_btn,["compress-button","font-14","font-bold"])
                settings_btn.add(bx)
                btn_box.pack_start(settings_btn,False,False,0)
                hbox.pack_start(btn_box, False, False, 0)
                
                bx2 = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL,height_request = 25)
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Delete.png', 25, -1, True)
                icon = Gtk.Image(pixbuf=p_buf)
                lbl = Gtk.Label("Delete")
                bx2.pack_start(lbl, 1, 0, 10)
                bx2.pack_start(icon, 0, 0, 0)
                delete_btn = Gtk.Button( height_request = 25, width_request = 25)
                delete_btn.connect("clicked", self.delete_tag,line['ID'],row)
                self.parent.add_style(delete_btn,["compress-button","font-14","font-bold"])
                delete_btn.add(bx2)
                btn_box.pack_start(delete_btn,False,False,0)
                
                self.listbox.add(row)

class ConnectionListRow(Gtk.Box):
        def __init__(self, conx_id=None,db=None, parent = None , content_area = None, conntype_dic = None, app = None):
                super(ConnectionListRow, self).__init__()
                self.parent = parent    # Holds a reference to the parent window
                self.content_area = content_area
                self.conx_id = conx_id
                self.db_manager = db
                self.app = app
                self.conx_Typedata = conntype_dic
                self.set_spacing(4)

                if self.conx_id != None:
                    #get connection specific data
                    c_data = self.db_manager.run_query('''SELECT Connection,ConnectionTypeID From Connections WHERE ID = ?;''',(self.conx_id,))
                    self.conx_user_name = c_data[0][0]
                    self.conx_type_id = c_data[0][1]
                    c_type = self.db_manager.run_query('''SELECT ConnectionType From ConnectionTypes WHERE ID =?;''',(self.conx_type_id,))
                    self.conx_type_name = (c_type[0][0])
                else:
                    pass
                    #creating a new connection

                #Used to tunnel back up to parent: self.parent.test('')
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Connect.png', 40, -1, True)
                icon = Gtk.Image(pixbuf=p_buf)
                self.pack_start(icon, 0, 0, 0)
                box = Gtk.Box(homogeneous = True,spacing = 10,)
                d_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing = 10)
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/New.png', 40, -1, True)
                self.delete_create_icon = Gtk.Image(pixbuf=p_buf)
                d_box.pack_start(self.delete_create_icon, 0, 0, 20)
                self.delete_create_lbl = Gtk.Label("Create")
                d_box.pack_start(self.delete_create_lbl, 0, 0, 0)
                self.delete_create_button = Gtk.Button(sensitive = False)
                self.parent.add_style(self.delete_create_button,["ctrl-button","font-16","font-bold"])
                self.delete_create_button.add(d_box)
                box.pack_start(self.delete_create_button, True, True, 0)
                self.delete_create_button.connect("clicked", self.update_connection)
                self.conx_name = Gtk.Entry(max_length = 30)
                self.conx_name.set_alignment(0.5)
                self.parent.add_style(self.conx_name,["entry","font-16","font-bold"])
                box.pack_start(self.conx_name, True, True, 0)
                self.conx_name.connect("notify::text-length", self.enable_new)
                self.connection_type_combo = Gtk.ComboBoxText()
                self.parent.add_style(self.connection_type_combo,["font-18","list-select"])
                for key in self.conx_Typedata:
                    self.connection_type_combo.append(str(key),self.conx_Typedata[key])

                self.connection_type_combo.set_active(0)
                box.pack_start(self.connection_type_combo, True, True, 0)
                self.pack_start(box, 1, 1, 0)
                self.driver_settings_button = Gtk.Button(label="Settings", sensitive = False)
                self.parent.add_style(self.driver_settings_button,["ctrl-button","font-14","font-bold"])
                self.driver_settings_button.connect("clicked", self.open_driver_settings)
                box.pack_start(self.driver_settings_button, True, True, 0)
                if self.conx_id != None:
                    self.update_row()

        def enable_new(self, obj, prop):
            enable = (obj.get_property('text-length') > 0)
            self.delete_create_button.set_sensitive(enable)

        def update_row(self,*args):
            #this method updates the enables / disables of buttons on connection settings popup
            c_data = self.db_manager.run_query('''SELECT Connection,ConnectionTypeID From Connections WHERE ID = ?;''',(self.conx_id,))
            self.conx_user_name = c_data[0][0]
            self.conx_type_id = c_data[0][1]
            c_type = self.db_manager.run_query('''SELECT ConnectionType From ConnectionTypes WHERE ID =?;''',(self.conx_type_id,))
            self.conx_type_name = (c_type[0][0])
            conx_type = self.db_manager.run_query('''SELECT ID,ConnectionType From ConnectionTypes WHERE ID =?;''',(self.conx_id,))
            p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Delete.png', 40, -1, True)
            self.delete_create_lbl.set_text("Delete")
            self.delete_create_icon.set_from_pixbuf(p_buf)
            self.conx_name.set_text(self.conx_user_name)
            self.connection_type_combo.remove_all()
            self.connection_type_combo.append_text(self.conx_type_name)
            self.connection_type_combo.set_active(0)
            self.conx_name.set_sensitive(False)
            self.connection_type_combo.set_sensitive(False)
            self.driver_settings_button.set_sensitive(self.conx_id != None)
    
        def update_connection(self,button):
            if self.conx_id == None:
                self.create_connection()
            else:
                self.delete_connection()
            
        def create_connection(self, *args):
                name = self.conx_name.get_text()
                conx_id = self.connection_type_combo.get_active_id()
                #verify conection name does not exist in database
                if self.db_manager.item_exists('Connections','Connection',name):
                    msg = 'Connection Name, {} Not Unique'.format(name)
                    self.parent.app.display_msg(None,msg)
                    return
                #add new connection 
                conx_name = self.conx_Typedata[int(conx_id)]
                col = '(Connection,ConnectionTypeID)'
                vals = [name,conx_id]
                #Create connection in mem db
                lastconx_id = self.db_manager.add_item_to_table('Connections',col,vals)
                self.conx_id = lastconx_id
                temp = self.db_manager.run_query('SELECT * FROM [Connections] WHERE Connection =?;''',(name,))
                self.conx_data = temp[0]
                #get conx parameters table name
                conx_tag_dbname = self.db_manager.run_query('''SELECT ID,ConnectionType From ConnectionTypes WHERE ID =?;''',(self.conx_data[2],))
                conx_tbl = (conx_tag_dbname[0][1]+'ConnectionsParams')
                #update enables of new connection row
                self.update_row(self.conx_data)
                #Copy connection to file db
                self.db_manager.copy_table('Connections')
                #Add default connection parameters row
                self.db_manager.add_default_param_item(conx_tbl,lastconx_id)
                self.db_manager.copy_table(conx_tbl)

        def delete_connection(self, *args):
            ################################ NEED TO BE ABLE TO ADJUST GRBL SETTINGS ###########################################
            name = self.conx_name.get_text()
            row = self.db_manager.run_query('SELECT ID FROM [Connections] WHERE Connection =?;''',(name,))

            confirmed = self.app.confirm(None, 'Are you sure you want to delete the connection', [])
            if row and confirmed:
                conx_id = row[0][0]
                #Delete Connection
                self.db_manager.delete_item_from_table('Connections','ID',conx_id)
                self.db_manager.delete_item_ext_table("public/mill.db",'Connections','ID',conx_id)
                self.content_area.remove(self)
                #Delete Tags of Connection
                self.db_manager.delete_item_from_table('Tags','ConnectionID',conx_id)
                self.db_manager.delete_item_ext_table("public/mill.db",'Tags','ConnectionID',conx_id)

        def open_driver_settings(self, button):
            if self.conx_id:
                    popup = ConnectionSettingsWindow(self.conx_id, db = self.db_manager, app = self.app )
                    self.parent.destroy()
            else:
                msg = 'Driver Settings Failed to Load {}'.format(self.conx_user_name)
                self.parent.app.display_msg(None,msg)

class ConnectionSettingsWindow(Gtk.Window):
        '''This is the base class for all the driver settings windows.
        Override the connection class's pack_connection_widgets to add driver specific content.
        Add the required methods for the wigets to adjust you connection's properties to you connection class and connect
        them in the pack_connection_widgets method'''
        def __init__(self, conx_id, db=None, app = None):
                super(ConnectionSettingsWindow, self).__init__()
                self.connection = None
                self.db_manager = db
                self.app = app
                self.conx_id = conx_id

                self.default_icon = './Public/images/logo.png' # should override this based on the connection opened
                self.set_property('window-position', Gtk.WindowPosition.CENTER)
                self.set_title('Connection Settings')
                self.set_border_width(30)
                self.set_default_size(1060, 700)
                self.set_keep_above(True)
                self.window_area = Gtk.Box(spacing = 10,orientation=Gtk.Orientation.VERTICAL)

                #get connection specific tag data
                c_data = self.db_manager.run_query('''SELECT Connection,ConnectionTypeID From Connections WHERE ID = ?;''',(self.conx_id,))
                self.conx_user_name = c_data[0][0]
                self.conx_type_id = c_data[0][1]
                c_type = self.db_manager.run_query('''SELECT ConnectionType From ConnectionTypes WHERE ID =?;''',(self.conx_type_id,))
                self.conx_type_name = (c_type[0][0])

                '''____Filling the Header____'''
                header = Gtk.Box(spacing=10,height_request=50)
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.default_icon, 40, -1, True)
                self.icon = Gtk.Image(pixbuf=p_buf)
                header.pack_start(self.icon, 0, 0, 0)

                h_lbl = "Connection Type : {} - {}".format(self.conx_type_name, self.conx_user_name)
                lbl = Gtk.Label(h_lbl)
                self.add_style(lbl,["font-30","font-bold"])
                header.pack_start(lbl, 1, 1, 0)
                b1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                b2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

                self.back_btn_box = Gtk.Box(halign = Gtk.Align.CENTER)
                but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Refresh.png', 40, -1, True)
                icon = Gtk.Image(pixbuf=p_buf)
                but_box.pack_start(icon, 0, 0, 0)
                label = Gtk.Label("Back")
                but_box.pack_start(label, 1, 0, 10)
                back_btn = Gtk.Button(width_request = 150, height_request = 50)
                back_btn.set_tooltip_text('Click to go to connections menu')
                self.add_style(back_btn,["ctrl-button","font-16","font-bold"])
                back_btn.add(but_box)
                back_btn.connect("clicked", self.open_connection_settings)
                self.back_btn_box.pack_end(back_btn, 0, 0, 0)

                b2.pack_start(self.back_btn_box, 0, 0, 0)
                btn_box = Gtk.Box()
                btn_box.set_spacing(10)
                b1.pack_start(b2,0,0,1)
                header.pack_start(b1, 0, 0, 0)
                self.window_area.pack_start(header, False, False, 0)
                '''____Filling Connection Properties Box____'''
 
                connection_enum = { 1: LocalSettingsBox,2: ModbusTCPSettingsBox,3: ModbusRTUSettingsBox, 4: EthernetIPSettingsBox, 5: ADSSettingsBox, 6: GRBLSettingsBox
                }
                #connection_enum = { 1: LocalSettingsBox, 2: ModbusTCPSettingsBox, 3: ModbusRTUSettingsBox, 4: EthernetIPSettingsBox, 5: Buff_EthernetIPSettingsBox, 6: TwinCatSettingsBox, 7: Buff_TwinCatSettingsBox, 8: CommDaqSettingsBox, 9: TT_DAQSettingsBox,}
                div = Gtk.Separator()
                div.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(120,120,120,1))
                self.window_area.pack_start(div, False, False, 0)

                '''____Filling the Scroll Layout____'''
                self.content_area = Gtk.Box(spacing = 10,orientation=Gtk.Orientation.VERTICAL,halign = Gtk.Align.CENTER)
                self.scroll = Gtk.ScrolledWindow()
                self.scroll.set_size_request(1000, 400)
                self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
                self.scroll.add(self.content_area)
                self.window_area.pack_start(self.scroll, True, True, 0)
                self.connect("delete_event", lambda *args: self.close_popup())
                self.connection_widget_box = connection_enum[self.conx_type_id](self.conx_id, db = self.db_manager, parent = self)
                self.content_area.pack_start(self.connection_widget_box, 1,1,0)
                '''______Footer_____'''
                div = Gtk.Separator()
                div.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(120,120,120,1))
                self.window_area.pack_start(div, False, False, 0)
                box = Gtk.Box(halign = Gtk.Align.CENTER)
                box = Gtk.Box()

                self.close_btn_box = Gtk.Box(halign = Gtk.Align.CENTER)
                but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Close.png', 40, -1, True)
                icon = Gtk.Image(pixbuf=p_buf)
                but_box.pack_start(icon, 0, 0, 0)
                label = Gtk.Label("Close")
                but_box.pack_start(label, 1, 0, 10)
                close_btn = Gtk.Button(width_request = 150, height_request = 50)
                close_btn.set_tooltip_text('Click to close popup')
                self.add_style(close_btn,["ctrl-button","font-16","font-bold"])
                close_btn.add(but_box)
                close_btn.connect("clicked", self.cancel)
                self.close_btn_box.pack_start(close_btn, 0, 0, 0)
                box.pack_end(self.close_btn_box, 0, 0, 1)
                self.close_button = close_btn # save a handle to it

                self.done_btn_box = Gtk.Box(halign = Gtk.Align.CENTER)    #hexpand = True
                but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Check.png', 40, -1, True)
                icon = Gtk.Image(pixbuf=p_buf)
                but_box.pack_start(icon, 0, 0, 0)
                label = Gtk.Label("Done")
                but_box.pack_start(label, 1, 0, 10)
                done_btn = Gtk.Button(width_request = 150, height_request = 50)
                done_btn.set_tooltip_text('Click to save and close popup')
                self.add_style(done_btn,["ctrl-button","font-16","font-bold"])
                done_btn.add(but_box)
                done_btn.connect("clicked", self.done)
                self.done_btn_box.pack_start(done_btn, 0, 0, 0)
                box.pack_end(self.done_btn_box, 0, 0, 1)
                self.done_button = done_btn # save a handle to it


                self.save_button_box = Gtk.Box(halign = Gtk.Align.CENTER)
                but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Save.png', 40, -1, True)
                icon = Gtk.Image(pixbuf=p_buf)
                but_box.pack_start(icon, 0, 0, 0)
                label = Gtk.Label("Save")
                but_box.pack_start(label, 1, 0, 10)
                self.save_button = Gtk.Button(width_request = 150, height_request = 50) # save a handle to it
                self.save_button.set_tooltip_text('Save updated connection settings')
                self.add_style(self.save_button,["ctrl-button","font-16","font-bold"])
                self.save_button.add(but_box)
                self.save_button.connect("clicked", self.save_settings)
                self.save_button_box.pack_start(self.save_button, 0, 0, 0)
                self.save_button.set_sensitive(False)
                box.pack_end(self.save_button_box, 0, 0, 1)
                self.window_area.pack_start(box, False, False, 0)

                self.add(self.window_area)
                self.show_all()

        def save_settings(self, button):
                #apply sent to connection type settings box 
                self.connection_widget_box.apply()
                self.save_button.set_sensitive(False)

        def done(self, button):
                self.save_settings(None)
                self.open_connection_settings()
                #self.close_popup()

        def cancel(self, button):
                self.close_popup()

        def close_popup(self,*args):
                self.destroy()

        def settings_not_applied(self, *args):
                self.save_button.set_sensitive(True)

        def open_connection_settings(self, *args):
                self.app.setup_connection()
                self.close_popup()
        
        def open_tag_list(self,conx_id, *args):
                self.app.setup_tags(None,conx_id)
                self.close_popup()
        
        def add_style(self, wid, style):
            #style should be a list
            sc = wid.get_style_context()
            for sty in style:
                sc.add_class(sty)

class LocalSettingsBox(Gtk.Box):
        def __init__(self, conx_id, db=None, parent = None):
                super(LocalSettingsBox, self).__init__()
                self.db_manager = db
                self.conx_id = conx_id
                self.parent = parent
                self.conx_icon = './Public/images/logo.png'
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.conx_icon, 80, -1, True)
                self.parent.icon.set_from_pixbuf(p_buf)

                # build content area here
                self.box = Gtk.Box(spacing=10,orientation=Gtk.Orientation.VERTICAL,halign = Gtk.Align.CENTER)

                # Connection Data
                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('No Connection Settings Exist',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-16","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                #Go to Tag List Popup
                tags_btn_box = Gtk.Box(halign = Gtk.Align.CENTER)    #hexpand = True
                but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Tag.png', 40, -1, True)
                icon = Gtk.Image(pixbuf=p_buf)
                but_box.pack_start(icon, 0, 0, 0)
                label = Gtk.Label("Tags List")
                but_box.pack_start(label, 1, 0, 10)
                tags_btn = Gtk.Button(width_request = 150, height_request = 50)
                tags_btn.set_tooltip_text('Click to open Tags popup')
                self.parent.add_style(tags_btn,["ctrl-button","font-16","font-bold"])
                tags_btn.add(but_box)
                tags_btn.connect("clicked", self.open_tags_list)
                tags_btn_box.pack_start(tags_btn, 0, 0, 0)
                self.box.pack_start(tags_btn_box, 0, 0, 1)

                self.pack_start(self.box, 0, 0, 0)

        def open_tags_list(self,*args):
                self.parent.open_tag_list(self.conx_id)

class GRBLSettingsBox(Gtk.Box):
    ################################## WORK ON ADDING GRBL TAGS SO THE CONNECTION IS THE SAME AS THE REST ###############################################
        def __init__(self, conx_id, db=None, parent = None):
                super(GRBLSettingsBox, self).__init__()
                self.db_manager = db
                self.conx_id = conx_id
                self.parent = parent
                self.conx_icon = './Public/images/logo.png'
                self.db_table = 'GRBLConnectionsParams'
                self.db_columns = ["Port","PendantPort","Pollrate","AutoConnect","Status"]
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.conx_icon, 80, -1, True)
                self.parent.icon.set_from_pixbuf(p_buf)
                self.conx_active = 0 # False
                if self.conx_id:
                        col_list = ','.join(self.db_columns)
                        sql = "SELECT {lst} FROM [{tbl}] WHERE ID =?;".format( lst =col_list,tbl = self.db_table)
                        c_data = self.db_manager.run_query(sql,[self.conx_id]) 
                self.serial_port = c_data[0][0]
                self.pendant_port = c_data[0][1]
                self.pollrate = c_data[0][2]
                self.a_connect = c_data[0][3]
                self.conx_active = c_data[0][4]

                # build content area here
                self.box = Gtk.Box(spacing=10,orientation=Gtk.Orientation.VERTICAL,halign = Gtk.Align.CENTER)

                # Connection Data
                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Poll Rate (s)',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.poll_rate_spinner = Gtk.SpinButton(adjustment=Gtk.Adjustment(self.pollrate,0.001, 2 ** 32, 1, 10, 0), numeric=True, digits=3,width_request = 150)
                bx.pack_start(self.poll_rate_spinner, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Serial Port',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.serial_port = self.serial_port.replace("COM","")
                self.port_spinner = Gtk.SpinButton(adjustment=Gtk.Adjustment(int(self.serial_port), 0, 255, 1, 2, 0), numeric=True,width_request = 150)
                bx.pack_start(self.port_spinner, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Pendant Port',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.pendant_port = self.pendant_port.replace("COM","")
                self.pendant_num = Gtk.SpinButton(adjustment=Gtk.Adjustment(int(self.pendant_port), 0, 255, 1, 2, 0), numeric=True,width_request = 150)
                bx.pack_start(self.pendant_num, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Auto Connect',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                bh = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,halign = Gtk.Align.CENTER,width_request = 150)
                self.auto_conn_cb = Gtk.CheckButton(width_request = 30,height_request = 30)
                self.parent.add_style(self.auto_conn_cb,["check-box"])
                if self.a_connect == 1:
                    self.auto_conn_cb.set_active(True)
                else:
                    self.auto_conn_cb.set_active(False)
                bh.pack_start(self.auto_conn_cb,0,0,0)
                bx.pack_start(bh, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                #Go to Tag List Popup
                tags_btn_box = Gtk.Box(halign = Gtk.Align.CENTER)    #hexpand = True
                but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Tag.png', 40, -1, True)
                icon = Gtk.Image(pixbuf=p_buf)
                but_box.pack_start(icon, 0, 0, 0)
                label = Gtk.Label("Tags List")
                but_box.pack_start(label, 1, 0, 10)
                tags_btn = Gtk.Button(width_request = 150, height_request = 50)
                tags_btn.set_tooltip_text('Click to open Tags popup')
                self.parent.add_style(tags_btn,["ctrl-button","font-16","font-bold"])
                tags_btn.add(but_box)
                tags_btn.connect("clicked", self.open_tags_list)
                tags_btn_box.pack_start(tags_btn, 0, 0, 0)
                self.box.pack_start(tags_btn_box, 0, 0, 1)
                
                self.poll_rate_spinner.connect("changed", self.parent.settings_not_applied)
                self.port_spinner.connect("changed", self.parent.settings_not_applied)
                self.pendant_num.connect("changed", self.parent.settings_not_applied)
                self.auto_conn_cb.connect("toggled",self.parent.settings_not_applied)
                
                self.pack_start(self.box, 0, 0, 0)

        def apply(self,*args):
            a_connect = self.auto_conn_cb.get_active()
            col_name_str = ''
            for i in range(len(self.db_columns)):
                col_name_str += self.db_columns[i] +' = ?'
                if len(self.db_columns)>=1 and (i+1) != len(self.db_columns): 
                    col_name_str+=','
            sql = "UPDATE {t} SET {col} WHERE ID = (?);".format(t=self.db_table,col=col_name_str)
            self.db_manager.run_query(sql,[str('COM'+str(int(self.port_spinner.get_value()))),
                                                                        str('COM'+str(int(self.pendant_num.get_value()))),
                                                                        self.poll_rate_spinner.get_value(),
                                                                        a_connect,self.conx_active,self.conx_id])
            self.db_manager.copy_table(self.db_table)
        
        def open_tags_list(self,*args):
                self.parent.open_tag_list(self.conx_id)

class ModbusTCPSettingsBox(Gtk.Box):
        def __init__(self, conx_id, db=None, parent = None):
                super(ModbusTCPSettingsBox, self).__init__()
                self.db_manager = db
                self.conx_id = conx_id
                self.parent = parent
                self.conx_icon = './Public/images/logo.png'
                self.db_table = 'ModbusTCPConnectionsParams'
                self.db_columns = ["Host","Port","StationID","Pollrate","AutoConnect","Status"]
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.conx_icon, 80, -1, True)
                self.parent.icon.set_from_pixbuf(p_buf)
                self.conx_active = 0 # False
                if self.conx_id:
                        col_list = ','.join(self.db_columns)
                        sql = "SELECT {lst} FROM [{tbl}] WHERE ID =?;".format( lst =col_list,tbl = self.db_table)
                        c_data = self.db_manager.run_query(sql,[self.conx_id]) 
                self.host_val = c_data[0][0]
                self.port_val = c_data[0][1]
                self.stationID_val = c_data[0][2]
                self.pollrate = c_data[0][3]
                self.a_connect = c_data[0][4]
                self.conx_active = c_data[0][5]

                # build content area here
                self.box = Gtk.Box(spacing=10,orientation=Gtk.Orientation.VERTICAL,halign = Gtk.Align.CENTER)

                # Connection Data
                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Poll Rate (s)',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.poll_rate_spinner = Gtk.SpinButton(adjustment=Gtk.Adjustment(self.pollrate,0.001, 2 ** 32, 1, 10, 0), numeric=True, digits=3,width_request = 150)
                bx.pack_start(self.poll_rate_spinner, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Host',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.host_entry = Gtk.Entry(text=str(self.host_val))
                bx.pack_start(self.host_entry, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Port',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.port_spinner = Gtk.SpinButton(adjustment=Gtk.Adjustment(int(self.port_val),-2 ** 32, 2 ** 32, 1, 10, 0), numeric=True, digits=0,width_request = 150)
                bx.pack_start(self.port_spinner, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Unit Number',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.stationID_num = Gtk.SpinButton(adjustment=Gtk.Adjustment(int(self.stationID_val), 0, 255, 1, 2, 0), numeric=True,width_request = 150)
                bx.pack_start(self.stationID_num, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Auto Connect',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                bh = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,halign = Gtk.Align.CENTER,width_request = 150)
                self.auto_conn_cb = Gtk.CheckButton(width_request = 30,height_request = 30)
                self.parent.add_style(self.auto_conn_cb,["check-box"])
                if self.a_connect == 1:
                    self.auto_conn_cb.set_active(True)
                else:
                    self.auto_conn_cb.set_active(False)
                bh.pack_start(self.auto_conn_cb,0,0,0)
                bx.pack_start(bh, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                #Go to Tag List Popup
                tags_btn_box = Gtk.Box(halign = Gtk.Align.CENTER)    #hexpand = True
                but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Tag.png', 40, -1, True)
                icon = Gtk.Image(pixbuf=p_buf)
                but_box.pack_start(icon, 0, 0, 0)
                label = Gtk.Label("Tags List")
                but_box.pack_start(label, 1, 0, 10)
                tags_btn = Gtk.Button(width_request = 150, height_request = 50)
                tags_btn.set_tooltip_text('Click to open Tags popup')
                self.parent.add_style(tags_btn,["ctrl-button","font-16","font-bold"])
                tags_btn.add(but_box)
                tags_btn.connect("clicked", self.open_tags_list)
                tags_btn_box.pack_start(tags_btn, 0, 0, 0)
                self.box.pack_start(tags_btn_box, 0, 0, 1)
                
                self.poll_rate_spinner.connect("changed", self.parent.settings_not_applied)
                self.host_entry.connect("changed", self.parent.settings_not_applied)
                self.port_spinner.connect("changed", self.parent.settings_not_applied)
                self.stationID_num.connect("changed", self.parent.settings_not_applied)
                self.auto_conn_cb.connect("toggled",self.parent.settings_not_applied)
                
                self.pack_start(self.box, 0, 0, 0)

        def apply(self,*args):
            a_connect = self.auto_conn_cb.get_active()
            col_name_str = ''
            for i in range(len(self.db_columns)):
                col_name_str += self.db_columns[i] +' = ?'
                if len(self.db_columns)>=1 and (i+1) != len(self.db_columns): 
                    col_name_str+=','
            sql = "UPDATE {t} SET {col} WHERE ID = (?);".format(t=self.db_table,col=col_name_str)
            self.db_manager.run_query(sql,[self.host_entry.get_text(),
                                                                        self.port_spinner.get_value(),
                                                                        self.stationID_num.get_value(),
                                                                        self.poll_rate_spinner.get_value(),
                                                                        a_connect,self.conx_active,self.conx_id])
            self.db_manager.copy_table(self.db_table)

        def open_tags_list(self,*args):
                self.parent.open_tag_list(self.conx_id)

class EthernetIPSettingsBox(Gtk.Box):
        def __init__(self, conx_id, db=None, parent = None):
                super(EthernetIPSettingsBox, self).__init__()
                self.db_manager = db
                self.conx_id = conx_id
                self.parent = parent
                self.conx_icon = './Public/images/logo.png'
                self.db_table = 'EthernetIPConnectionsParams'
                self.db_columns = ["Host","Port","StationID","Pollrate","AutoConnect","Status"]
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.conx_icon, 80, -1, True)
                self.parent.icon.set_from_pixbuf(p_buf)
                self.conx_active = 0 # False
                if self.conx_id:
                        col_list = ','.join(self.db_columns)
                        sql = "SELECT {lst} FROM [{tbl}] WHERE ID =?;".format( lst =col_list,tbl = self.db_table)
                        c_data = self.db_manager.run_query(sql,[self.conx_id]) 
                self.host_val = c_data[0][0]
                self.port_val = c_data[0][1]
                self.stationID_val = c_data[0][2]
                self.pollrate = c_data[0][3]
                self.a_connect = c_data[0][4]
                self.conx_active = c_data[0][5]

                # build content area here
                self.box = Gtk.Box(spacing=10,orientation=Gtk.Orientation.VERTICAL,halign = Gtk.Align.CENTER)

                # Connection Data
                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Poll Rate (s)',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.poll_rate_spinner = Gtk.SpinButton(adjustment=Gtk.Adjustment(self.pollrate,0.001, 2 ** 32, 1, 10, 0), numeric=True, digits=3,width_request = 150)
                bx.pack_start(self.poll_rate_spinner, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Host',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.host_entry = Gtk.Entry(text=str(self.host_val))
                bx.pack_start(self.host_entry, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Port',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.port_spinner = Gtk.SpinButton(adjustment=Gtk.Adjustment(int(self.port_val),-2 ** 32, 2 ** 32, 1, 10, 0), numeric=True, digits=0,width_request = 150)
                bx.pack_start(self.port_spinner, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Unit Number',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.stationID_num = Gtk.SpinButton(adjustment=Gtk.Adjustment(int(self.stationID_val), 0, 255, 1, 2, 0), numeric=True,width_request = 150)
                bx.pack_start(self.stationID_num, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Auto Connect',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                bh = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,halign = Gtk.Align.CENTER,width_request = 150)
                self.auto_conn_cb = Gtk.CheckButton(width_request = 30,height_request = 30)
                self.parent.add_style(self.auto_conn_cb,["check-box"])
                if self.a_connect == 1:
                    self.auto_conn_cb.set_active(True)
                else:
                    self.auto_conn_cb.set_active(False)
                bh.pack_start(self.auto_conn_cb,0,0,0)
                bx.pack_start(bh, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                #Go to Tag List Popup
                tags_btn_box = Gtk.Box(halign = Gtk.Align.CENTER)    #hexpand = True
                but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Tag.png', 40, -1, True)
                icon = Gtk.Image(pixbuf=p_buf)
                but_box.pack_start(icon, 0, 0, 0)
                label = Gtk.Label("Tags List")
                but_box.pack_start(label, 1, 0, 10)
                tags_btn = Gtk.Button(width_request = 150, height_request = 50)
                tags_btn.set_tooltip_text('Click to open Tags popup')
                self.parent.add_style(tags_btn,["ctrl-button","font-16","font-bold"])
                tags_btn.add(but_box)
                tags_btn.connect("clicked", self.open_tags_list)
                tags_btn_box.pack_start(tags_btn, 0, 0, 0)
                self.box.pack_start(tags_btn_box, 0, 0, 1)
                
                self.poll_rate_spinner.connect("changed", self.parent.settings_not_applied)
                self.host_entry.connect("changed", self.parent.settings_not_applied)
                self.port_spinner.connect("changed", self.parent.settings_not_applied)
                self.stationID_num.connect("changed", self.parent.settings_not_applied)
                self.auto_conn_cb.connect("toggled",self.parent.settings_not_applied)
                
                self.pack_start(self.box, 0, 0, 0)

        def open_tags_list(self,*args):
                self.parent.open_tag_list(self.conx_id)

        def apply(self,*args):
            a_connect = self.auto_conn_cb.get_active()
            col_name_str = ''
            for i in range(len(self.db_columns)):
                col_name_str += self.db_columns[i] +' = ?'
                if len(self.db_columns)>=1 and (i+1) != len(self.db_columns): 
                    col_name_str+=','
            sql = "UPDATE {t} SET {col} WHERE ID = (?);".format(t=self.db_table,col=col_name_str)
            self.db_manager.run_query(sql,[self.host_entry.get_text(),
                                                                         self.port_spinner.get_value(),
                                                                         self.stationID_num.get_value(),
                                                                         self.poll_rate_spinner.get_value(),
                                                                         a_connect,self.conx_active,self.conx_id])
            self.db_manager.copy_table(self.db_table)

class ModbusRTUSettingsBox(Gtk.Box):
        def __init__(self, conx_id, db=None, parent = None):
                super(ModbusRTUSettingsBox, self).__init__()
                self.db_manager = db
                self.conx_id = conx_id
                self.parent = parent
                self.conx_icon = './Public/images/logo.png'
                self.baud_list = ['1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200']
                self.db_table = 'ModbusRTUConnectionsParams'
                self.available_bytes = ['8', '7']
                self.available_stopbits = ['1', '2']
                self.available_parity = ['N', 'O', 'E']
                self.db_columns = ["SerialPort","StationID","Pollrate","BaudRate","Timeout","StopBit","Parity","ByteSize","Retries","AutoConnect","Status"]
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.conx_icon, 80, -1, True)
                self.parent.icon.set_from_pixbuf(p_buf)
                self.conx_active = 0 # False
                if self.conx_id:
                        col_list = ','.join(self.db_columns)
                        sql = "SELECT {lst} FROM [{tbl}] WHERE ID =?;".format( lst =col_list,tbl = self.db_table)
                        c_data = self.db_manager.run_query(sql,[self.conx_id]) 

                self.serial_port = c_data[0][0]
                self.station_id = c_data[0][1]
                self.pollrate = c_data[0][2]
                self.baudrate = c_data[0][3]
                self.time_out = c_data[0][4]
                self.stop_bits = c_data[0][5]
                self.parity = c_data[0][6]
                self.byte_size = c_data[0][7]
                self.retries = c_data[0][8]
                self.a_connect = c_data[0][9]
                self.conx_active = c_data[0][10]

                # build content area here
                self.box = Gtk.Box(spacing=10,orientation=Gtk.Orientation.VERTICAL,halign = Gtk.Align.CENTER)

                # Connection Data
                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Poll Rate (s)',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.poll_rate_spinner = Gtk.SpinButton(adjustment=Gtk.Adjustment(self.pollrate,0.001, 2 ** 32, 1, 10, 0), numeric=True, digits=3,width_request = 150)
                bx.pack_start(self.poll_rate_spinner, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)
                

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Serial Port',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.serial_port = self.serial_port.replace("COM","")
                self.serial_port_spinner = Gtk.SpinButton(adjustment=Gtk.Adjustment(int(self.serial_port), 0, 255, 1, 2, 0), numeric=True,width_request = 150)
                bx.pack_start(self.serial_port_spinner, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Unit Number',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.stationID_num = Gtk.SpinButton(adjustment=Gtk.Adjustment(int(self.station_id), 0, 255, 1, 2, 0), numeric=True,width_request = 150)
                bx.pack_start(self.stationID_num, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Baud Rate',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.br_entry = Gtk.ComboBoxText(width_request = 150)
                temp = 0
                for baudrate in self.baud_list:
                        self.br_entry.append_text(baudrate)
                        if str(self.baudrate) == baudrate:
                                self.br_entry.set_active(temp)
                        temp += 1
                bx.pack_start(self.br_entry, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Byte Size',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.b_size = Gtk.ComboBoxText(width_request = 150)
                temp = 0
                for size in self.available_bytes:
                        self.b_size.append_text(size)
                        if str(self.byte_size) == size:
                                self.b_size.set_active(temp)
                        temp += 1
                bx.pack_start(self.b_size, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Stop Bits',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.s_bit = Gtk.ComboBoxText(width_request = 150)
                temp = 0
                for bits in self.available_stopbits:
                        self.s_bit.append_text(bits)
                        if str(self.stop_bits) == bits:
                                self.s_bit.set_active(temp)
                        temp += 1
                bx.pack_start(self.s_bit, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Parity',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.par_box = Gtk.ComboBoxText(width_request = 150)
                temp = 0
                for bits in self.available_parity:
                        self.par_box.append_text(bits)
                        if str(self.parity) == bits:
                                self.par_box.set_active(temp)
                        temp += 1
                bx.pack_start(self.par_box, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Timeout (s)',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.t_out = Gtk.SpinButton(adjustment=Gtk.Adjustment(float(self.time_out), 0, 100.0, 1, 2, 0), numeric=True, digits=1,width_request = 150)
                bx.pack_start(self.t_out, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Retries',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.retry_spin = Gtk.SpinButton(adjustment=Gtk.Adjustment(float(self.retries), 0, 100.0, 1, 2, 0), numeric=True,width_request = 150)
                bx.pack_start(self.retry_spin, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Auto Connect',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                bh = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,halign = Gtk.Align.CENTER,width_request = 150)
                self.auto_conn_cb = Gtk.CheckButton(width_request = 30,height_request = 30)
                self.parent.add_style(self.auto_conn_cb,["check-box"])
                if self.a_connect == 1:
                    self.auto_conn_cb.set_active(True)
                else:
                    self.auto_conn_cb.set_active(False)
                bh.pack_start(self.auto_conn_cb,0,0,0)
                bx.pack_start(bh, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                #Go to Tag List Popup
                tags_btn_box = Gtk.Box(halign = Gtk.Align.CENTER)    #hexpand = True
                but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Tag.png', 40, -1, True)
                icon = Gtk.Image(pixbuf=p_buf)
                but_box.pack_start(icon, 0, 0, 0)
                label = Gtk.Label("Tags List")
                but_box.pack_start(label, 1, 0, 10)
                tags_btn = Gtk.Button(width_request = 150, height_request = 50)
                tags_btn.set_tooltip_text('Click to open Tags popup')
                self.parent.add_style(tags_btn,["ctrl-button","font-16","font-bold"])
                tags_btn.add(but_box)
                tags_btn.connect("clicked", self.open_tags_list)
                tags_btn_box.pack_start(tags_btn, 0, 0, 0)
                self.box.pack_start(tags_btn_box, 0, 0, 1)

                self.serial_port_spinner.connect("changed", self.parent.settings_not_applied)
                self.stationID_num.connect("changed", self.parent.settings_not_applied)
                self.poll_rate_spinner.connect("changed", self.parent.settings_not_applied)
                self.br_entry.connect("changed", self.parent.settings_not_applied)
                self.t_out.connect("changed", self.parent.settings_not_applied)
                self.s_bit.connect("changed", self.parent.settings_not_applied)
                self.par_box.connect("changed", self.parent.settings_not_applied)
                self.b_size.connect("changed", self.parent.settings_not_applied)
                self.retry_spin.connect("changed", self.parent.settings_not_applied)
                self.auto_conn_cb.connect("toggled",self.parent.settings_not_applied)
                
                self.pack_start(self.box, 0, 0, 0)


        def apply(self,*args):
            a_connect = self.auto_conn_cb.get_active()
            col_name_str = ''
            for i in range(len(self.db_columns)):
                col_name_str += self.db_columns[i] +' = ?'
                if len(self.db_columns)>=1 and (i+1) != len(self.db_columns): 
                    col_name_str+=','
            sql = "UPDATE {t} SET {col} WHERE ID = (?);".format(t=self.db_table,col=col_name_str)
            self.db_manager.run_query(sql,[str('COM'+str(int(self.serial_port_spinner.get_value()))),
                                                                         self.stationID_num.get_value(),
                                                                         self.poll_rate_spinner.get_value(),
                                                                         self.br_entry.get_active_text(),
                                                                         self.t_out.get_value(),
                                                                         self.s_bit.get_active_text(),
                                                                         self.par_box.get_active_text(),
                                                                         self.b_size.get_active_text(),
                                                                         self.retry_spin.get_value(),
                                                                         a_connect,self.conx_active,self.conx_id])
            self.db_manager.copy_table(self.db_table)

        def open_tags_list(self,*args):
                self.parent.open_tag_list(self.conx_id)

class ADSSettingsBox(Gtk.Box):
        def __init__(self, conx_id, db=None, parent = None):
                super(ADSSettingsBox, self).__init__()
                self.db_manager = db
                self.conx_id = conx_id
                self.parent = parent
                self.conx_icon = './Public/images/logo.png'
                self.db_table = 'ADSConnectionsParams'
                self.db_columns = ["Host","TargetAMS","SourceAMS","Port","Pollrate","AutoConnect","Status"]
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.conx_icon, 80, -1, True)
                self.parent.icon.set_from_pixbuf(p_buf)
                self.conx_active = 0 # False
                if self.conx_id:
                        col_list = ','.join(self.db_columns)
                        sql = "SELECT {lst} FROM [{tbl}] WHERE ID =?;".format( lst =col_list,tbl = self.db_table)
                        c_data = self.db_manager.run_query(sql,[self.conx_id]) 

                self.host_val = c_data[0][0]
                self.t_AMS_val = c_data[0][1]
                self.s_AMS_val = c_data[0][2]
                self.port_val = c_data[0][3]
                self.pollrate = c_data[0][4]
                self.a_connect = c_data[0][5]
                self.conx_active = c_data[0][6]

                # build content area here
                self.box = Gtk.Box(spacing=10,orientation=Gtk.Orientation.VERTICAL,halign = Gtk.Align.CENTER)

                # Connection Data
                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Poll Rate (s)',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.poll_rate_spinner = Gtk.SpinButton(adjustment=Gtk.Adjustment(self.pollrate,0.001, 2 ** 32, 1, 10, 0), numeric=True, digits=3,width_request = 150)
                bx.pack_start(self.poll_rate_spinner, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Host',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.host_entry = Gtk.Entry(text=str(self.host_val))
                bx.pack_start(self.host_entry, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('TargetAMS',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.t_AMS_entry = Gtk.Entry(text=str(self.t_AMS_val))
                bx.pack_start(self.t_AMS_entry, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('SourceAMS',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.s_AMS_entry = Gtk.Entry(text=str(self.s_AMS_val))
                bx.pack_start(self.s_AMS_entry, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Port',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                self.port_spinner = Gtk.SpinButton(adjustment=Gtk.Adjustment(int(self.port_val),-2 ** 32, 2 ** 32, 1, 10, 0), numeric=True, digits=0,width_request = 150)
                bx.pack_start(self.port_spinner, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                l = Gtk.Label('Auto Connect',width_request = 200)
                self.parent.add_style(l,["text-gray-color","font-14","font-bold"])
                bx.pack_start(l, 1, 1, 0)
                bh = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,halign = Gtk.Align.CENTER,width_request = 150)
                self.auto_conn_cb = Gtk.CheckButton(width_request = 30,height_request = 30)
                self.parent.add_style(self.auto_conn_cb,["check-box"])
                if self.a_connect == 1:
                    self.auto_conn_cb.set_active(True)
                else:
                    self.auto_conn_cb.set_active(False)
                bh.pack_start(self.auto_conn_cb,0,0,0)
                bx.pack_start(bh, 1, 1, 0)
                self.box.pack_start(bx, 0, 0, 0)

                #Go to Tag List Popup
                tags_btn_box = Gtk.Box(halign = Gtk.Align.CENTER)    #hexpand = True
                but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Tag.png', 40, -1, True)
                icon = Gtk.Image(pixbuf=p_buf)
                but_box.pack_start(icon, 0, 0, 0)
                label = Gtk.Label("Tags List")
                but_box.pack_start(label, 1, 0, 10)
                tags_btn = Gtk.Button(width_request = 150, height_request = 50)
                tags_btn.set_tooltip_text('Click to open Tags popup')
                self.parent.add_style(tags_btn,["ctrl-button","font-16","font-bold"])
                tags_btn.add(but_box)
                tags_btn.connect("clicked", self.open_tags_list)
                tags_btn_box.pack_start(tags_btn, 0, 0, 0)
                self.box.pack_start(tags_btn_box, 0, 0, 1)
                
                self.poll_rate_spinner.connect("changed", self.parent.settings_not_applied)
                self.host_entry.connect("changed", self.parent.settings_not_applied)
                self.t_AMS_entry.connect("changed", self.parent.settings_not_applied)
                self.s_AMS_entry.connect("changed", self.parent.settings_not_applied)
                self.port_spinner.connect("changed", self.parent.settings_not_applied)
                self.auto_conn_cb.connect("toggled",self.parent.settings_not_applied)
                
                self.pack_start(self.box, 0, 0, 0)

        def apply(self,*args):
            a_connect = self.auto_conn_cb.get_active()
            col_name_str = ''
            for i in range(len(self.db_columns)):
                col_name_str += self.db_columns[i] +' = ?'
                if len(self.db_columns)>=1 and (i+1) != len(self.db_columns): 
                    col_name_str+=','
            sql = "UPDATE {t} SET {col} WHERE ID = (?);".format(t=self.db_table,col=col_name_str)
            self.db_manager.run_query(sql,[self.host_entry.get_text(),
                                                                         self.t_AMS_entry.get_text(),
                                                                         self.s_AMS_entry.get_text(),
                                                                         self.port_spinner.get_value(),
                                                                         self.poll_rate_spinner.get_value(),
                                                                         a_connect,self.conx_active,self.conx_id])
            self.db_manager.copy_table(self.db_table)

        def open_tags_list(self,*args):
                self.parent.open_tag_list(self.conx_id)

class TagSettingsWindow(Gtk.Window):
    '''This is the tag settings/parameters windows.
    '''
    def __init__(self, t_id , conx_id , db=None, app = None, new_tag = False):
            super(TagSettingsWindow, self).__init__()
            self.connection = None
            self.db_manager = db
            self.app = app
            self.conx_id = conx_id
            self.tag_id = t_id
            self.new_tag = new_tag

            self.default_icon = './Public/images/logo.png' 
            self.set_property('window-position', Gtk.WindowPosition.CENTER)
            self.set_title('Tag Settings')
            self.set_border_width(30)
            self.set_default_size(1660, 700)
            self.connect("delete_event", lambda *args: self.close_popup())
            self.set_keep_above(True)
            self.window_area = Gtk.Box(spacing = 10,orientation=Gtk.Orientation.VERTICAL)

            #get connection specific tag data
            c_data = self.db_manager.run_query('''SELECT Connection,ConnectionTypeID From Connections WHERE ID = ?;''',(self.conx_id,))
            self.conx_user_name = c_data[0][0]
            self.conx_type_id = c_data[0][1]
            c_type = self.db_manager.run_query('''SELECT ConnectionType From ConnectionTypes WHERE ID =?;''',(self.conx_type_id,))
            self.conx_type_name = (c_type[0][0])
            self.tag_params_db_name = self.conx_type_name+'TagParams'

            #get tags list database
            conx_tag_dbname = self.db_manager.run_query('''SELECT ID,ConnectionType From ConnectionTypes WHERE ID =?;''',(self.conx_type_id,))
            self.db_table = (conx_tag_dbname[0][1]+'Tags')

            #getting specific tag data
            sql = "SELECT * FROM [{tbl}] WHERE ID =?;".format( tbl = self.db_table)
            self.tag_row = self.db_manager.run_query(sql,[self.tag_id])

            #get all tags in connection for list
            sql = "SELECT ID,Tag FROM [{tbl}];".format( tbl = self.db_table)
            tags_list = self.db_manager.run_query(sql)

            '''____Filling the Header____'''
            header = Gtk.Box(spacing=10,height_request = 50)
            p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.default_icon, 60, -1, True)
            self.icon = Gtk.Image(pixbuf=p_buf)
            header.pack_start(self.icon, 0, 0, 0)

            h_lbl = "Tag Settings : {}".format('Configure Tags')
            lbl = Gtk.Label(h_lbl)
            self.add_style(lbl,["font-30","font-bold"])
            header.pack_start(lbl, 1, 1, 0)
            b1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            b2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

            self.back_btn_box = Gtk.Box(halign = Gtk.Align.CENTER)
            but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Refresh.png', 40, -1, True)
            icon = Gtk.Image(pixbuf=p_buf)
            but_box.pack_start(icon, 0, 0, 0)
            label = Gtk.Label("Back")
            but_box.pack_start(label, 1, 0, 10)
            back_btn = Gtk.Button(width_request = 150, height_request = 50)
            back_btn.set_tooltip_text('Click to go to back')
            self.add_style(back_btn,["ctrl-button","font-16","font-bold"])
            back_btn.add(but_box)
            back_btn.connect("clicked", self.open_tag_list)
            self.back_btn_box.pack_end(back_btn, 0, 0, 0)

            b2.pack_start(self.back_btn_box, 0, 0, 0)
            btn_box = Gtk.Box()
            btn_box.set_spacing(10)
            b1.pack_start(b2,0,0,1)
            header.pack_start(b1, 0, 0, 0)
            self.window_area.pack_start(header, False, False, 0)
            div = Gtk.Separator()
            div.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(120,120,120,1))
            self.window_area.pack_start(div, False, False, 0)

            '''____Filling the Content Area____'''

            # add header subtitle
            sub_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,halign = Gtk.Align.CENTER)
            bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,halign = Gtk.Align.CENTER)
            l = Gtk.Label(label = 'Available Tags:',width_request = 150)
            self.add_style(l,["text-gray-color","font-20","font-bold"])
            bx.pack_start(l, 0, 0, 0)
            self.tag_select = Gtk.ComboBoxText(width_request = 200,popup_fixed_width=True, wrap_width = 3)
            lst = []
            temp = 0
            for row in tags_list:
                    self.tag_select.append_text(row[1])
                    if self.tag_id != None:
                        if str(self.tag_row[0][1]) == row[1]:
                                self.tag_select.set_active(temp)
                        temp += 1
                    else:
                        self.tag_select.set_active(temp)
            bx.pack_start(self.tag_select, 0, 0, 0)
            sub_title.pack_start(bx, 0, 0, 0)
            self.window_area.pack_start(sub_title, False, False, 0)

            #add tag confirguration
            self.content_area = Gtk.Box(spacing = 10,orientation=Gtk.Orientation.VERTICAL, height_request = 400, halign = Gtk.Align.CENTER)
            self.window_area.pack_start(self.content_area, False,False, 0)
            self.update_tag()
            self.tag_select.connect("changed", self.tag_changed)


            '''______Footer_____'''
            div = Gtk.Separator()
            div.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(120,120,120,1))
            self.window_area.pack_start(div, False, False, 0)
            box = Gtk.Box(halign = Gtk.Align.CENTER)

            self.close_btn_box = Gtk.Box(halign = Gtk.Align.CENTER)
            but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Close.png', 40, -1, True)
            icon = Gtk.Image(pixbuf=p_buf)
            but_box.pack_start(icon, 0, 0, 0)
            label = Gtk.Label("Cancel")
            but_box.pack_start(label, 1, 0, 10)
            close_btn = Gtk.Button(width_request = 150, height_request = 50)
            close_btn.set_tooltip_text('Click to close popup')
            self.add_style(close_btn,["ctrl-button","font-16","font-bold"])
            close_btn.add(but_box)
            close_btn.connect("clicked", self.cancel)
            self.close_btn_box.pack_start(close_btn, 0, 0, 0)
            box.pack_end(self.close_btn_box, 0, 0, 1)
            self.close_button = close_btn # save a handle to it

            self.done_btn_box = Gtk.Box(halign = Gtk.Align.CENTER)    #hexpand = True
            but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Check.png', 40, -1, True)
            icon = Gtk.Image(pixbuf=p_buf)
            but_box.pack_start(icon, 0, 0, 0)
            label = Gtk.Label("Done")
            but_box.pack_start(label, 1, 0, 10)
            done_btn = Gtk.Button(width_request = 150, height_request = 50)
            done_btn.set_tooltip_text('Click to save and close popup')
            self.add_style(done_btn,["ctrl-button","font-16","font-bold"])
            done_btn.add(but_box)
            done_btn.connect("clicked", self.done)
            self.done_btn_box.pack_start(done_btn, 0, 0, 0)
            box.pack_end(self.done_btn_box, 0, 0, 1)
            self.done_button = done_btn # save a handle to it


            self.save_button_box = Gtk.Box(halign = Gtk.Align.CENTER)
            but_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Save.png', 40, -1, True)
            icon = Gtk.Image(pixbuf=p_buf)
            but_box.pack_start(icon, 0, 0, 0)
            label = Gtk.Label("Save")
            but_box.pack_start(label, 1, 0, 10)
            self.save_button = Gtk.Button(width_request = 150, height_request = 50) # save a handle to it
            self.save_button.set_tooltip_text('Save updated connection settings')
            self.add_style(self.save_button,["ctrl-button","font-16","font-bold"])
            self.save_button.add(but_box)
            self.save_button.connect("clicked", self.save_settings)
            self.save_button_box.pack_start(self.save_button, 0, 0, 0)
            self.save_button.set_sensitive(False)
            box.pack_end(self.save_button_box, 0, 0, 1)
            self.window_area.pack_start(box, False, False, 0)

            self.add(self.window_area)
            self.show_all()

    def tag_changed(self,*args):
            tag_name = self.tag_select.get_active_text()
            #getting specific tag data
            sql = "SELECT ID FROM [{tbl}] WHERE Tag =?;".format( tbl = self.db_table)
            t_id = self.db_manager.run_query(sql,[tag_name])
            self.tag_id = t_id[0][0]
            self.update_tag()

    def update_tag(self,*args):
            for wid in self.content_area.get_children():
                self.content_area.remove(wid)
            self.tag_widget_box = TagSettingsBox(self.tag_id,self.conx_id,db = self.db_manager,parent = self,app = self.app)
            self.content_area.pack_start(self.tag_widget_box, 1,1,0)
            self.show_all()

    def save_settings(self, button):
            #apply sent to connection type settings box 
            self.tag_widget_box.apply()
            self.save_button.set_sensitive(False)

    def done(self, button):
            self.save_settings(None)
            self.open_tag_list()

    def cancel(self, button):
        #If new tag was just added and user cancels then delete tag
        if self.new_tag:
            self.db_manager.delete_item_from_table('Tags','ID',self.tag_id)
            self.db_manager.delete_item_ext_table("public/mill.db",'Tags','ID',self.tag_id)
            self.db_manager.delete_item_from_table(self.tag_params_db_name,'ID',self.tag_id)
            self.db_manager.delete_item_ext_table("public/mill.db",self.tag_params_db_name,'ID',self.tag_id)
        self.open_tag_list()

    def close_popup(self,*args):
            self.destroy()

    def settings_not_applied(self, *args):
            self.save_button.set_sensitive(True)

    def open_connection_settings(self, *args):
            popup = ConnectionSettingsWindow(self.conx_id, db = self.db_manager, app = self.app )
            self.close_popup()
    
    def open_tag_list(self, *args):
        self.app.setup_tags(None,self.conx_id)
        self.close_popup()
    
    def add_style(self, wid, style):
        #style should be a list
        sc = wid.get_style_context()
        for sty in style:
            sc.add_class(sty)

class TagSettingsBox(Gtk.Box):
        def __init__(self, t_id, conx_id, db=None, parent = None, app = None):
                super(TagSettingsBox, self).__init__()
                self.db_manager = db
                self.conx_id = conx_id
                self.tag_id = t_id
                self.parent = parent
                self.app = app
                self.conx_icon = './Public/images/logo.png'
                self.data_type_list = ['BOOL', 'DINT', 'INT', 'LINT', 'LREAL', 'REAL', 'SINT', 'STRING','UDINT','UINT','ULINT','USINT']
                self.Modbus_func_type_list = ['Coil','Input Status','Holding Register','Input Register']
                p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.conx_icon, 80, -1, True)
                self.parent.icon.set_from_pixbuf(p_buf)
                self.conx_active = 0 # False

                #get connection specific tag data
                c_data = self.db_manager.run_query('''SELECT Connection,ConnectionTypeID From Connections WHERE ID = ?;''',(self.conx_id,))
                self.conx_user_name = c_data[0][0]
                self.conx_type_id = c_data[0][1]
                c_type = self.db_manager.run_query('''SELECT ConnectionType From ConnectionTypes WHERE ID =?;''',(self.conx_type_id,))
                self.conx_type_name = (c_type[0][0])
                self.tag_params_db_name = self.conx_type_name+'TagParams'

                #get tag data
                self.t_dict1 = {}
                self.tag_db_name = 'Tags'
                self.tag_db_columns = ['Tag','Description','DataType','ConnectionID']
                db_col_string = ','.join(self.tag_db_columns)
                sql = "SELECT {lst} FROM [{tbl}] WHERE ID =?;".format( lst =db_col_string,tbl = self.tag_db_name)
                t_data = self.db_manager.run_query(sql,[self.tag_id])
                for i in range(len(self.tag_db_columns)):
                    self.t_dict1[self.tag_db_columns[i]] = t_data[0][i]

                if self.conx_type_name == 'ModbusTCP' or self.conx_type_name == 'ModbusRTU':
                    self.t_dict2 = {}
                    self.tag_conx_db_columns = ['Function','Address','Bit','WordSwapped','ByteSwapped']
                    db_col_string = ','.join(self.tag_conx_db_columns)
                    sql = "SELECT {lst} FROM [{tbl}] WHERE ID =?;".format( lst =db_col_string,tbl = self.tag_params_db_name)
                    t_data = self.db_manager.run_query(sql,[self.tag_id])
                    for i in range(len(self.tag_conx_db_columns)):
                        self.t_dict2[self.tag_conx_db_columns[i]] = t_data[0][i]
                else:
                    self.t_dict2 = {}
                    self.tag_conx_db_columns = ['Address']
                    db_col_string = ','.join(self.tag_conx_db_columns)
                    sql = "SELECT {lst} FROM [{tbl}] WHERE ID =?;".format( lst =db_col_string,tbl = self.tag_params_db_name)
                    t_data = self.db_manager.run_query(sql,[self.tag_id])
                    for i in range(len(self.tag_conx_db_columns)):
                        self.t_dict2[self.tag_conx_db_columns[i]] = t_data[0][i]

                # build content area here
                self.box = Gtk.Box(spacing=10,orientation=Gtk.Orientation.VERTICAL)
                self.bx_widgets = {'ConnectionID':self.conx_id}
                
                for t_item in self.tag_db_columns:
                    #Tag
                    if t_item == 'Tag':
                        bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request = 50)
                        l = Gtk.Label('Tag:',width_request = 200)
                        self.parent.add_style(l,["text-white-color","font-20","font-bold"])
                        bx.pack_start(l, 0, 0, 0)
                        self.parameter1 = Gtk.Entry(text = self.t_dict1['Tag'],max_length = 100, xalign = 0.5,width_request = 400)
                        self.parent.add_style(self.parameter1,["entry","font-16","font-bold"])
                        self.parent.add_style(self.parameter1,["text-white-color","font-20","font-bold"])
                        bx.pack_start(self.parameter1, 0, 0, 0)
                        self.box.pack_start(bx, 0, 0, 0)
                        self.parameter1.connect("changed", self.parent.settings_not_applied)
                        self.parameter1.connect("changed", lambda wid:self.update_ref('Tag',self.parameter1.get_text()))
                        self.bx_widgets['Tag'] = (self.parameter1.get_text())
                    #Description
                    if t_item == 'Description':
                        bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request = 50)
                        l = Gtk.Label('Description:',width_request = 200)
                        self.parent.add_style(l,["text-white-color","font-20","font-bold"])
                        bx.pack_start(l, 0, 0, 0)
                        self.parameter2 = Gtk.Entry(text = self.t_dict1['Description'],max_length = 100, xalign = 0.5,width_request = 400)
                        self.parent.add_style(self.parameter2,["entry","font-16","font-bold"])
                        bx.pack_start(self.parameter2, 0, 0, 0)
                        self.box.pack_start(bx, 0, 0, 0)
                        self.parameter2.connect("changed", self.parent.settings_not_applied)
                        self.parameter2.connect("changed", lambda wid:self.update_ref('Description',self.parameter2.get_text()))
                        self.bx_widgets['Description'] = (self.parameter2.get_text())
                    #DataType
                    if t_item == 'DataType':
                        bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request = 50)
                        l = Gtk.Label('DataType:',width_request = 200)
                        self.parent.add_style(l,["text-white-color","font-20","font-bold"])
                        bx.pack_start(l, 1, 1, 0)
                        self.parameter3 = Gtk.ComboBoxText(width_request = 400)
                        self.parent.add_style(self.parameter3,["font-16","font-bold"])
                        temp = 0
                        for func in self.data_type_list:
                            self.parameter3.append_text(func)
                            if str(self.t_dict1['DataType']) == func:
                                self.parameter3.set_active(temp)
                            temp += 1
                        bx.pack_start(self.parameter3, 0, 0, 0)
                        self.box.pack_start(bx, 0, 0, 0)
                        self.parameter3.connect("changed", self.parent.settings_not_applied)
                        self.parameter3.connect("changed", lambda wid:self.update_ref('DataType',self.parameter3.get_active_text()))
                        self.bx_widgets['DataType'] = (self.parameter3.get_active_text())
                for t_item in self.tag_conx_db_columns:
                    #Address
                    if t_item == 'Address':
                        bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request = 50)
                        l = Gtk.Label('Address:',width_request = 200)
                        self.parent.add_style(l,["text-white-color","font-20","font-bold"])
                        bx.pack_start(l, 0, 0, 0)
                        self.parameter4 = Gtk.Entry(text = self.t_dict2['Address'],max_length = 50, xalign = 0.5,width_request = 400)
                        bx.pack_start(self.parameter4, 0, 0, 0)
                        self.box.pack_start(bx, 0, 0, 0)
                        if self.conx_type_name == 'Local':
                            self.parameter4.set_editable(False)
                            self.parent.add_style(self.parameter4,["entry-disabled","font-16","font-bold"])
                        else:
                            self.parent.add_style(self.parameter4,["entry","text-white-color","font-16","font-bold"])
                        self.parameter4.connect("changed", self.parent.settings_not_applied)
                        self.parameter4.connect("changed", lambda wid:self.update_ref('Address',self.parameter4.get_text()))
                        self.bx_widgets['Address'] = (self.parameter4.get_text())
                    #Bit
                    if t_item == 'Bit':
                        bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request = 50)
                        l = Gtk.Label('Bit Number',width_request = 200)
                        self.parent.add_style(l,["text-white-color","font-20","font-bold"])
                        bx.pack_start(l, 1, 1, 0)
                        self.parameter5 = Gtk.SpinButton(adjustment=Gtk.Adjustment(int(self.t_dict2['Bit']), 0, 16, 1, 2, 0), numeric=True,width_request = 400)
                        self.parent.add_style(self.parameter5,["font-16","font-bold"])
                        bx.pack_start(self.parameter5, 0, 0, 0)
                        self.box.pack_start(bx, 0, 0, 0)
                        self.parameter5.connect("changed", self.parent.settings_not_applied)
                        self.parameter5.connect("changed", lambda wid:self.update_ref('Bit',self.parameter5.get_value()))
                        self.bx_widgets['Bit'] = (self.parameter5.get_value())
                    #Function
                    if t_item == 'Function':
                        bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request = 50)
                        l = Gtk.Label('Function',width_request = 200)
                        self.parent.add_style(l,["text-white-color","font-20","font-bold"])
                        bx.pack_start(l, 1, 1, 0)
                        self.parameter6 = Gtk.ComboBoxText(width_request = 400)
                        self.parent.add_style(self.parameter6,["font-16","font-bold"])
                        temp = 0
                        for func in self.Modbus_func_type_list:
                            self.parameter6.append_text(func)
                            if str(self.t_dict2['Function']) == func:
                                self.parameter6.set_active(temp)
                            temp += 1
                        bx.pack_start(self.parameter6, 0, 0, 0)
                        self.box.pack_start(bx, 0, 0, 0)
                        self.parameter6.connect("changed", self.parent.settings_not_applied)
                        self.parameter6.connect("changed", lambda wid:self.update_ref('Function',self.parameter6.get_active_text()))
                        self.bx_widgets['Function'] = (self.parameter6.get_active_text())
                    #Byteswapped
                    if t_item == 'ByteSwapped':
                        bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request = 50)
                        l = Gtk.Label('ByteSwapped:',width_request = 200)
                        self.parent.add_style(l,["text-white-color","font-20","font-bold"])
                        bx.pack_start(l, 1, 1, 0)
                        bh = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,halign = Gtk.Align.CENTER)
                        self.parameter7 = Gtk.CheckButton(width_request = 30,height_request = 30)
                        self.parent.add_style(self.parameter7,["tog-ctrl-enabled"])
                        if self.t_dict2['ByteSwapped'] == 1:
                            self.parameter7.set_active(True)
                        else:
                            self.parameter7.set_active(False)
                        bh.pack_start(self.parameter7,1,1,0)
                        bx.pack_start(bh, 1, 1, 0)
                        self.box.pack_start(bx, 0, 0, 0)
                        self.parameter7.connect("toggled", self.parent.settings_not_applied)
                        self.parameter7.connect("toggled", lambda wid:self.update_ref('ByteSwapped',self.parameter7.get_active()))
                        self.bx_widgets['ByteSwapped'] = (self.parameter7.get_active())
                    #Wordswapped
                    if t_item == 'WordSwapped':
                        bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request = 50)
                        l = Gtk.Label('WordSwapped:',width_request = 200)
                        self.parent.add_style(l,["text-white-color","font-20","font-bold"])
                        bx.pack_start(l, 1, 1, 0)
                        bh = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,halign = Gtk.Align.CENTER)
                        self.parameter8 = Gtk.CheckButton(width_request = 30,height_request = 30)
                        self.parent.add_style(self.parameter8,["tog-ctrl-enabled"])
                        if self.t_dict2['WordSwapped'] == 1:
                            self.parameter8.set_active(True)
                        else:
                            self.parameter8.set_active(False)
                        bh.pack_start(self.parameter8,1,1,0)
                        bx.pack_start(bh, 1, 1, 0)
                        self.box.pack_start(bx, 0, 0, 0)
                        self.parameter8.connect("toggled", self.parent.settings_not_applied)
                        self.parameter8.connect("toggled", lambda wid:self.update_ref('WordSwapped',self.parameter8.get_active()))
                        self.bx_widgets['WordSwapped'] = (self.parameter8.get_active())
                self.pack_start(self.box, 0, 0, 0)
                self.set_enables()

        def set_enables(self,*args):

            if self.conx_type_name == 'ModbusTCP' or self.conx_type_name == 'ModbusRTU':
                #Bit
                if (self.parameter6.get_active_text() == 'Holding Register' or self.parameter6.get_active_text() == 'Input Register') and self.parameter3.get_active_text() == 'BOOL':
                    self.parameter5.set_sensitive(True)
                else:
                    self.parameter5.set_sensitive(False)
                #Byte Swap
                if self.parameter3.get_active_text() != 'BOOL':
                    self.parameter7.set_sensitive(True)
                    sc = self.parameter7.get_style_context()
                    sc.remove_class("tog-ctrl-disabled")
                    self.parent.add_style(self.parameter7,["tog-ctrl-enabled"])
                else:
                    self.parameter7.set_sensitive(False)
                    self.parameter7.set_active(False)
                    sc = self.parameter7.get_style_context()
                    sc.remove_class("tog-ctrl-disabled")    
                    self.parent.add_style(self.parameter7,["tog-ctrl-disabled"])    
                #Word Swap
                temp_list = ['DINT', 'LINT', 'LREAL', 'REAL', 'STRING','UDINT','ULINT']
                if self.parameter3.get_active_text() in temp_list:
                    self.parameter8.set_sensitive(True)
                    sc = self.parameter8.get_style_context()
                    sc.remove_class("tog-ctrl-disabled")
                    self.parent.add_style(self.parameter8,["tog-ctrl-enabled"])
                else:
                    self.parameter8.set_sensitive(False)     
                    self.parameter8.set_active(False)    
                    sc = self.parameter8.get_style_context()
                    sc.remove_class("tog-ctrl-disabled")
                    self.parent.add_style(self.parameter8,["tog-ctrl-disabled"])    


        def update_ref(self,name,val,*args):
            self.bx_widgets[name] = val
            self.set_enables()
            #Function
            if name == 'DataType':
                self.parameter6.remove_all()
                if self.parameter3.get_active_text() != 'BOOL':
                    temp = 0
                    for func in ['Holding Register','Input Register']:
                        self.parameter6.append_text(func)
                        self.parameter6.set_active(0)
                else:
                    temp = 0
                    for func in self.Modbus_func_type_list:
                        self.parameter6.append_text(func)
                        if str(self.t_dict2['Function']) == func:
                            self.parameter6.set_active(temp)
                        temp += 1

        def apply(self,*args):
                col_name_str = ' '
                vals = []
                for i in range(len(self.tag_db_columns)):
                    col_name_str += self.tag_db_columns[i] +' = ?'
                    if len(self.tag_db_columns)>=1 and (i+1) != len(self.tag_db_columns): 
                        col_name_str+=','
                    vals.append(self.bx_widgets[self.tag_db_columns[i]])
                #Update Tags data
                vals.append(self.tag_id)
                sql = "UPDATE {t} SET {col} WHERE ID = (?);".format(t=self.tag_db_name,col=col_name_str)
                self.db_manager.run_query(sql,vals)
                self.db_manager.copy_table(self.tag_db_name)

                #Update Connection Specfic Tag Data
                vals = []
                col_name_str = ''
                for i in range(len(self.tag_conx_db_columns)):
                    col_name_str += self.tag_conx_db_columns[i] +' = ?'
                    if len(self.tag_conx_db_columns)>=1 and (i+1) != len(self.tag_conx_db_columns): 
                        col_name_str+=','
                    vals.append(self.bx_widgets[self.tag_conx_db_columns[i]])
                vals.append(self.tag_id)
                sql = "UPDATE {t} SET {col} WHERE ID = (?);".format(t=self.tag_params_db_name,col=col_name_str)
                self.db_manager.run_query(sql,vals)
                self.db_manager.copy_table(self.tag_params_db_name)
