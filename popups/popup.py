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
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf, Gio
import re

class PopupConfirm(Gtk.Dialog):
    def __init__(self, parent, msg='Do you really want to do this?'):
        Gtk.Dialog.__init__(self, "Confirm?", parent, Gtk.DialogFlags.MODAL,
                            (Gtk.STOCK_YES, Gtk.ResponseType.YES,
                              Gtk.STOCK_NO, Gtk.ResponseType.NO)
                            )
        self.set_default_size(300, 200)
        self.set_border_width(10)
        sc = self.get_style_context()
        sc.add_class("dialog-border")
        self.set_keep_above(True)
        self.set_decorated(False)
        box = Gtk.Box()
        box.set_spacing(10)
        box.set_orientation(Gtk.Orientation.VERTICAL)
        c = self.get_content_area()
        c.add(box)
        box.pack_start(Gtk.Image(stock=Gtk.STOCK_DIALOG_WARNING), 0, 0, 0)
        confirm_msg = Gtk.Label(msg + '\n\n')
        sc = confirm_msg.get_style_context()
        sc.add_class('borderless-num-display')
        sc.add_class('text-black-color')
        sc.add_class('font-20')
        box.pack_start(confirm_msg, 0, 0, 0)
        sep = Gtk.Label(height_request=3)
        c.pack_start(sep,1,1,1)
        self.show_all()
        #Add style to dialog buttons
        a = self.get_action_area()
        b = a.get_children()
        for but in b:
            sc = but.get_style_context()
            sc.add_class("dialog-buttons")
            sc.add_class("font-16")

class PopupMsg(Gtk.Dialog):
    def __init__(self, parent, msg='Something Went Wrong'):
        Gtk.Dialog.__init__(self, msg,parent, Gtk.DialogFlags.MODAL,
                            (Gtk.STOCK_OK, Gtk.ResponseType.YES)
                            )
        self.set_default_size(300, 200)
        self.set_border_width(10)
        sc = self.get_style_context()
        sc.add_class("dialog-border")
        self.set_keep_above(True)
        self.set_decorated(False)
        box = Gtk.Box()
        box.set_spacing(30)
        box.set_orientation(Gtk.Orientation.VERTICAL)
        c = self.get_content_area()
        c.add(box)
        p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Warning.png', 40, -1, True)
        image = Gtk.Image(pixbuf=p_buf)
        box.pack_start(image, 0, 0, 0)
        message = Gtk.Label(msg + '\n\n')
        sc = message.get_style_context()
        sc.add_class('borderless-num-display')
        sc.add_class('text-black-color')
        sc.add_class('font-14')
        box.pack_start(message, 0, 0, 0)
        self.show_all()
        #Add style to dialog buttons
        a = self.get_action_area()
        b = a.get_children()
        for but in b:
            sc = but.get_style_context()
            sc.add_class("dialog-buttons")
            sc.add_class("font-16")

class SetReset(Gtk.Dialog):
    def __init__(self, app,hmi_wid,obj_wid,params,val):
        Gtk.Dialog.__init__(self, params, app.root, Gtk.DialogFlags.MODAL,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.NO)
                            )
        self.app = app
        self.root = app.root
        self.hmi_widget = hmi_wid
        self.widget_obj = obj_wid
        self.params = params
        self.lbl = "Toggle Setting"
        self.value = val
        self.set_default_size(350, 250)
        self.set_border_width(10)
        sc = self.get_style_context()
        sc.add_class("dialog-border")
        self.set_keep_above(True)
        self.set_decorated(False)
        box = Gtk.Box()
        box.set_spacing(30)
        box.set_orientation(Gtk.Orientation.VERTICAL)
        c = self.get_content_area()
        c.add(box)
        message = Gtk.Label(label = self.params['Description'], height_request = 50)
        sc = message.get_style_context()
        sc.add_class('borderless-num-display')
        sc.add_class('text-black-color')
        sc.add_class('font-14')
        box.pack_start(message, 0, 0, 0)
        box2 = Gtk.Box(height_request = 50)
        box2.set_spacing(30)
        box2.set_orientation(Gtk.Orientation.HORIZONTAL)
        btn_list = ['SET','RESET']
        for item in btn_list:
            btn = Gtk.Button(label = item, width_request=100)
            btn.connect("clicked", self.btn_pressed)
            box2.pack_start(btn, 1, 0, 0)
            sc = btn.get_style_context()
            sc.add_class("dialog-buttons")
            sc.add_class("font-16")
        box.pack_start(box2, 0, 0, 0)
        self.show_all()
                #Add style to dialog buttons
        a = self.get_action_area()
        b = a.get_children()
        for but in b:
            sc = but.get_style_context()
            sc.add_class("dialog-buttons")
            sc.add_class("font-16")

    def btn_pressed(self,btn,*args):
        text = btn.get_label()
        if text == 'SET':
            val = '1'
        elif text == 'RESET':
            val = '0'
        self.hmi_widget.update_value(val,self.params)
        self.destroy()

