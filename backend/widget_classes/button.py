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
from os import error
import gi, cairo
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
from gi.repository.GLib import GError
import re
import time

from backend.widget_classes.widget import Widget, WidgetSettingsBase, WidgetParamsError
from backend.managers.database_models.widget_database import WidgetParamsControlButton
class ButtonSettingsPanels(WidgetSettingsBase):
    
    def build_base_settings_panel(self):
        super(ButtonSettingsPanels,self).build_base_settings_panel()
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.append_page(panel, Gtk.Label(label="Button Settings"))
        grid = Gtk.Grid(column_spacing=4, row_spacing=4)
        panel.add(grid)
        #row 1
        row = 0     
        grid.attach(Gtk.Label("label", width_request=50), 0,row, 1,1)
        self.label_entry = Gtk.Entry()
        buffer = self.label_entry.get_property("buffer")
        buffer.connect("deleted-text", lambda buf,pos,n_chars: self.set_param("label",    buf.get_property("text")))
        buffer.connect("inserted-text", lambda buf,pos, chars, n_chars:self.set_param("label",    buf.get_property("text")))
        grid.attach(self.label_entry, 1,row, 3,1)

        #row2
        row+=1
        grid.attach(Gtk.Label("image", width_request=50), 0,row, 1,1)
        self.image_entry = Gtk.Entry()
        buffer = self.image_entry.get_property("buffer")
        buffer.connect("deleted-text", lambda buf,pos,n_chars: self.set_param("image",    buf.get_property("text")))
        buffer.connect("inserted-text", lambda buf,pos, chars, n_chars:self.set_param("image",    buf.get_property("text")))
        grid.attach(self.image_entry, 1,row, 3,1)

        #row3
        row+=1
        grid.attach(Gtk.Label("on_press", width_request=50), 0,row, 1,1)
        self.on_press_entry = Gtk.Entry()
        buffer = self.on_press_entry.get_property("buffer")
        buffer.connect("deleted-text", lambda buf,pos,n_chars: self.set_param("on_press",    buf.get_property("text")))
        buffer.connect("inserted-text", lambda buf,pos, chars, n_chars:self.set_param("on_press",    buf.get_property("text")))
        grid.attach(self.on_press_entry, 1,row, 3,1)

        #row4
        row+=1
        grid.attach(Gtk.Label("on_release", width_request=50), 0,row, 1,1)
        self.on_release_entry = Gtk.Entry()
        buffer = self.on_release_entry.get_property("buffer")
        buffer.connect("deleted-text", lambda buf,pos,n_chars: self.set_param("on_release",    buf.get_property("text")))
        buffer.connect("inserted-text", lambda buf,pos, chars, n_chars:self.set_param("on_release",    buf.get_property("text")))
        grid.attach(self.on_release_entry, 1,row, 3,1)

        #row5
        row+=1
        grid.attach(Gtk.Label("confirm_on_press_msg", width_request=50), 0,row, 1,1)
        self.confirm_on_press_msg_entry = Gtk.Entry()
        buffer = self.confirm_on_press_msg_entry.get_property("buffer")
        buffer.connect("deleted-text", lambda buf,pos,n_chars: self.set_param("confirm_on_press_msg",    buf.get_property("text")))
        buffer.connect("inserted-text", lambda buf,pos, chars, n_chars:self.set_param("confirm_on_press_msg",    buf.get_property("text")))
        grid.attach(self.confirm_on_press_msg_entry, 1,row, 3,1)

        #row6
        row+=1
        grid.attach(Gtk.Label("confirm_on_release_msg", width_request=50), 0,row, 1,1)
        self.confirm_on_release_msg_entry = Gtk.Entry()
        buffer = self.confirm_on_release_msg_entry.get_property("buffer")
        buffer.connect("deleted-text", lambda buf,pos,n_chars: self.set_param("confirm_on_release_msg",    buf.get_property("text")))
        buffer.connect("inserted-text", lambda buf,pos, chars, n_chars:self.set_param("confirm_on_release_msg",    buf.get_property("text")))
        grid.attach(self.confirm_on_release_msg_entry, 1,row, 3,1)

        self.show_all()




    def set_to_widget_vals(self):
        super(ButtonSettingsPanels,self).set_to_widget_vals()

        self.label_entry.set_text(self.hmi_widget.label)
        self.image_entry.set_text(self.hmi_widget.image)
        self.on_press_entry.set_text(self.hmi_widget.on_press)
        self.on_release_entry.set_text(self.hmi_widget.on_release)
        self.confirm_on_press_msg_entry.set_text(self.hmi_widget.confirm_on_press_msg)
        self.confirm_on_release_msg_entry.set_text(self.hmi_widget.confirm_on_release_msg)


