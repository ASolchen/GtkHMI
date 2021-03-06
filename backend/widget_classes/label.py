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
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
import re
import time

from backend.widget_classes.widget import Widget

class LabelWidget(Widget):
    def build(self):
        rows = self.db_manager.get_rows("WidgetParams-label",
                ["LabelText", "Justify"], "WidgetID", self.id)
        try:
            self.substitute_replacements(self.replacements, rows[0])
            self.label_text = rows[0]["LabelText"] 
            self.text_justify = rows[0].get("Justify", "CENTER") 
        except (IndexError, KeyError):
            event_msg = "LabelWidget {} path lookup error".format(self.id)
            self.app.display_event(event_msg)
        
        self.widget = Gtk.Label(width_request=self.width, height_request=self.height)
        _justify = {"LEFT": 0.0, "CENTER": 0.5, "RIGHT": 1.0}
        x_align = 0.5
        if self.text_justify in _justify:
            x_align = _justify.get(self.text_justify, 0.5)
        self.widget.set_property("xalign", x_align)

        self.widget.set_text(self.label_text)
        self.set_styles(self.widget)

    def animate_state(self, val):
        super(LabelWidget, self).animate_state(val)
        
        if self.builder_mode:
            return
        #override this in child classes if needed
        for state in self.states:
            if state["Caption"]:
                if type(val) != type(None): 
                    val = int(val)
                if val == state["State"]:
                    self.widget.set_text(state["Caption"])
