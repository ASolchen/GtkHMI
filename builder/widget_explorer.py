import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk




class WidgetExplorer(Gtk.ScrolledWindow):
  def __init__(self, builder_ui):
    Gtk.ScrolledWindow.__init__(self)
    self.widget_tree_data = {} #stores a list of widget tree iter and ID
    self.tree_columns = ["ID", "ParentID", "Class"]
    self.widget_data = Gtk.TreeStore(str, str, str)
    self.widget_tree = Gtk.TreeView(self.widget_data) # put the list in the Treeview
    self.widget_tree.connect("button_press_event", self.tree_item_clicked)
    self.widget_tree.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
    for i, col_title in enumerate(self.tree_columns):
      renderer = Gtk.CellRendererText()
      col = Gtk.TreeViewColumn(col_title, renderer, text=i)
      col.set_sort_column_id(i)
      self.widget_tree.append_column(col)    

  def build_widget_tree(self):
    self.widget_data.clear()
    style_res = self.db_manager.get_rows("ApplicationSettings", ["Stylesheet"])
    if len(style_res):
      style_file = style_res[0]["Stylesheet"]
      self.add_style(style_file)
    self.get_widgets(None, None)
    self.get_widgets(None, "GLOBAL")
  
  def enable_widgets(self,*args):
    #put items in here want to be enabled after database is opened
    self.tag_button.set_sensitive(True)
    self.conn_button.set_sensitive(True)

  def get_widgets(self, parent_iter, parent_id):
    if not parent_id:
      rows = self.db_manager.run_query(
        'SELECT [ID], [ParentID], [Class] FROM [Widgets] WHERE [ParentID] IS NULL ORDER BY [BuildOrder] ASC, [ID] ASC')
    elif parent_id == "GLOBAL":
      rows = self.db_manager.run_query(
        'SELECT [ID], [ParentID], [Class] FROM [Widgets] WHERE [ParentID] IS "GLOBAL" ORDER BY [BuildOrder] ASC, [ID] ASC')
    else:
      rows = self.db_manager.run_query(
        'SELECT [ID], [ParentID], [Class] FROM [Widgets] WHERE [ParentID] = ? ORDER BY [BuildOrder] ASC, [ID] ASC', [parent_id])
    for row in rows:
      store_row = []
      for col in self.tree_columns:
        store_row.append(row[col])
      widget_data_iter = self.widget_data.insert(parent_iter, 0, store_row)
      self.widget_tree_data[row[0]]=widget_data_iter
      self.get_widgets(widget_data_iter, row[0])

  def tree_right_click(self, action, param):
    about_dialog = Gtk.AboutDialog(transient_for=self, modal=True)
    about_dialog.present()


  def tree_item_clicked(self, treeview, event):
    pthinfo = treeview.get_path_at_pos(event.x, event.y)
    if event.button == 1: #left click
      pthinfo = treeview.get_path_at_pos(event.x, event.y)
      if pthinfo != None:
        path,col,cellx,celly = pthinfo
        treeview.grab_focus()
        treeview.set_cursor(path,col,0)
        #update currently active display
        selection = treeview.get_selection()
        tree_model, tree_iter = selection.get_selected()
        self.active_display = tree_model[tree_iter][0]
        self.base_panel_open = tree_model[tree_iter][0]
        self.global_reference = None
      else:
        #unselect row in treeview
        selection = treeview.get_selection()
        selection.unselect_all()
    elif event.button == 3: #right click
      rect = Gdk.Rectangle()
      rect.x = event.x
      rect.y = event.y + 10
      rect.width = rect.height = 1
      selection = treeview.get_selection()
      tree_model, tree_iter = selection.get_selected()
      popover = Gtk.Popover(width_request = 200)
      vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
      if tree_iter is None:
        #popover to add display
        add_display_btn = Gtk.ModelButton(label="Add Display",name=None)
        cb = lambda btn: self.add_display(btn)
        add_display_btn.connect("clicked", cb)
        vbox.pack_start(add_display_btn, False, True, 10)
        #return
      else:
        w_id = tree_model[tree_iter][0]
        edit_btn = Gtk.ModelButton(label="Edit", name=w_id)
        cb = lambda btn: self.open_widget_popup(btn)
        edit_btn.connect("clicked", cb)
        vbox.pack_start(edit_btn, False, True, 10)
        class_type = tree_model[tree_iter][2]
        if class_type == 'display':
          add_btn = Gtk.ModelButton(label="Add Widget", name=w_id)
          cb = lambda btn:self.add_widget(btn)
          add_btn.connect("clicked", cb)
          vbox.pack_start(add_btn, False, True, 10)
      popover.add(vbox)
      popover.set_position(Gtk.PositionType.RIGHT)
      popover.set_relative_to(treeview)
      popover.set_pointing_to(rect)
      popover.show_all()
      sc = popover.get_style_context()
      sc.add_class('popover-bg')
      sc.add_class('font-16')
      return
    else:
      return
    selection = treeview.get_selection()
    tree_model, tree_iter = selection.get_selected()
    #Rebuild panel with widgets
    if tree_iter is not None:
      w_id = tree_model[tree_iter][0]
      #self.active_widget = w_id
      p_id = self.get_widgets_display(w_id)
      self.refresh_panel(w_id,p_id)
