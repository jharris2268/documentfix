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


root2 = 2.0**0.5

class ImageView:
    def __init__(self, image):
        self.set_image(image)
    
    
    def __repr__(self):
        return f"ImageView[({self.image.width} {self.image.height}): cx={self.center_x} cy={self.center_y} sc={self.scale}]"
    
    def set_image(self, image):
        self.image=image
        if self.image:
            self.surface = surface_from_pil(image)
        
        self.zoom_all()
        
        
    def update_matrix(self):
        m = cairo.Matrix(x0=self.image.width/2, y0=self.image.height/2)
        m = m.multiply(cairo.Matrix(xx=self.scale, yy=self.scale))
        m = m.multiply(cairo.Matrix(x0=-self.center_x, y0=-self.center_y))
               
        self.matrix = m
    
    def zoom_all(self):
        if not self.image:
            self.center_x,self.center_y,self.scale=0,0,1
            return
            
        self.center_x = self.image.width/2
        self.center_y = self.image.height/2
        
        self.scale = 1
        self.update_matrix()
        
    def zoom_by(self, x, y, zoom_factor):
        if not self.image:
            self.center_x,self.center_y,self.scale=0,0,1
            return
        
        
        self.center_x += (self.center_x - x)*zoom_factor
        self.center_y += (self.center_y - y)*zoom_factor
        self.scale *= zoom_factor
        if abs(self.scale - round(self.scale))<0.001:
            self.scale = round(self.scale)
        self.update_matrix()
        
    def zoom_in(self, x, y):
        self.zoom_by(x,y,root2)
    def zoom_out(self, x, y):
        self.zoom_by(x,y, 1/root2)
    
    
    def move(self, x, y):
        if not self.image:
            self.center_x,self.center_y,self.scale=0,0,1
            
        self.center_x += x
        self.center_y += y
        self.update_matrix()
        
        
    def draw(self, c, width, height):
        if not self.image:
            return
        print('draw',self, width, height)
        
        
        sc = min((width-10)/self.image.width, (height-10)/self.image.height)
        m = self.matrix.multiply(cairo.Matrix(x0=-self.center_x, y0=-self.center_y))
        m = m.multiply(cairo.Matrix(xx=sc, yy=sc))
        m = m.multiply(cairo.Matrix(x0=width/2, y0=height/2))
        print(m)
        c.save()
        c.set_matrix(m)
        c.set_source_surface(self.surface)
        c.paint()
        return self.scale / sc
        
    def transform(self, x,y, width, height):
        sc = min((width-10)/self.image.width, (height-10)/self.image.height)
        scinv = 1/sc
        m=cairo.Matrix(x0=-width/2, y0=-height/2)
        m=m.multiply(cairo.Matrix(xx=scinv, yy=scinv))
        m=m.multiply(cairo.Matrix(x0=self.center_x, y0=self.center_y))
        
        xx,yy=m.transform_point(x,y)
        return (xx,yy)
        
    
    

class Draw(Gtk.DrawingArea):
    def __init__(self, parent, with_points=False, img=None):
        super().__init__()
        
        self.parent = parent
        self.imv = None
        
        self.set_image(img)
        
        
        
        
        
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
        
    def set_image(self, img):
        if img:
            self.imv = ImageView(img)
        else:
            self.imv = None
        
    
    def on_click(self, gesture, data, x, y):
        
        if self.imv:
            xx,yy =self.imv.transform(x, y, self.get_width(), self.get_height())
            print(f"on_click: {x} {y} => {xx:0.1f} {yy:0.1f}")
            if len(self.pts)>=4:
                self.pts=[]
            self.pts.append((xx,yy))
        
        self.queue_draw()  # Force a redraw
    
    
    def draw(self, area, c, width, height, data):
        # c is a Cairo context
        #print("draw",width,height,self.scale, self.xoff, self.yoff)
        
        
        c.save()
        c.identity_matrix()
        
        c.move_to(2,2)
        c.line_to(width-2,2)
        c.line_to(width-2,height-2)
        c.line_to(2,height-2)
        c.line_to(2,2)
        c.stroke()
        sc=1
        if self.imv:
            sc=self.imv.draw(c, width, height)
            
            
            
        
        c.set_source_rgb(1,0,0)
        c.set_line_width(5*sc)
        
        if hasattr(self, 'pts'):
            for i,(x,y) in enumerate(self.pts):
                    
                if i>0:
                    c.line_to(x,y)
                    c.stroke()                
                
                #print(f"point at {x} {y} => {x/scale-xoff} {y/scale-yoff}")
                radius = 10 * sc
                c.arc(x, y, radius, 0, 2*np.pi)
                c.fill()
                
                c.move_to(x,y)
                
            if len(self.pts)==4:
                c.line_to(self.pts[0][0],self.pts[0][1])
                
                c.stroke()
            
        c.restore()
    
