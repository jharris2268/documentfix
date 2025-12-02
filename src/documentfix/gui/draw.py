import gi
from gi.repository import Gtk, Gdk

import cairo
import numpy as np


def surface_from_pil(im, alpha=1.0, format=cairo.FORMAT_ARGB32):
    """
    :param im: Pillow Image
    :param alpha: 0..1 alpha to add to non-alpha images
    :param format: Pixel format for output surface
    """
    assert format in (
        cairo.FORMAT_RGB24,
        cairo.FORMAT_ARGB32,
    ), f"Unsupported pixel format: {format}"
    if 'A' not in im.getbands():
        im.putalpha(int(alpha * 256.))
    arr = bytearray(im.tobytes('raw', 'BGRa'))
    surface = cairo.ImageSurface.create_for_data(arr, format, im.width, im.height)
    return surface



class Draw(Gtk.DrawingArea):
    def __init__(self, parent, with_points=False, img=None):
        super().__init__()
        
        self.parent = parent
        
        self.surface = None
        
        if img:
            self.prep_surface(img)
        else:
            self.prep_scale_offset()
        
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_draw_func(self.draw, None)
        
        if with_points:
            evk = Gtk.GestureClick.new()
            evk.connect("pressed", self.on_click)  # could be "released"
            self.add_controller(evk)

            self.pts=[]
        
        cursor_crosshair = Gdk.Cursor.new_from_name("crosshair")
        self.set_cursor(cursor_crosshair)
        
    def resize(self, width, height):
        super().resize(width,height)
        self.prep_scale_offset(width,height)
        
    def prep_surface(self, img):
        self.surface = surface_from_pil(img)        
        self.prep_scale_offset()
        
    def prep_scale_offset(self,width=None,height=None):
        if width is None:
            width, height = self.get_content_width(), self.get_content_height()
        if width==0 or height==0 or self.surface is None:
            self.scale=1
            self.xoff=0
            self.yoff=0
            return
            
        self.scale = min((width-10)/self.surface.get_width(), (height-10)/self.surface.get_height())
        self.xoff = (width - self.surface.get_width()*self.scale)/2
        self.yoff = (height - self.surface.get_height()*self.scale)/2
        print(f"scale={self.scale}, xoff={self.xoff}, yoff={self.yoff}")
    
    
    
        
    
    def on_click(self, gesture, data, x, y):
        xx = (x-self.xoff)/self.scale
        yy = (y-self.yoff)/self.scale
        print(f"on_click: {x} {y} => {xx:0.1f} {yy:0.1f}")
        if len(self.pts)>=4:
            self.pts=[]
        self.pts.append((xx,yy))
        
        self.queue_draw()  # Force a redraw
    
    
    def draw(self, area, c, width, height, data):
        # c is a Cairo context
        print("draw",width,height,self.scale, self.xoff, self.yoff)
        
        
        c.save()
        c.identity_matrix()
        
        c.move_to(2,2)
        c.line_to(width-2,2)
        c.line_to(width-2,height-2)
        c.line_to(2,height-2)
        c.line_to(2,2)
        c.stroke()
        
        self.prep_scale_offset(width,height)
        c.translate(self.xoff,self.yoff)
        c.scale(self.scale,self.scale)
        
        
                
        # Fill background with a colour
        if self.surface:
            c.set_source_surface(self.surface)
            c.paint()
            
            
        
        c.set_source_rgb(1,0,0)
        if hasattr(self, 'pts'):
            for i,(x,y) in enumerate(self.pts):
                    
                if i>0:
                    c.line_to(x,y)
                    c.stroke()                
                
                #print(f"point at {x} {y} => {x/scale-xoff} {y/scale-yoff}")
                radius = 10 / self.scale
                c.arc(x, y, radius, 0, 2*np.pi)
                c.fill()
                
                c.move_to(x,y)
                
            if len(self.pts)==4:
                c.line_to(self.pts[0][0],self.pts[0][1])
                c.stroke()
            
            c.restore()
    
