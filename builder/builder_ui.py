import gi, os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf, Gio
import json
from popups.popup import PopupConfirm, PopupMsg, ValueEnter, Keyboard, SaveFile, OpenFile
from backend.widget_classes.factory import WidgetFactory, WIDGET_TYPES

from backend.widget_classes.widget import Widget, WidgetSettingsBase
from backend.widget_classes.numeric_display import NumericDisplayWidget
from backend.widget_classes.string_display import StringDisplayWidget
from backend.widget_classes.display import DisplayWidget, PopupDisplayWidget
from backend.widget_classes.numeric_entry import NumericEntryWidget
from backend.widget_classes.string_entry import StringEntryWidget
from backend.widget_classes.image import ImageWidget
from backend.widget_classes.button import ButtonWidget
from backend.widget_classes.label import LabelWidget
from backend.widget_classes.state_indicator import StateIndicationWidget
from backend.widget_classes.textview import TextViewWidget
from backend.widget_classes.state_control import StateControlWidget
from backend.widget_classes.alarm_viewer import AlarmViewWidget
from backend.widget_classes.Event_viewer import EventViewWidget
from backend.widget_classes.settings import SettingsWidget
from backend.widget_classes.list_select import ListSelectionWidget
from backend.widget_classes.checkbox import CheckBoxWidget

from backend.managers.database import DatabaseManager
from backend.managers.datalog import AlarmEventViewHandler
from backend.managers.connection_classes.manager import ConnectionManager 
from builder.menu import Menu
from builder.widget_explorer import WidgetExplorer
from builder.widget_panels.display_edit_panel import DisplayEditPanel
from builder.widget_panels.widget_panel import BuilderToolsWidget, AdvancedBuilderToolsWidget
from builder.widget_panels.popup import WidgetSettingsPopup, ConnectionListWindow, TagsListWindow,CreateWidgetWindow