class SaveFile(Gtk.FileChooserDialog):
    def __init__(self, app,hint,filter_pat):
        Gtk.FileChooserDialog.__init__(self,"Save As",
                                                                            app.root,
                                                                                Gtk.FileChooserAction.SAVE,
                                                                                (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                                                                    Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.app = app
        self.root = app.root
        #self.set_decorated(False)
        #Add styling
        a = self.get_action_area()
        b = a.get_children()
        for but in b:
            sc = but.get_style_context()
            sc.add_class("dialog-buttons")
            sc.add_class("font-16")
        #The code below recursively searches the content area to return all base widgets
        #--------------------#
        sc = self.get_content_area()
        sc = sc.get_children()
        wid_list = sc
        base_list = []
        keep_going = True
        while keep_going:
            for wid in wid_list:
                wid_list.remove(wid)
                try:
                    new = wid.get_children()
                    for items in new:
                        wid_list.append(items)
                except:
                    base_list.append(wid)
            if not wid_list:
                keep_going = False
        for items in base_list:
            if isinstance(items, Gtk.Entry):
                sty = items.get_style_context()
                sty.add_class("font-20")
                items.connect("button-press-event",self.entry_press_action)
        #--------------------#
        if hint:
            self.set_current_name(hint)
        #add filters
        if filter_pat:
            for pat in filter_pat:
                filter1 = Gtk.FileFilter()
                filter1.add_pattern(pat)
                filter1.set_name(pat)
                self.add_filter(filter1)
    def entry_press_action(self,wid,*args):
        self.app.open_keypad(self.update_value, self,wid ,wid,"")

    def update_value(self,val,widget,*args):
        widget.set_text(str(val))

class OpenFile(Gtk.FileChooserDialog):
    def __init__(self, app,message,filter_pat):
        Gtk.FileChooserDialog.__init__(self,message,
                                                                            app.root,
                                                                                Gtk.FileChooserAction.OPEN,
                                                                                (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                                                                    Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.app = app
        self.root = app.root
        #self.set_decorated(False)
        #Add styling
        a = self.get_action_area()
        b = a.get_children()
        for but in b:
            sc = but.get_style_context()
            sc.add_class("dialog-buttons")
            sc.add_class("font-16")
        #add filters
        if filter_pat:
            for pat in filter_pat:
                filter1 = Gtk.FileFilter()
                filter1.add_pattern(pat)
                filter1.set_name(pat)
                self.add_filter(filter1)

class ValueEnter(Gtk.Dialog):
    #Need to add check for value exceeding min,max range based on type
    def __init__(self, app, hmi_wid,obj_wid,params):
        Gtk.Dialog.__init__(self, params, app.root, Gtk.DialogFlags.MODAL,
                                                (Gtk.STOCK_CANCEL, Gtk.ResponseType.NO)
                                                )
        self.app = app
        self.root = app.root
        self.hmi_widget = hmi_wid
        self.widget_obj = obj_wid
        self.first_key_pressed = False #the user hasn't typed anything yet
        self.params = params
        self.lbl = self.params["Label"]
        self.min = self.params["ValMin"]
        self.max = self.params["ValMax"]
        self.set_default_size(600, 400)
        self.set_border_width(10)
        sc = self.get_style_context()
        sc.add_class("dialog-border")
        self.set_keep_above(True)
        self.set_decorated(False)

        grid = Gtk.Grid(column_spacing=4, row_spacing=4, column_homogeneous=True, row_homogeneous=True)
        pop_lbl = Gtk.Label("{}".format(self.lbl))
        self.add_style(pop_lbl,['borderless-num-display','font-14','text-black-color'])
        grid.attach(pop_lbl,0,0,2,1)
        try:
            value = float(self.widget_obj.get_text())
        except ValueError:
            value = 0
        self.val_label = Gtk.Label(str(value))
        self.add_style(self.val_label,['numpad-display','font-16'])
        grid.attach(self.val_label,2,0,1,1)
        min_str = "-"+chr(0x221e) if type(self.min) == type(None) else self.min
        max_str = chr(0x221e) if type(self.max) == type(None) else self.max
        min_max_lbl = Gtk.Label(u"({} ~ {})".format(min_str, max_str))
        self.add_style(min_max_lbl,['font-14'])
        grid.attach(min_max_lbl,3,0,1,1)
        key = []
        for k in range(10):
            b = Gtk.Button(str(k), can_focus=False, can_default=False)
            #b.get_style_context().add_class("keypad_key")
            b.connect("clicked", self.btn_pressed)
            key.append(b)
            self.add_style(b,['numpad-bg','keypad_key'])
        grid.attach(key[7],0,2,1,1)
        grid.attach(key[8],1,2,1,1)
        grid.attach(key[9],2,2,1,1)
    
        grid.attach(key[4],0,3,1,1)
        grid.attach(key[5],1,3,1,1)
        grid.attach(key[6],2,3,1,1)

        grid.attach(key[1],0,4,1,1)
        grid.attach(key[2],1,4,1,1)
        grid.attach(key[3],2,4,1,1)

        grid.attach(key[0],0,5,2,1)

        period_key = Gtk.Button(".", can_focus=False, can_default=False)
        period_key.connect("clicked", self.add_period)
        self.add_style(period_key,['numpad-bg','keypad_key'])
        grid.attach(period_key,2,5,1,1)

        PM_key = Gtk.Button("+/-")
        PM_key.connect("clicked", self.add_plus_minus)
        self.add_style(PM_key,['numpad-bg','keypad_key'])
        grid.attach(PM_key,3,5,1,1)
        
        clear_key = Gtk.Button("CLEAR", can_focus=False, can_default=False)
        clear_key.connect("clicked", self.init_val)
        self.add_style(clear_key,['numpad-cmd-bg','keypad_enter'])
        grid.attach(clear_key,3,2,1,1)

        delete_key = Gtk.Button("DEL", can_focus=False, can_default=False)
        delete_key.connect("clicked", self.del_num)
        self.add_style(delete_key,['numpad-cmd-bg','keypad_enter'])
        grid.attach(delete_key,3,3,1,1)

        enter_key = Gtk.Button("ENTER", can_focus=False, can_default=False)
        enter_key.connect("clicked", self.accept_val)
        self.add_style(enter_key,['numpad-cmd-bg','keypad_enter'])
        grid.attach(enter_key,3,4,1,1)

        c = self.get_content_area()
        c.pack_start(grid,1,1,1)
        sep = Gtk.Label(height_request=3)
        c.pack_start(sep,1,1,1)
        self.signals = []
        self.signals.append(self.connect('key-release-event', self.key_pressed))
        self.show_all()

        #Add style to dialog buttons
        a = self.get_action_area()
        b = a.get_children()
        for but in b:
            self.add_style(but,['dialog-buttons','font-16'])

    def key_pressed(self, popup, key_event):
        if key_event.get_keycode().keycode == 13:#Enter
            self.accept_val(None)
        if key_event.get_keycode().keycode == 8:#Backspace
            self.first_key_pressed = True #they want to use the number in there
            self.del_num(None)
        elif key_event.string == "-" or key_event.string == "+":
            self.add_plus_minus(None)
        elif key_event.string in "0123456789" and len(key_event.string)==1:
            self.update_val(key_event.string)
        elif key_event.string == ".":
            self.add_period(None)
        else:
            pass

    def add_style(self, item,style):
        sc = item.get_style_context()
        for sty in style:
            sc.add_class(sty)


    def btn_pressed(self, key):
        num = int(key.get_label())
        self.update_val(num)

    def update_val(self, num):
        if not self.first_key_pressed:
            val = str(num)
            self.first_key_pressed = True
        else:
            old_val = self.val_label.get_text()
            if old_val == '0':
                val = str(num)
            else:
                val = old_val+str(num)
        
        
        if self.check_limits(val):
            self.val_label.set_text(val)
    
    def check_limits(self, val):
        try:
            val = float(val)
        except ValueError:
            return False
        if not type(self.min) == type(None) and val < self.min:
            return False        
        if not type(self.max) == type(None) and val > self.max:
            return False
        return True
    
    def init_val(self, key):
        self.val_label.set_text('')
    
    def del_num(self,*args):
        val = self.val_label.get_text()
        val = (val)[:-1]
        if not val:
            val = '0'
        self.val_label.set_text(val)

    def add_period(self,*args):
        if not self.first_key_pressed:
            self.update_val("0")
        val = self.val_label.get_text()
        if "." not in val:
            val = val+"."
            self.val_label.set_text(val)

    def add_plus_minus(self,*args):
        val = self.val_label.get_text()
        if "-" not in val:
            val = "-"+val
        else:
            val = val.replace('-',"")
        if self.check_limits(val):
            self.val_label.set_text(val)

    def cleanup(self):
        for signal in self.signals:
            self.disconnect(signal)

    def accept_val(self, key):
        self.cleanup()
        #set tag?
        #self.widget_obj.set_text(self.val_label.get_text())
        self.hmi_widget.set_value(self.val_label.get_text())
        self.destroy()

class Keyboard(Gtk.Dialog):
    #Need to add check for value exceeding min,max range based on type
    def __init__(self, app, hmi_wid,obj_wid,params,val):
        Gtk.Dialog.__init__(self, params, app.root, Gtk.DialogFlags.MODAL,
                                                (Gtk.STOCK_CANCEL, Gtk.ResponseType.NO)
                                                )
        self.app = app
        self.root = app.root
        self.hmi_widget = hmi_wid
        self.widget_obj = obj_wid
        self.params = params
        self.lbl = "Keyboard"
        self.value = val
        self.set_default_size(800, 400)
        self.set_border_width(10)
        sc = self.get_style_context()
        sc.add_class("dialog-border")
        self.set_keep_above(True)
        self.set_decorated(False)
        #Adding custom button to dialog box
        ok_button = Gtk.Button('OK')
        ok_button.connect("clicked",self.enter_value)
        box = self.get_action_area()
        box.add(ok_button)

        grid = Gtk.Grid(column_spacing=1, row_spacing=1, column_homogeneous=False, row_homogeneous=True)
        pop_lbl = Gtk.Label("{}".format(self.lbl))
        self.add_style(pop_lbl,['borderless-num-display','font-14','text-black-color'])
        grid.attach(pop_lbl,0,0,2,1)
        
        #value = self.widget_obj.get_text()
        self.val_label = Gtk.Label(str(self.value))
        self.add_style(self.val_label,['numpad-display','font-16'])
        grid.attach(self.val_label,2,0,10,1)

        rows = ["1234567890+$", "QWERTYUIOP-=", "ASDFGHJKL:/'","ZXCVBNM<>._",]
        #Row 2
        for row_i, row in enumerate(rows):
            for i, l in enumerate(row):
                b = Gtk.Button(label=l, width_request=80, can_focus=False, can_default=False)
                b.connect("clicked", self.btn_pressed)
                self.add_style(b,['numpad-bg','keypad_key'])
                grid.attach(b,i,row_i+2,1,1)

        clear_key = Gtk.Button("CLEAR", can_focus=False, can_default=False)
        clear_key.connect("clicked", self.init_val)
        self.add_style(clear_key,['numpad-cmd-bg','keypad_enter'])
        grid.attach(clear_key,12,0,1,1)

        delete_key = Gtk.Button("DEL", can_focus=False, can_default=False)
        delete_key.connect("clicked", self.del_num)
        self.add_style(delete_key,['numpad-cmd-bg','keypad_enter'])
        grid.attach(delete_key,12,2,1,1)

        enter_key = Gtk.Button("ENTER", can_focus=False, can_default=False)
        enter_key.connect("clicked", self.accept_val)
        self.add_style(enter_key,['numpad-cmd-bg','keypad_enter'])
        grid.attach(enter_key,12,4,1,1)

        space_key = Gtk.Button("SPACE")
        space_key.connect("clicked", self.add_space)
        self.add_style(space_key,['numpad-cmd-bg','keypad_enter'])
        grid.attach(space_key,1,6,10,1)

        c = self.get_content_area()
        c.pack_start(grid,1,1,1)
        sep = Gtk.Label(height_request=3)
        c.pack_start(sep,1,1,1)
        self.signals = []
        self.signals.append(self.connect('key-release-event', self.key_pressed))
        self.show_all()

        #Add style to dialog buttons
        a = self.get_action_area()
        b = a.get_children()
        for but in b:
            self.add_style(but,['dialog-buttons','font-14'])

    def key_pressed(self, popup, key_event):
        code = key_event.get_keycode().keycode
        if code in[13, 36]:#\n or \r
            self.accept_val(None)
        elif code in [8,22]:#Backspace
            self.del_num(None)
        elif code == 32:#Space
            self.add_space(None)
        else:
            self.update_val(key_event.string)
    
    def enter_value(self, wid, *args):
        self.accept_val(13)

    def add_style(self, item,style):
        sc = item.get_style_context()
        for sty in style:
            sc.add_class(sty)

    def btn_pressed(self, key):
        val = key.get_label()
        self.update_val(val)

    def update_val(self, val):
        old_val = self.val_label.get_text()
        val = old_val+str(val)
        self.val_label.set_text(val)
    
    def init_val(self, key):
        
        self.val_label.set_text('')
    
    def del_num(self,*args):
        val = self.val_label.get_text()
        val = (val)[:-1]
        if not val:
            val = ''
        self.val_label.set_text(val)

    def add_space(self,*args):
        val = self.val_label.get_text()
        val = val+" "
        self.val_label.set_text(val)

    def cleanup(self):
        for signal in self.signals:
            self.disconnect(signal)

    def accept_val(self, key):
        self.cleanup()
        val = self.val_label.get_text()
        #set tag?
        #self.widget_obj.set_text(self.val_label.get_text())
        if self.hmi_widget:
            #no callback
            self.hmi_widget.update_value(val,self.params)
        self.destroy()
    