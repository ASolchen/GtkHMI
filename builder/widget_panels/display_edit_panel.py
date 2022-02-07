import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk




class DisplayEditPanel(Gtk.Box):
  def __init__(self, builder_ui) -> None:
      super().__init__()
      self.hmi_layout = builder_ui.hmi_layout
      self.add(self.hmi_layout)