class BuilderLayout(Gtk.Box):
  def __init__(self, app):
    super(BuilderLayout, self).__init__()
    self.app = app
    self.hmi_layout = app.hmi_layout
    self.build_interface()
    #self.open_database("backend/     mill.db")
    self.db_file_path = ""
    #self.active_widget = None #Keeps track of ID of widget which has been clicked on the build panel
    self.widget_highlighted = None  #Keeps track of which widget is currently highlighted on the build panel
    self.base_panel_open = None
    self.global_reference = None
    self.global_coordinates = {'x':0,'y':0,'width':0,'height':0,'abs_x':0,'abs_y':0}
    self.widget_clicked = None
    self.active_display = None  #Keeps track of which display is being edited
    self.click_panel = None
    self.selected_widgets = {}
    self.clipboard = {"widgets": {}}

  def on_key_press_event(self, window, event):
      if event.keyval == 99: #ctrl-c
        self.clipboard["widgets"] = self.selected_widgets.copy()
        print(self.clipboard)
      if event.keyval == 118 and len(self.clipboard): #ctrl-v:
        for w in self.clipboard["widgets"]:
          params = self.clipboard["widgets"][w].params.copy()
          params['id'] = 9999999999
          params['x'] += 10
          params['y'] += 10
          self.app.widget_factory.create_widget(params)


  def append_selected(self, widget):
    self.selected_widgets[widget.id] = widget
    widget.builder_mask.select()
    self.update_settings_panel(None)
  
  def new_selected(self, widget):
    for w in self.selected_widgets:
      self.selected_widgets[w].builder_mask.deselect()
    self.selected_widgets= {widget.id: widget} #single one
    widget.builder_mask.select()
    self.update_settings_panel(widget)

  def none_selected(self):
    for w in self.selected_widgets:
      self.selected_widgets[w].builder_mask.deselect()
    self.selected_widgets= {}
    self.update_settings_panel(None)



  def build_interface(self):
    #try:
    left_top_frame = Gtk.Frame(width_request=400)
    left_top_frame.set_label("Navigator")
    self.navigator_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    left_top_frame.add(self.navigator_panel)
    self.nav_button_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,height_request=40)
    self.navigator_panel.add(self.nav_button_bar)

    left_bottom_frame = Gtk.Frame(width_request=400)
    left_bottom_frame.set_label("Widget Settings")
    self.settings_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    scroll = Gtk.ScrolledWindow()
    scroll.add(self.settings_panel)
    left_bottom_frame.add(scroll)

    self.conn_button = Gtk.Button(width_request = 40, label="Connections")
    self.conn_button.connect('clicked',self.setup_connection)
    self.conn_button.set_sensitive(False)
    self.nav_button_bar.add(self.conn_button)

    self.tag_button = Gtk.Button(width_request = 40, label="Tags")
    self.tag_button.connect('clicked',self.setup_tags,None)
    self.tag_button.set_sensitive(False)
    self.nav_button_bar.add(self.tag_button)

    right_frame = Gtk.Frame()
    right_frame.set_label("Build")
    v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    self.build_panel = DisplayEditPanel(self)
    v_box.pack_start(self.build_panel,1,1,2)
    right_frame.add(v_box)  
    
    self.size = (640, 480)
    self.layout = Gtk.Box(width_request=self.size[0], height_request=self.size[1],
    orientation=Gtk.Orientation.VERTICAL, spacing=20)
    menu_box=Gtk.Box(width_request=self.size[0], height_request=8)
    self.menu = Menu(self)
    menu_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    menu_box.pack_start(self.menu, 0, 0, 0)
    self.layout.add(menu_box)
    self.add(self.layout)
    left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,height_request=(self.size[1]),homogeneous = True)
    bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    self.layout.pack_start(bottom_box,1,1,8)
    bottom_box.set_spacing(20)
    left_box.pack_start(left_top_frame,0,1,5)
    left_box.pack_start(left_bottom_frame,0,1,5)
    bottom_box.pack_start(left_box,0,1,10)
    bottom_box.pack_start(right_frame,1,1,10)
    self.navigator_panel.pack_start(WidgetExplorer(self),1,1,2)

  
  def update_settings_panel(self, widget,*args):
    #Building settings panel
    for c in self.settings_panel.get_children():
      self.settings_panel.remove(c)
    if len(self.selected_widgets) == 0:
      self.settings_panel.add(Gtk.Label(label="No Widgets Selected"))
      self.settings_panel.show_all()
      return
    if widget:
      nb = Gtk.Notebook()
      self.settings_panel.add(widget.get_settings_panels()(widget))
      self.settings_panel.show_all()
      return
    self.settings_panel.add(Gtk.Label(label="Multiple Widgets Selected"))
    self.settings_panel.show_all()

      
  
  def open_widget_popup(self, button):
    popup = WidgetSettingsPopup(self, self, self.db_manager, button.get_property("name"))
    response = popup.run()
    popup.destroy()
  
  def setup_connection(self,*args):
    if self.db_open:
      popup = ConnectionListWindow(self, self, self.db_manager)
    else:
      #If database not open then force user to open DB first
      self.open_database_req()
  
  def setup_tags(self,button,conx_id,*args):
    if self.db_open:
      popup = TagsListWindow(conx_id,self, self.db_manager)
    else:
      #If database not open then force user to open DB first
      self.open_database_req()

  def add_widget(self,button,*args):
    if self.db_open:
      wid_id = button.get_property("name")
      popup = CreateWidgetWindow(self, self, self.db_manager,'New',wid_id)
    else:
      #If database not open then force user to open DB first
      self.open_database_req()

  def add_display(self,button,*args):
    if self.db_open:
      popup = CreateWidgetWindow(self, self, self.db_manager,'display',None)
    else:
      #If database not open then force user to open DB first
      self.open_database_req()

  def confirm(self, runnable, msg="Are you sure?", args=[]):
    popup = PopupConfirm(self.app.root, msg=msg)
    response = popup.run()
    popup.destroy()
    if response == Gtk.ResponseType.YES:
      if not runnable==None:
        runnable(*args)
      return True
    else:
      return False
  
  def display_msg(self, runnable, msg="Something has gone wrong", args=[]):
    popup = PopupMsg(self, msg=msg)
    response = popup.run()
    popup.destroy()
    if response == Gtk.ResponseType.YES:
      if not runnable==None:
        runnable(*args)
      return True
    else:
      return False
    
  def menu_callback_confirm(self, menu_item, cb, msg, *args):
    self.confirm(cb, msg, *args)

  def open_file(self, callback, args=[], msg="Open a file",filter_pattern = []):
    openIT = OpenFile(app=self.app,message = msg,filter_pat = filter_pattern)
    response = openIT.run()
    if response == Gtk.ResponseType.OK:
        fn = openIT.get_filename()
        callback(fn, *args)  # runs this callback with the filename and args passed if any
    openIT.destroy()
  
  def save_file(self, callback, args=[], file_hint = None, filter_pattern = []):
    saveIT = SaveFile(app=self.app,hint = file_hint,filter_pat = filter_pattern)
    response = saveIT.run()
    if response == Gtk.ResponseType.OK:
      fp = saveIT.get_filename()
      fn = os.path.basename(fp)
      directory = saveIT.get_current_folder()
      callback(fp, *args)
    saveIT.destroy()

  def shutdown(self,*args):
    Gtk.main_quit()
  
  def app_exit(self,*args):
    popup = PopupConfirm(self.app.root, msg='Are you sure you want to exit')
    response = popup.run()
    popup.destroy()
    if response == Gtk.ResponseType.NO:
      return True
    else:
      Gtk.main_quit()
      return False
  '''
  def open_widget(self, w_id):
    #clear the panel
    for c in self.build_panel.get_children():
      self.build_panel.remove(c)
    rows = self.db_manager.get_rows("Widgets", Widget.base_parmas, "ID", w_id)
    self.notebook = Gtk.Notebook() 
    self.build_panel.pack_start(self.notebook,1,1,10)  
    self.page1 = Gtk.Box() 
    self.page1.set_border_width(50)
    if len(rows):
      row = rows[0]
      self.base_widget_panel = BuilderToolsWidget(self, row)
      self.page1.add(self.base_widget_panel)

      self.notebook.append_page(self.page1, Gtk.Label("Basic")) 
      self.page2 = Gtk.Box() 
      self.page2.set_border_width(50) 
      self.page2.add(Gtk.Label("Need to put class stuff here")) 
      self.notebook.append_page(self.page2, Gtk.Label("Advanced"))
    self.build_panel.show_all()
  '''

  def open_database_req(self, *args):
    def set_db(path):
      self.app.db = path # setting a new path on this app property will trigger it to open session
    self.open_file(set_db, filter_pattern=["*.db"])
  
  def create_database_req(self, *args):
    def set_db(path):
      self.app.db = path# setting a new path on this app property will trigger it to create and open session
    self.save_file(set_db, filter_pattern=["*.db"])

  def save_db(self, button):
    self.db_manager.write_sqlite_db(self.db_file_path)

  def save_db_as(self, button):
    self.save_file(self.db_manager.write_sqlite_db, filter_pattern=["*.db"])
      
  def get_widgets_display(self, w_id):
    display = w_id #move up the tree to find the top level widget
    rows = [{'ParentID': w_id},]
    while rows[0]["ParentID"] and not rows[0]["ParentID"] == "GLOBAL":
      w_id = rows[0]["ParentID"]
      rows = self.db_manager.get_rows("Widgets", ["ParentID"], match_col="ID", match=w_id)
    return w_id

  def get_widgets_rectangle(self, w_id):
    x,y = self.get_widgets_coords_rel_to_display(w_id)
    rows = self.db_manager.get_rows("Widgets", ["Width", "Height"], match_col="ID", match=w_id)
    w,h = (rows[0]["Width"], rows[0]["Height"])
    coord_list = [x,y,w,h]
    for i, val in enumerate(coord_list):
      if val == None: coord_list[i] = 0
    return coord_list

  def get_widgets_coords_rel_to_display(self, w_id):
    x,y = (0,0)
    display = w_id #move up the tree to find the top level widget
    rows = [{'ParentID': w_id},]
    while rows[0]["ParentID"] and not rows[0]["ParentID"] == "GLOBAL":
      w_id = rows[0]["ParentID"]
      new_x,new_y = self.get_widgets_coords(w_id)
      x,y = (x+new_x, y+new_y)
      rows = self.db_manager.get_rows("Widgets", ["ParentID"], match_col="ID", match=w_id)
    return (x,y)

  def get_widgets_coords(self, w_id):
    coord_res = self.db_manager.get_rows("Widgets", ["X", "Y"], match_col="ID", match=w_id)
    if not len(coord_res):
      return (None, None)
    return (coord_res[0]["X"], coord_res[0]["Y"])
      
  def add_style(self, path):
    #try:
    cssProvider = Gtk.CssProvider()
    screen = Gdk.Screen.get_default()
    styleContext = Gtk.StyleContext()    
    styleContext.remove_provider_for_screen(screen, cssProvider)
    cssProvider.load_from_path(path)
    styleContext.add_provider_for_screen(screen, cssProvider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_USER)
