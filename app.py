# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Jason Engman <jengman@testtech-solutions.com>
# Copyright (c) 2021 Adam Solchenberger <asolchenberger@testtech-solutions.com>
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

import gi, os, sys, glob, serial.tools.list_ports
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
import json
from popups.popup import PopupConfirm, PopupMsg, ValueEnter, Keyboard, SaveFile, OpenFile, SetReset
from backend.widget_classes.factory import WidgetFactory
from backend.managers.database import DatabaseManager
from backend.managers.datalog import AlarmEventViewHandler
from backend.managers.connection_classes.manager import ConnectionManager 

class App(GObject.Object):  
  """    
  Base class of the app to hold all refs and logic
  main passes in the Gtk Builder object so all named widgets can be referenced
  """
  def __init__(self, root):
    super(App, self).__init__()
    self.builder = Gtk.Builder()
    self.root = root
    self.auto_refresh = False
    root.connect("delete-event", lambda *args: self.confirm(self.shutdown,"Do you really want to exit?"))
    with open("Public/app_settings.json", "r") as fp:
      self.app_settings = json.load(fp)    
    #settings.set_property("set_decorate",False)
    self.db_manager = DatabaseManager(self)
    self.connection_manager = ConnectionManager(self)
    self.widget_factory = WidgetFactory(self)
    self.alarm_manager = AlarmEventViewHandler(self)
    self.build()
      

  @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST, return_type=bool,
                    arg_types=(object,),
                    accumulator=GObject.signal_accumulator_true_handled)
  def db_ready(self, db_manager):
    pass #Lets other objects knkow the db_manager is ready
    
  def build(self):
    for c in self.root.get_children():
      c.destroy()
    #try:
    #self.builder.add_from_file("Public/glade/main_ui.glade")
    #self.builder.add_from_file("Public/glade/header.glade")
    #self.builder.add_from_file("Public/glade/navbar.glade")
    self.layout= Gtk.Fixed()
    self.root.add(self.layout)
    #self.builder.get_object("header_box").add(self.builder.get_object("header"))
    #self.builder.get_object("main_box").add(self.builder.get_object("panel_01"))
    #self.builder.get_object("nav_box").add(self.builder.get_object("navbar"))
    #self.navbar = NavBar(self)
    #self.update_header()  # adding functions and images to permenant part of page
    self.start_app()
  
  def add_style(self, path):
    #try:
    cssProvider = Gtk.CssProvider()
    screen = Gdk.Screen.get_default()
    styleContext = Gtk.StyleContext()    
    styleContext.remove_provider_for_screen(screen, cssProvider)
    cssProvider.load_from_path(path)
    styleContext.add_provider_for_screen(screen, cssProvider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_USER)
    #except error as e:
    #  print(e)
    #return False #True to hot load
  
  def confirm(self, runnable, msg="Are you sure?", args=[]):
    popup = PopupConfirm(self.root, msg=msg)
    response = popup.run()
    popup.destroy()
    if response == Gtk.ResponseType.YES:
      if not runnable==None:
        runnable(*args)
      return True
    else:
      return False

  def update_header(self):
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale("Public/images/logo.png", 50, 35, False)
    image = Gtk.Image()
    image.set_from_pixbuf(pixbuf)
    self.builder.get_object("logo_box").add(image)
    #assign function to exit button on header bar
    self.builder.get_object("exit_button").connect("clicked",self.app_exit)
    self.builder.get_object("refresh_switch").connect("notify::state",self.toggle_auto_refresh)

  def start_app(self, *args):
    self.db_manager.open('./Public/test_project.db')
    session = self.db_manager.project_db.session
    app_config_table = self.db_manager.project_db.app_config.models["application-settings"]
    settings = session.query(app_config_table).order_by(app_config_table.id).first()
    if not settings:
      raise KeyError("Application settings not in project database")
    self.app_settings['style-sheet'] = settings.style_sheet
    self.app_settings['width'] = settings.width
    self.app_settings['height'] = settings.height
    self.app_settings['dark-theme'] = settings.dark_theme
    self.app_settings['startup-display'] = settings.startup_display
    self.layout.set_property('width_request', self.app_settings["width"])
    self.layout.set_property('height_request', self.app_settings["height"])
    settings = Gtk.Settings.get_default()
    settings.set_property("gtk-application-prefer-dark-theme", self.app_settings["dark-theme"])
    self.widget_factory.open_display(self.app_settings["startup-display"])
    self.add_style(self.app_settings['style-sheet'])
    return self.auto_refresh

  def shutdown(self,*args):
    self.db_manager.clear_tag_subs(next(iter(self.widget_factory.displays)))
    Gtk.main_quit()
  
  def app_exit(self,*args):
    self.confirm(self.shutdown,"Do you really want to exit?")

  def open_file(self, callback, args=None, msg="Open a file",filter_pattern = []):
    openIT = OpenFile(app=self,message = msg,filter_pat = filter_pattern)
    response = openIT.run()
    if response == Gtk.ResponseType.OK:
        fn = openIT.get_filename()
        callback(fn, args)  # runs this callback with the filename and args passed
    openIT.destroy()

  def save_file(self, callback, args=None, file_hint = None, filter_pattern = []):
    saveIT = SaveFile(app=self,hint = file_hint,filter_pat = filter_pattern)
    response = saveIT.run()
    if response == Gtk.ResponseType.OK:
      fp = saveIT.get_filename()
      fn = os.path.basename(fp)
      directory = saveIT.get_current_folder()
      callback(fp,args)
    saveIT.destroy()

  def open_numpad(self,callback,hmi_widget,widget_obj,params,*args):
    numpad = ValueEnter(app=self, hmi_wid=hmi_widget,obj_wid=widget_obj, params=params)
    response = numpad.run()
    if response == Gtk.ResponseType.NO:
      pass
    else:
      pass
      #callback(args)
    numpad.destroy()

  def open_keypad(self,callback,hmi_widget,widget_obj,params,val,*args):
    keypad = Keyboard(app=self, hmi_wid=hmi_widget,obj_wid=widget_obj, params=params,val=val)
    response = keypad.run()
    if response == Gtk.ResponseType.NO:
      pass
    else:
      pass
      #callback(args)
    keypad.destroy()
  
  def set_reset(self, callback,hmi_widget,widget_obj,params,val,*args):
    sr = SetReset(app=self, hmi_wid=hmi_widget,obj_wid=widget_obj, params=params,val=val)
    response = sr.run()
    if response == Gtk.ResponseType.NO:
      pass
    else:
      pass
    sr.destroy()
  
  def get_serial_ports(self,*args):
    ports = []
    if sys.platform.startswith('win'):
      for i in serial.tools.list_ports.comports():
        ports.append(str(i).split(" ")[0])
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    return ports
  
  def display_event(self,msg):
    #self.db_manager.add_item_to_table('EventLog','(Message)',[msg])
    self.db_manager.emit('save_event',msg)
    #rows = self.db_manager.get_rows("ApplicationSettings", ["StyleSheet", "Width", "Height", "DarkTheme", "StartupDisplay"])
