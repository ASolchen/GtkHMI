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

class Coord2d(object):
    def __repr__(self) -> str:
        return f"x={self.x}, y={self.y}"
    def __init__(self, x=0, y=0) -> None:
        super().__init__()
        self.x = x
        self.y = y
    def set_by_event(self, event):
        self.x, self.y = (event.x_root, event.y_root)
    def set_xy(self, x, y):
        self.x = x
        self.y = y


class BuildMask(Gtk.EventBox):
    
    @GObject.Property(type=bool, default=False, flags=GObject.ParamFlags.READWRITE)
    def selected(self):
        return self._selected    
    @selected.setter
    def selected(self, value):
        self._selected = value
        if value:
            self.override_background_color(Gtk.StateFlags.NORMAL,
                Gdk.RGBA(1.0, 1.0, 0.0, 0.2))
        else:
            self.override_background_color(Gtk.StateFlags.NORMAL,
                Gdk.RGBA(0.0, 0.0, 0.0, 0.0))
            self.remove_right_click()


    def __init__(self, widget):
        super().__init__(above_child=True)
        self.hmi_widget = widget
        self._selected = False
        self.last_widget_move = Coord2d()
        self.widget_start_location = Coord2d()
        self.right_click_menu = Gtk.Popover()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                
        for x in range(0,10,2):
            vbox.pack_start(Gtk.ModelButton(label=f"Item {1+x}"), False, True, 10)
            vbox.pack_start(Gtk.Label(label=f"Item {2+x}"), False, True, 10)
            vbox.show_all()
        self.right_click_menu.add(vbox)
        self.connect("button-press-event", self.mouse_down)
        self.connect("button-release-event", self.mouse_up)
        self.connect("motion-notify-event", self.mouse_dragged)
        self.builder = None
        self.build_mode_changed()

    def remove_right_click(self):
        self.right_click_menu.set_relative_to(None)

    def mouse_down(self, e_box, event):
        self.last_widget_move.set_by_event(event)
        rect = self.hmi_widget.widget.get_allocation()
        self.widget_start_location.set_xy(rect.x, rect.y)

    def mouse_up(self, e_box, event):
        if not self.builder:
            return
        if event.button == 3:
            self.remove_right_click()
            self.right_click_menu.set_relative_to(self.hmi_widget.layout)
            self.right_click_menu.show_all()
        if self.hmi_widget.widget_class == "display" and not self.hmi_widget.overlay:
            self.builder.none_selected()
            return
        ctrl = bool(event.state & Gdk.ModifierType.CONTROL_MASK) #ctrl button held?
        if event.button in [1,3]: # left or right click
            if ctrl:
                self.builder.append_selected(self.hmi_widget)
            else:
                self.builder.new_selected(self.hmi_widget)
        
    def mouse_dragged(self, build_mask, event):
        delta_x = event.x_root - self.last_widget_move.x
        delta_y = event.y_root - self.last_widget_move.y
        if any((abs(delta_x) > 50, abs(delta_y) > 50)):
            self.last_widget_move.set_by_event(event)
            self.hmi_widget.x += int(delta_x)
            self.hmi_widget.y += int(delta_y)
        return
        
        x = event.x_root
        y = event.y_root
        
        x = int(round(x) /grid[0]) * grid[0]
        y = int(round(y) /grid[1]) * grid[1]
        self.hmi_widget.x = x
        self.hmi_widget.y = y

    def build_mode_changed(self, *args):
        if self.hmi_widget.app.builder_mode and self.hmi_widget.app.builder:
            self.builder = self.hmi_widget.app.builder
        else:
            self.builder = None
