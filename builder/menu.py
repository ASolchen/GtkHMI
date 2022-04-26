import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk

def my_print(*args):
    print(args)



class Menu(Gtk.MenuBar):
    def __init__(self, builder):
      super(Menu, self).__init__()
      # drop downs
      # file
      self.builder = builder
      self.app = builder.app
      file_menu = Gtk.Menu()
      file_menu_dropdown = Gtk.MenuItem("File")
      self.append(file_menu_dropdown)
      file_menu_dropdown.set_submenu(file_menu)
      # file/project
      prj_menu = Gtk.Menu()
      prj_open = Gtk.MenuItem('Project')
      prj_open.set_tooltip_text("Click here to manage projects")
      prj_open.set_submenu(prj_menu)
      file_menu.append(prj_open)
      # File/Project/New
      new_project = Gtk.MenuItem('New Project')
      new_project.connect("activate", self.confirm_create_db)
      #new_project.connect("activate", callback, arg1, arg2 ...)
      prj_menu.append(new_project)
      # File/Project/Open
      opn_project = Gtk.MenuItem('Open Project')
      opn_project.connect("activate", self.confirm_open_db)
      prj_menu.append(opn_project)
      file_menu.append(Gtk.SeparatorMenuItem())
      file_exit = Gtk.MenuItem("Exit")
      file_menu.append(file_exit)
      #file_exit.connect("activate", lambda *args: self.app.confirm(self.app.shutdown,"Do you really want to exit?"))  
      file_exit.connect("activate", self.app.app_exit)  

      # edit
      edit_menu = Gtk.Menu()
      edit_menu_dropdown = Gtk.MenuItem("Edit")
      edit_menu_dropdown.set_submenu(edit_menu)
      connection_settings = Gtk.MenuItem("Connection Settings")
      #connection_settings.connect("activate", self.root.open_popup, 'connection_settings')
      connection_settings.set_tooltip_text("Click here to open a settings panel for data connections")
      edit_menu.append(connection_settings)
      self.append(edit_menu_dropdown)

      # view
      view_menu = Gtk.Menu()
      view_menu_dropdown = Gtk.MenuItem("View")
      view_menu_dropdown.set_submenu(view_menu)
      dark_mode_toggle = Gtk.MenuItem("Toggle Dark Mode")
      dark_mode_toggle.connect("activate", self.toggle_dark_mode)
      dark_mode_toggle.set_tooltip_text("Click here to toggle application dark mode")
      view_menu.append(dark_mode_toggle)
      self.append(view_menu_dropdown)

      # Objects
      objects_menu_dropdown = Gtk.MenuItem("Objects")
      self.append(objects_menu_dropdown)
      objects_menu = Gtk.Menu()
      objects_menu_dropdown.set_submenu(objects_menu)
      select = Gtk.MenuItem("Select")
      objects_menu.append(select)
      rotate = Gtk.MenuItem("Rotate")
      objects_menu.append(rotate)
      objects_menu.append(Gtk.SeparatorMenuItem())
      drawing = Gtk.MenuItem("Drawing")
      objects_menu.append(drawing)
      #>>>Drawing Widgets
      drawing_widgets = Gtk.Menu()
      drawing.set_submenu(drawing_widgets)
      text_widget = Gtk.MenuItem("Text")
      drawing_widgets.append(text_widget)
      image_widget = Gtk.MenuItem("Image")
      drawing_widgets.append(image_widget)
      panel_widget = Gtk.MenuItem("Panel")
      drawing_widgets.append(panel_widget)
      drawing_widgets.append(Gtk.SeparatorMenuItem())
      arc_widget = Gtk.MenuItem("Arc")
      drawing_widgets.append(arc_widget)
      ellipse_widget = Gtk.MenuItem("Ellipse")
      drawing_widgets.append(ellipse_widget)
      freehand_widget = Gtk.MenuItem("Freehand")
      drawing_widgets.append(freehand_widget)
      line_widget = Gtk.MenuItem("Line")
      drawing_widgets.append(line_widget)
      polygon_widget = Gtk.MenuItem("Polygon")
      drawing_widgets.append(polygon_widget)
      polyline_widget = Gtk.MenuItem("Polyline")
      drawing_widgets.append(polyline_widget)
      rectangle_widget = Gtk.MenuItem("Rectangle")
      drawing_widgets.append(rectangle_widget)

      push_btn = Gtk.MenuItem("Push Button")
      objects_menu.append(push_btn)
      #>>>Push Button Widgets
      button_widgets = Gtk.Menu()
      push_btn.set_submenu(button_widgets)
      button_widget = Gtk.MenuItem("Button")
      button_widgets.append(button_widget)
      momentary_widget = Gtk.MenuItem("Momentary")
      button_widgets.append(momentary_widget)
      maintaned_widget = Gtk.MenuItem("Maintaned")
      button_widgets.append(maintaned_widget)
      latched_widget = Gtk.MenuItem("Latched")
      button_widgets.append(latched_widget)
      multistate_widget = Gtk.MenuItem("Multistate")
      button_widgets.append(multistate_widget)
      interlocked_widget = Gtk.MenuItem("Interlocked")
      button_widgets.append(interlocked_widget)
      ramp_widget = Gtk.MenuItem("Ramp")
      button_widgets.append(ramp_widget)
      navigation_widget = Gtk.MenuItem("Navigation")
      button_widgets.append(navigation_widget)


      numeric_and_string = Gtk.MenuItem("Numeric and String")
      objects_menu.append(numeric_and_string)
      #>>>Number and String Widgets
      num_and_str_widgets = Gtk.Menu()
      numeric_and_string.set_submenu(num_and_str_widgets)
      numeric_display_widget = Gtk.MenuItem("Numeric Display")
      num_and_str_widgets.append(numeric_display_widget)
      numeric_input_widget = Gtk.MenuItem("Numeric Input")
      num_and_str_widgets.append(numeric_input_widget)
      num_and_str_widgets.append(Gtk.SeparatorMenuItem())
      string_display_widget = Gtk.MenuItem("String Display")
      num_and_str_widgets.append(string_display_widget)
      string_input_widget = Gtk.MenuItem("String Input")
      num_and_str_widgets.append(string_input_widget)

      indicator = Gtk.MenuItem("Indicator")
      objects_menu.append(indicator)
      #>>>Indicator Widgets
      ind_widgets = Gtk.Menu()
      indicator.set_submenu(ind_widgets)
      m_state_ind_widget = Gtk.MenuItem("Mulistate")
      ind_widgets.append(m_state_ind_widget)
      sym_ind_widget = Gtk.MenuItem("Symbol")
      ind_widgets.append(sym_ind_widget)
      list_ind_widget = Gtk.MenuItem("List")
      ind_widgets.append(list_ind_widget)

      gauge_and_graph = Gtk.MenuItem("Gauge and Graph")
      objects_menu.append(gauge_and_graph)
      #>>>Gauge and Graph Widgets
      gauge_widgets = Gtk.Menu()
      gauge_and_graph.set_submenu(gauge_widgets)

      key = Gtk.MenuItem("Key")
      objects_menu.append(key)
      trending = Gtk.MenuItem("Trending")
      objects_menu.append(trending)
      advanced = Gtk.MenuItem("Advanced")
      objects_menu.append(advanced)
      alarm_and_event = Gtk.MenuItem("Alarm and Event")
      objects_menu.append(alarm_and_event)

      #Arrange
      arrange_menu_dropdown = Gtk.MenuItem("Arrange")
      self.append(arrange_menu_dropdown)

      #Animation
      animation_menu_dropdown = Gtk.MenuItem("Animation")
      self.append(animation_menu_dropdown)

      #Tools
      tools_menu_dropdown = Gtk.MenuItem("Tools")
      self.append(tools_menu_dropdown)

      #Arrange
      help_menu_dropdown = Gtk.MenuItem("Help")
      self.append(help_menu_dropdown)

    def confirm_open_db(self, *args):
      if len(self.app.db):
          self.builder.confirm(self.builder.open_database_req, "Close current project and open another?") 
      else:
          self.builder.open_database_req()

    def confirm_create_db(self, *args):
        if len(self.app.db):
            self.builder.confirm(self.builder.create_database_req, "Close current project and create new?")
        else:
            self.builder.create_database_req()

    def toggle_dark_mode(self, widget):
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme",
                            not settings.get_property("gtk-application-prefer-dark-theme"))
