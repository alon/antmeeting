import Image
import gtk
from numpy import sin

im = Image.new('RGB', (100,100))
imdata = im.getdata()
pixels = imdata.pixel_access()
for i in xrange(100): pixels[i,i]=(i,255-i,255-i)
for i in xrange(100): pixels[99-i,i]=(i,255-i,255-i)
pixbuf=gtk.gdk.pixbuf_new_from_data(
    im.tostring(),
    gtk.gdk.COLORSPACE_RGB,
    False,
    8,
    im.size[0],
    im.size[1],
    3*im.size[0])
pixmap,mask = pixbuf.render_pixmap_and_mask()
gpixmap = gtk.Pixmap(pixmap,mask)
w = gtk.Window()
w.add(gpixmap)
w.show_all()
#for i in xrange(100):
#    pixels[99-min(sin(float(i)/50)*50,99),i]=(i,255-i,255-i)
import gobject
def inverse():
    pixbuf.pixel_array[:,:,:] = 255 - pixbuf.pixel_array[:,:,:]
    pixbuf.render_to_drawable(pixmap, pixmap.new_gc(),
        0, 0, 0, 0, pixbuf.get_width(), pixbuf.get_height())
    gpixmap.queue_draw()
    return True

gobject.timeout_add(100, inverse)
gtk.main()

