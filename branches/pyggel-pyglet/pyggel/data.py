"""
pyggle.data
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The data module holds all classes used to create, store and access OpenGL data,
like textures, display lists and vertex arrays.
"""

from include import *
import view

class Texture(object):
    """An object to load and store an OpenGL texture"""
    def __init__(self, filename, flip=0):
        """Create a texture
           flip indicates whether the texture data needs to be flipped - some formats need this
           filename can be be a filename for an image, or a pygame.Surface object"""
        view.require_init()
        self.filename = filename
        self.flip = flip

        self.size = (0,0)

        self.gl_tex = GLuint()
        glGenTextures(1, ctypes.byref(self.gl_tex))

        if type(filename) is type(""):
            self._load_file()
        else:
            self._compile(filename)
            self.filename = None

    def _get_next_biggest(self, x, y):
        """Get the next biggest power of two x and y sizes"""
        nw = 16
        nh = 16
        while nw < x:
            nw *= 2
        while nh < y:
            nh *= 2
        return nw, nh

    def _load_file(self):
        """Loads file"""
        image = pygame.image.load(self.filename)

        self._compile(image)

    def _compile(self, image):
        """Compiles image data into texture data"""
        size = self._get_next_biggest(*image.get_size())

        image = pygame.transform.scale(image, size)

        tdata = pygame.image.tostring(image, "RGBA", self.flip)
        
        glBindTexture(GL_TEXTURE_2D, self.gl_tex)

        xx, xy = size
        self.size = size
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, xx, xy, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, tdata)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    def bind(self):
        """Binds the texture for usage"""
        glBindTexture(GL_TEXTURE_2D, self.gl_tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    def __del__(self):
        """Clear the texture data"""
        try:
            glDeleteTextures([self.gl_tex])
        except:
            pass #already cleared...


class DisplayList(object):
    """An object to compile and store an OpenGL display list"""
    def __init__(self):
        """Creat the list"""
        self.gl_list = glGenLists(1)

    def begin(self):
        """Begin recording to the list - anything rendered after this will be compiled into the list and not actually rendered"""
        glNewList(self.gl_list, GL_COMPILE)

    def end(self):
        """End recording"""
        glEndList()

    def render(self):
        """Render the display list"""
        glCallList(self.gl_list)

    def __del__(self):
        """Clear the display list data"""
        try:
            glDeleteLists(self.gl_list, 1)
        except:
            pass #already cleared!

class VertexArray(object):
    """An object to store and render an OpenGL vertex array of vertices, colors and texture coords"""
    def __init__(self, render_type=None, max_size=100):
        """Create the array
           render_type is the OpenGL constant used in rendering, ie GL_POLYGON, GL_TRINAGLES, etc.
           max_size is the size of the array"""
        if render_type is None:
            render_type = GL_QUADS
        self.render_type = render_type
        self.texture = create_empty_texture()

        self.max_size = max_size

        self.verts = numpy.empty((max_size, 3), dtype=object)
        self.colors = numpy.empty((max_size, 4), dtype=object)
        self.texcs = numpy.empty((max_size, 2), dtype=object)

    def render(self):
        """Render the array"""
        self.texture.bind()

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        assert len(self.verts) == len(self.colors) == len(self.texcs)
        num = len(self.verts)

        vv = []
        for i in self.verts:
            a, b, c = i
            if a == None:
                a = 0.0
            if b == None:
                b = 0.0
            if c == None:
                c = 0.0
            vv.extend((a,b,c))
        vv = (GLfloat*(num*3))(*vv)

        cc = []
        for i in self.colors:
            a, b, c, d = i
            if a == None:
                a = 0.0
            if b == None:
                b = 0.0
            if c == None:
                c = 0.0
            if d == None:
                d = 0.0
            cc.extend((a,b,c,d))
        cc = (GLfloat*(num*4))(*cc)

        tt = []
        for i in self.texcs:
            a, b = i
            if a == None:
                a = 0.0
            if b == None:
                b = 0.0
            tt.extend((a,b))
        tt = (GLfloat*(num*2))(*tt)

        glVertexPointer(3, GL_FLOAT, 0, vv)
        glColorPointer(4, GL_FLOAT, 0, cc)
        glTexCoordPointer(2, GL_FLOAT, 0, tt)

        glDrawArrays(self.render_type, 0, self.max_size)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

def create_empty_texture(size=(2,2), color=(1,1,1,1)):
    """Create an empty data.Texture
       size must be a two part tuple representing the pixel size of the texture
       color must be a four-part tuple representing the (RGBA 0-1) color of the texture"""
    i = pygame.Surface(size)
    if len(color) == 4:
        r, g, b, a = color
    else:
        r, g, b = color
        a = 1
    r *= 255
    g *= 255
    b *= 255
    a *= 255
    i.fill((r,g,b,a))
    return Texture(i)

x = view.require_init #bypass the textures not wanting to load before init, blank texture doesn't require it...
view.require_init = lambda: None
blank_texture = create_empty_texture()
view.require_init = x
