import gi, os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf, Gio
import json
from popups.popup import PopupConfirm, PopupMsg, ValueEnter, Keyboard, SaveFile, OpenFile
from backend.widget_classes.factory import WidgetFactory, WIDGET_TYPES

from backend.widget_classes.widget import Widget
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

    self.conn_button = Gtk.Button(width_request = 40)
    self.conn_button.connect('clicked',self.setup_connection)
    self.conn_button.set_sensitive(False)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Connection.png', 40, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.conn_button.add(image)
    self.nav_button_bar.add(self.conn_button)

    self.tag_button = Gtk.Button(width_request = 40)
    self.tag_button.connect('clicked',self.setup_tags,None)
    self.tag_button.set_sensitive(False)
    p_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale('./Public/images/Tag.png', 40, -1, True)
    image = Gtk.Image(pixbuf=p_buf)
    self.tag_button.add(image)
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

  
  def build_panel_clicked(self,widget,event,*args):
    widget_found = False

    #######################Could put base panel click with item click on top so have two connects and one override the other if click in smaller location
    #######################double click to go down
    #######################tree view would have check marks to make visible
    #######################treeveiw popover would have edit and add widget if it is a group, otherwise just edit for highlighted'upda widget
    if event.button == 1:
      #Left Click
      if self.active_display == None:
        return
      if self.widget_clicked != None:
        if self.global_reference != None:
          display_rows = self.db_manager.get_rows("Widgets", Widget.base_parmas, "ParentID", self.global_reference)
        else:
          display_rows = self.db_manager.get_rows("Widgets", Widget.base_parmas, "ParentID", self.widget_clicked)
      else:
        display_rows = self.db_manager.get_rows("Widgets", Widget.base_parmas, "ParentID", self.active_display)
      #keeps track of upper left hand corner of widget clicked on so that groups of widgets can be selected
      absolute_x = event.x - self.global_coordinates['abs_x']
      absolute_y = event.y - self.global_coordinates['abs_y']
      if (self.global_coordinates['x'] <= event.x <= (self.global_coordinates['x']+self.global_coordinates['width'])) and (self.global_coordinates['y'] <= event.y <= (self.global_coordinates['height']+self.global_coordinates['y'])):
        #if user has group selected and then clicks within group but not on a new widget within the group.  Prevents the group from being de-selected
        widget_found = True
      elif (self.global_coordinates['x'] >= absolute_x or absolute_x >= (self.global_coordinates['x']+self.global_coordinates['width'])) or (self.global_coordinates['y'] >= absolute_y or absolute_y >= (self.global_coordinates['height']+self.global_coordinates['y'])):
        #user clicked outside current widget selected so now research active panel to see if new widget was clicked or de-selected widget
        if self.widget_clicked != None:
          self.global_reference = None
          self.widget_clicked = None
          self.global_coordinates = {'x':0,'y':0,'width':0,'height':0,'abs_x':0,'abs_y':0}
          absolute_x = event.x
          absolute_y = event.y
          display_rows = self.db_manager.get_rows("Widgets", Widget.base_parmas, "ParentID", self.active_display)

      if len(display_rows) == 0:
        if (self.global_coordinates['x'] <= absolute_x <= (self.global_coordinates['x']+self.global_coordinates['width'])) and (self.global_coordinates['y'] <= absolute_y <= (self.global_coordinates['height']+self.global_coordinates['y'])):
          #User clicked on same widget but it is the base widget
          widget_found = True

      else:
        for dr in range(len(display_rows)):
          #print('length=',len(display_rows),display_rows[dr]['ID'],display_rows[dr]['X'],absolute_x,display_rows[dr]['Width'],display_rows[dr]['Y'],absolute_y,display_rows[dr]['Height'])
          if (display_rows[dr]['X'] <= absolute_x <= (display_rows[dr]['X']+display_rows[dr]['Width'])) and (display_rows[dr]['Y'] <= absolute_y <= (display_rows[dr]['Height']+display_rows[dr]['Y'])):
            #Found item that user clicked on
            if display_rows[dr]['GlobalReference'] != None and display_rows[dr]['GlobalReference'] != '':
              #if the item selected has a global reference ('Group') then search within group
              self.global_reference = display_rows[dr]['GlobalReference']
            else:
              self.global_reference = None
            widget_found = display_rows[dr]['ID']
            self.widget_clicked = display_rows[dr]['ID']
            self.global_coordinates['x'] = display_rows[dr]['X']
            self.global_coordinates['y'] = display_rows[dr]['Y']
            self.global_coordinates['width'] = display_rows[dr]['Width']
            self.global_coordinates['height'] = display_rows[dr]['Height']
            self.global_coordinates['abs_x'] = self.global_coordinates['abs_x'] + display_rows[dr]['X']
            self.global_coordinates['abs_y'] = self.global_coordinates['abs_y'] + display_rows[dr]['Y']
            self.add_widget_highlight(self.widget_clicked)
            self.update_settings_panel(self.widget_clicked)
            break
      if not widget_found:
        #widget not found within group selected or where user clicked
        self.global_reference = None
        self.widget_clicked = None
        self.global_coordinates = {'x':0,'y':0,'width':0,'height':0,'abs_x':0,'abs_y':0}
        self.add_widget_highlight(self.active_display)
        self.update_settings_panel(self.active_display)
    elif event.button == 3: #right click
      rect = Gdk.Rectangle()
      rect.x = event.x
      rect.y = event.y + 10
      rect.width = rect.height = 1
      popover = Gtk.Popover(width_request = 200)
      vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
      edit_btn = Gtk.ModelButton(label="Properties", name=self.widget_clicked)
      cb = lambda btn: self.open_widget_popup(btn)
      edit_btn.connect("clicked", cb)
      vbox.pack_start(edit_btn, False, True, 10)
      popover.add(vbox)
      popover.set_position(Gtk.PositionType.RIGHT)
      popover.set_relative_to(self.hmi_layout)
      popover.set_pointing_to(rect)
      popover.show_all()
      sc = popover.get_style_context()
      sc.add_class('popover-bg')
      sc.add_class('font-16')


  def refresh_panel(self,w_id,p_id,*args):
    return # for now
    #w_id = which widget was selected
    #p_id = which panel is currently being displayed
    if w_id == None:
      self.global_coordinates = {'x':0,'y':0,'width':0,'height':0,'abs_x':0,'abs_y':0}  #refresh widget global coordinates
    g_displays = 0
    for c in self.build_panel.get_children():
      self.build_panel.remove(c)
    for c in self.hmi_layout.get_children():
      self.hmi_layout.remove(c)
    self.build_panel.add(self.hmi_layout)
    params = self.db_manager.get_rows("Widgets", Widget.base_parmas, "ID", p_id)[0]
    if params["ParentID"] == "GLOBAL":
      g_displays +=1
      d_name = u'GLOBAL_DISPLAY_{}'.format(g_displays)
      params["Display"] = d_name
      if not params["Class"] or not len(params["Class"]):
        w_class = Widget
      else:
        w_class = WIDGET_TYPES[params["Class"]]
      w_class(self.factory, self.hmi_layout, params)
      pass # make generic display and add global to it
    else:
      params["Display"] = params["ID"] #display is its own parent
      self.display = DisplayWidget(self.factory, self.hmi_layout, params, replacements=[])
    self.add_click_panel(self.active_display)
    self.add_widget_highlight(w_id)
    self.update_settings_panel(w_id)
    self.build_panel.show_all()

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
      self.settings_panel.add(nb)
      #nb.append_page(BuilderToolsWidget(self, row), Gtk.Label(label="Basic"))
      nb.append_page(Gtk.Box(), Gtk.Label(label=f"{widget.id} Basic"))
      nb.append_page(Gtk.Box(), Gtk.Label(label=f"{widget.id} Advanced"))
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
