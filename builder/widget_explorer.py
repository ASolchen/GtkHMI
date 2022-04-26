import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
from backend.widget_classes.widget import Widget
from backend.widget_classes.display import DisplayWidget


class ProjectTree(Gtk.TreeView):
    pass



class WidgetExplorer(Gtk.ScrolledWindow):
    def __init__(self, builder_ui):
        Gtk.ScrolledWindow.__init__(self)
        self.app = builder_ui.app
        self.db_session = self.app.db_manager.project_db.session
        self.widget_tree_data = {} #stores a list of widget tree iter and ID
        self.tree_columns = ["Display id", "description"]
        self.widget_data = Gtk.TreeStore(int, str)
        self.widget_tree = Gtk.TreeView(self.widget_data) # put the list in the Treeview
        self.widget_tree.connect("button_press_event", self.tree_item_clicked)
        self.widget_tree.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        for i, col_title in enumerate(self.tree_columns):
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(col_title, renderer, text=i)
            col.set_sort_column_id(i)
            self.widget_tree.append_column(col)
        self.add(self.widget_tree)
        self.build_widget_tree()
        

    def build_widget_tree(self):
        self.widget_data.clear()
        d_res = self.db_session.query(Widget.orm_model).join(DisplayWidget.orm_model)\
            .filter(Widget.orm_model.id == DisplayWidget.orm_model.id)\
            .all()
        for d in d_res:
            self.widget_data.insert(None, -1, (d.id, d.description))
        self.show_all()
        

    
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
            rect.y = event.y + 20
            rect.width = rect.height = 1
            selection = treeview.get_selection()
            tree_model, tree_iter = selection.get_selected()
            popover = Gtk.Popover(width_request = 200)
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            if tree_iter is None:
                #popover to add display
                add_display_btn = Gtk.ModelButton(label="Add Display",name=None)
                add_display_btn.connect("clicked", lambda btn: self.add_display())
                vbox.pack_start(add_display_btn, False, True, 0)
                #return
            else:
                w_id = tree_model[tree_iter][0]
                open_btn = Gtk.ModelButton(label="Open")
                dup_btn = Gtk.ModelButton(label="Duplicate")
                #edit_btn.connect("clicked", cb)
                for btn in [open_btn, dup_btn]:
                    vbox.pack_start(btn, False, True, 10)
            popover.add(vbox)
            popover.set_position(Gtk.PositionType.RIGHT)
            popover.set_relative_to(treeview)
            popover.set_pointing_to(rect)
            popover.show_all()
            return
        else:
            return
        selection = treeview.get_selection()
        tree_model, tree_iter = selection.get_selected()
        #Rebuild panel with widgets
        if tree_iter is not None:
            w_id = tree_model[tree_iter][0]
            self.open_display(w_id)

    def open_display(self, w_id):
            self.app.widget_factory.kill_all()
            self.app.widget_factory.open_display(w_id)