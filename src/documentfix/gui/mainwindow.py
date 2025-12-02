import gi
from gi.repository import Gtk, Gdk

import os.path

import PIL.Image as Pi

from .imageutils import rotate_left, rotate_right, find_corners, transform_image
from .draw import Draw


def set_spacing(box, is_grid=False):
    if is_grid:
        box.set_row_spacing(10)
        box.set_column_spacing(10)
    else:
        box.set_spacing(10)
    box.set_margin_top(10)
    box.set_margin_bottom(10)
    box.set_margin_start(10)
    box.set_margin_end(10)        

def add_entry(grid, hint_text, col_off, row_off):
    entry_buffer = Gtk.EntryBuffer()
    
    entry = Gtk.Entry()
    entry.set_buffer(entry_buffer)
    entry.set_max_length(10)
    entry.set_input_purpose(Gtk.InputPurpose.NUMBER)
    entry.set_tooltip_text(hint_text)
    #entry.set_has_frame(False)
    
    grid.attach(entry, col_off+1, row_off,1,1)
    
    return entry_buffer

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, src, dest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(1200, 800)
        self.set_title("Document Fix")
        
        self.src = src
        self.dest=dest
        
        self.src_files=sorted(os.listdir(self.src))
        self.img = Pi.open(os.path.join(self.src, self.src_files[0]))
        
        
        
        main_box = Gtk.Grid()
        set_spacing(main_box,True)
        self.set_child(main_box)
        
        self.left_draw = Draw(self, True, self.img)
        self.left_draw.set_size_request(500,700)
        main_box.attach(self.left_draw, 0, 0, width=10, height=10)
        
        self.right_draw = Draw(self)
        
        self.right_draw.set_size_request(500,700)
        main_box.attach(self.right_draw, 10, 0, width=10, height=10)
        
        self.next_button = Gtk.Button(label="Next")
        main_box.attach(self.next_button, 8, 10,1,1)
        
        self.rotate_left_button = Gtk.Button(label="Rotate Left")
        main_box.attach(self.rotate_left_button, 9, 10,1,1)
        self.rotate_left_button.connect('clicked', self.rotate_left)
        
        
        self.rotate_right_button = Gtk.Button(label="Rotate Right")
        main_box.attach(self.rotate_right_button, 10, 10,1,1)
        self.rotate_right_button.connect('clicked', self.rotate_right)
        
        self.process_button = Gtk.Button(label="Process")
        main_box.attach(self.process_button, 11, 10,1,1)
        self.process_button.connect('clicked', self.process)
        
        page_number_label = Gtk.Label(label="Page Num")
        main_box.attach(page_number_label, 12, 10,1,1)
        self.page_number_text = Gtk.Entry()
        main_box.attach(self.page_number_text, 13, 10, width=3,height=1)
        
        self.save_button = Gtk.Button(label="Save")
        main_box.attach(self.save_button, 16, 10,1,1)
        
    
    def redraw(self):
        self.left_draw.queue_draw()
        self.right_draw.queue_draw()
    
            
    def rotate_left(self, evt):
        
        self.img = rotate_left(self.img)
        self.left_draw.set_image(self.img)
        self.redraw()
        
    def rotate_right(self, evt):
        
        self.img = rotate_right(self.img)
        self.left_draw.set_image(self.img)
        self.redraw()
    
    def process(self, evt):
        
        corners = find_corners(self.left_draw.pts)
        self.processed_img = transform_image(self.img, corners)
        
        self.right_draw.set_image(self.processed_img)
        self.redraw()
    
    
    def close(self, *args):
        print("clicked", args)
        super().close()
    
