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

class ListSelectionWidget(Widget):
    def build(self):
        rows = self.db_manager.get_rows("WidgetParams-list-select",
                ["ValueTag","OnChange","InitialTag","ExpressionTag"], "WidgetID", self.id)
        try:
            self.substitute_replacements(self.replacements, rows[0])
            self.value_tag = rows[0]["ValueTag"]            #Used to read tag value in database
            self.express_tag = rows[0]["ExpressionTag"] #Used to excute command to fill list
            self.on_change_cmd = rows[0]["OnChange"]
            self.initialTag = rows[0]["InitialTag"]
        except (IndexError, KeyError):
            event_msg = "ListSelectionWidget {} path lookup error".format(self.id)
            self.app.display_event(event_msg)

        self.initial_val = ''
        self.list_values = []
        self.widget =Gtk.ComboBoxText(width_request=self.width, height_request=self.height, popup_fixed_width=True)
        self.widget.set_entry_text_column(0)
        self.widget.connect("changed", self.on_change)
        self.label = Gtk.Label()
        self.widget.add(self.label)
        self.widget.show_all()
        self.null_state_label = None
        self.set_styles(self.widget)
        self.refresh()
    
    def refresh(self):
        self.initial_val = 'updating'
        self.get_list_val()
        self.set_list(self.list_values)
        self.set_initial_val()
        self.update_text()
        self.initial_val = ''

    def class_update(self, factory, subscriber):
        if self.display != subscriber:
            return
    
    def set_initial_val(self,*args):
        expression_val = self.connection_manager.evaluate_expression(self,self.initialTag, self.display,str)
        for i in range(len(self.list_values)):
            if expression_val == self.list_values[i]:
                self.initial_val = expression_val
                self.widget.set_active(i)
        
    def get_list_val(self,*args):
        del self.list_values[:]
        if self.value_tag != None:
            if self.value_tag.startswith("LIST"):
                "ex:LIST(Port 1,Port 2)"
                val = self.value_tag[self.value_tag.find("(")+1 : self.value_tag.find(")")]
                lst = val.split(",")
                for i in lst:
                    self.list_values.append(i)
            else:
                self.value_tag = self.value_tag.split(',')    #accepts a list of value tags to fill the drop down list
                if type(self.value_tag) is list:
                    for items in self.value_tag:
                        expression_val = self.connection_manager.evaluate_expression(self, self.value_tag, self.display)
                        if type(expression_val) is list:
                            for i in expression_val:
                                self.list_values.append(i)
                        else:
                            self.list_values.append(expression_val)
        elif self.express_tag != None:
            if type(self.express_tag) is list:
                for items in self.express_tag:
                    expression_val = self.connection_manager.evaluate_expression(self, items, self.display)
                    if type(expression_val) is list:
                        for i in expression_val:
                            self.list_values.append(i)
                    else:
                        self.list_values.append(expression_val)
            else:
                expression_val = self.connection_manager.evaluate_expression(self, self.express_tag, self.display)
                if type(expression_val) is list:
                    for i in expression_val:
                        self.list_values.append(i)
                else:
                    self.list_values.append(expression_val)
            if self.list_values != None and 'None' not in self.list_values:
                self.list_values.append('None')
        else:
             self.list_values.append('None')

    def on_change(self,*args):
        self.update_text()
        if not self.initial_val:    # prevents updating db with already saved Value
            self.run_cmd()

    def set_list(self,vals,*args):
        self.widget.remove_all()
        if vals != None:
            for i in vals:
                self.widget.append_text(str(i))
    
    def update_text(self,*args):
        txt = self.widget.get_active_text()
        self.label.set_text(str(txt))

    def return_text_value(self,*args):
        return self.widget.get_active_text()
    
    def run_cmd(self,*args):
        cmd = self.on_change_cmd
        if cmd:
            try:
                exec(cmd)
            except Exception as e:
                print('Error on widget id "{}"\n\tCommand: {}\n\tError: {}'.format(self.id, cmd, e))