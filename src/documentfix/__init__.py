import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Graphene', '1.0')
from gi.repository import Gtk, Gdk, Adw, Graphene

from .gui import MainWindow

class MyApp(Adw.Application):
    def __init__(self, src, dest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connect('activate', self.on_activate)
        self.src=src
        self.dest=dest
        
        sm = self.get_style_manager()
        sm.set_color_scheme(Adw.ColorScheme.PREFER_DARK)

    def on_activate(self, app):
        self.win = MainWindow(self.src, self.dest, application=app)
        self.win.present()

def main():
    src = '/home/james/railway/middletonpress/Waterloo_To_Woking/rawpages'
    dest='/home/james/railway/middletonpress/Waterloo_To_Woking/pages'
    
    app = MyApp(src, dest, application_id="com.example.GtkApplication")
    app.run(sys.argv)
