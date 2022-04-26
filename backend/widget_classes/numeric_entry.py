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
import time, numbers

from backend.widget_classes.widget import Widget

class NumericEntryWidget(Widget):

    def build(self):

        display_rows = self.db_manager.get_rows("WidgetParams-num-entry",
                ["PlaceHolder", "MaxChar", "Justify","Label","ValueTag","ValMin","ValMax"],
                "WidgetID", self.id)
        format_rows = self.db_manager.get_rows("WidgetParams-num-format",
                ["Format",	"LeftPadding", "Decimals"], "WidgetID", self.id)
        if not len(format_rows):
            format_rows.append({"Format": "Integer",
                                                    "LeftPadding": 0,
                                                    "Decimals": 0},) #use some defaults
        try:
            self.substitute_replacements(self.replacements, display_rows[0])
            self.place_holder = display_rows[0]["PlaceHolder"] #TODO remove from here and db
            self.max_char = display_rows[0]["MaxChar"]
            self.text_justify = display_rows[0]["Justify"]
            self.disp_label = display_rows[0]["Label"]
            self.value_tag = display_rows[0]["ValueTag"]
            self.val_min = display_rows[0]["ValMin"]
            self.val_max = display_rows[0]["ValMax"]
            self.substitute_replacements(self.replacements, format_rows[0])
            self.num_format = format_rows[0].get("Format", "Integer")
            self.left_padding = format_rows[0].get("LeftPadding", 0)
            self.decimals = format_rows[0].get("Decimals",0)     
        except (IndexError, KeyError):
            event_msg = "NumericEntryWidget {} path lookup error".format(self.id)
            self.app.display_event(event_msg)

        self.widget = Gtk.Entry(height_request=self.height)    #this only sets minimum width
        self.widget.set_width_chars(int(self.max_char))
        self.widget.set_placeholder_text(self.place_holder)
        self.widget.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.widget.connect("button-press-event", self.entry_press_action)
        self.widget.set_can_focus(False)
        if self.place_holder != None:
            self.widget.set_text(self.place_holder)

        try:
            self.min = float(self.val_min)
        except (TypeError, ValueError):
            self.min = None
        try:
            self.max = float(self.val_max)
        except (TypeError, ValueError):
            self.max = None
        self.set_styles(self.widget)

        _justify = {"LEFT": 0.0, "CENTER": 0.5, "RIGHT": 1.0}
        x_align = 0.5
        if self.text_justify in _justify:
            x_align = _justify.get(self.text_justify, 0.5)
        self.widget.set_alignment(x_align)

    def entry_press_action(self,*args):
        if self.builder_mode:
            return
        self.app.open_numpad(self.set_value, self,self.widget ,
        {"Label":self.disp_label,
        "ValMin":self.val_min,
        "ValMax":self.val_max,
        })

    def check_limits(self, val):
        try:
            val = float(val)
        except ValueError:
            event_msg = "Value entered is out of range"
            self.app.display_event(event_msg)
            return False
        if not type(self.min) == type(None) and val < self.min:
            return False        
        if not type(self.max) == type(None) and val > self.max:
            return False
        return True
    
    def set_value(self,val,*args):
        try:
            val = float(val)
        except ValueError:
            return
        if self.check_limits(val):
            self.write(self.value_tag, val)

    def class_update(self, factory, subscriber):
        if self.display != subscriber or self.widget.has_focus():
            return
        expression_val = self.connection_manager.evaluate_expression(self, self.value_tag, self.display)
        self.expression_err |= expression_val is None
        if type(expression_val) == type(None):
            expression_val = "**.**"
            self.expression_err = True
            return
        if self.num_format == "Float":
            text = ""
            dec = "" if type(self.decimals) == type(None) else int(self.decimals)
            pad = "" if type(self.left_padding) == type(None) else int(self.left_padding)
            line = """text = '{:"""+str(pad)+"."+str(dec)+"""f}'.format(expression_val)"""
            locs = locals()
            exec(line, globals(), locs)
            text = locs["text"]
            if pad:
                sign = ""
                if text.startswith("-"):
                    sign = text[0]
                    text = text[1:]
                whole_len = len(text.split(".")[0])
                add_chars = pad - whole_len
                if add_chars > 0:
                    text = text.rjust(len(text)+add_chars, "0")
                text = sign + text
            self.widget.set_text(text)
            return
        if self.num_format == "Hex":
            self.widget.set_text("0x{:X}".format(expression_val))
            return
        if self.num_format == "Integer":
            pad = "" if type(self.left_padding) == type(None) else int(self.left_padding)
            self.widget.set_text("{}".format(int(expression_val)))
            if pad:
                whole_len = len(text)
                add_chars = pad - whole_len
                if add_chars > 0:
                    text = text.rjust(len(text)+add_chars, "0")
            return
        #No formatting, let python decide
        self.widget.set_text("{}".format(expression_val))