class ButtonWidget(Widget):


    @classmethod
    def get_settings_panels(cls):
        return ButtonSettingsPanels

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
        for c in self.widget.get_children():
            self.widget.remove(c)
        self._label = value 
        self.widget.set_label(value)
        

    @GObject.Property(type=str, flags=GObject.ParamFlags.READWRITE)
    def image(self):
        return self._image 
    @image.setter
    def image(self, value):
        self._image = value
        for c in self.widget.get_children():
            self.widget.remove(c)
        if len(value):
            format, w, h = GdkPixbuf.Pixbuf.get_file_info(value)
            if format:
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
        self._image = ''
        self._on_press = ''
        self._on_release = ''
        self._confirm_on_press_msg = ''
        self._confirm_on_release_msg = ''
        self._label = ''
        self.btn_active = None
        #must init advanced params before init of the base params
        super(ButtonWidget, self).__init__(factory, params)
        self.widget.connect("pressed",self.btn_press_action)
        self.widget.connect("released",self.btn_release_action)
        self.set_styles(self.widget)
        self.resize()

    def initialize_params(self, *args):
        super(ButtonWidget, self).initialize_params()
        try:
            self.image= '' if self.params['image'] == None else self.params['image']
            self.on_press= '' if self.params['on_press'] == None else self.params['on_press']
            self.on_release = '' if self.params['on_release'] == None else self.params['on_release']
            self.confirm_on_press_msg = '' if self.params['confirm_on_press_msg'] == None else self.params['confirm_on_press_msg']
            self.confirm_on_release_msg = '' if self.params['confirm_on_release_msg'] == None else self.params['confirm_on_release_msg']
            self.label = '' if self.params['label'] == None else self.params['label']
        except KeyError as e:
            raise WidgetParamsError(f"Widget initialization failed to find key:{e} in parameters. Parameters: {self.self.params}")

    def animate_state(self, val):
        #override this in child classes if needed
        if self.app.builder_mode:
            return
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
        if not len(self.on_press):
            return
        if len(self.confirm_on_press_msg):
            #Confirmation Type Button
            self.app.confirm(self.on_press_callback, self.confirm_on_press_msg)
        else:
            self.on_press_callback()
        
    def on_press_callback(self):
        if not len(self.on_press):
            return
        exec(self.on_press)

        
    def btn_release_action(self,*args):
        if not len(self.on_release):
            return
        if len(self.confirm_on_release_msg):
            #Confirmation Type Button
            self.app.confirm(self.on_release_callback,self.confirm_on_release_msg)
        else:
            self.on_release_callback()

    def on_release_callback(self):
        if not len(self.on_release):
            return
        exec(self.on_release)

    def save_to_db(self):
        super(ButtonWidget, self).save_to_db() #save the base settings
        entry = self.db_session.query(ButtonWidget.orm_model).filter(ButtonWidget.orm_model.id == self.id).first()
        if entry == None:
            entry = ButtonWidget.orm_model()
        entry.id = self.id
        entry.label = None if not len(self.label) else self.label
        entry.image = None if not len(self.image) else self.image
        entry.on_press = None if not len(self.on_press) else self.on_press
        entry.on_release = None if not len(self.on_release) else self.on_release
        entry.confirm_on_press_msg = None if not len(self.confirm_on_press_msg) else self.confirm_on_press_msg
        entry.confirm_on_release_msg = None if not len(self.confirm_on_release_msg) else self.confirm_on_release_msg
        self.db_session.add(entry)
        self.db_session.commit()

