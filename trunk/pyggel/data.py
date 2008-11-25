"""
pyggle.data
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.
"""

from include import *
import view

class Texture(object):
    def __init__(self, filename, flip=0):
        view.require_init()
        self.filename = filename
        self.flip = 0

        self.size = (0,0)

        self.gl_tex = glGenTextures(1)

        if type(filename) is type(""):
            self._load_file()
        else:
            self._compile(filename)
            self.filename = None

    def _get_next_biggest(self, x, y):
        nw = 16
        nh = 16
        while nw < x:
            nw *= 2
        while nh < y:
            nh *= 2
        return nw, nh

    def _load_file(self):
        image = pygame.image.load(self.filename)

        self._compile(image)

    def _compile(self, image):
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
        glBindTexture(GL_TEXTURE_2D, self.gl_tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    def __del__(self):
        try:
            glDeleteTextures([self.gl_tex])
        except:
            pass #already cleared...


class DisplayList(object):
    """So we don't lose the list between copies/kills"""
    def __init__(self):
        self.gl_list = glGenLists(1)

    def begin(self):
        glNewList(self.gl_list, GL_COMPILE)

    def end(self):
        glEndList()

    def render(self):
        glCallList(self.gl_list)

    def __del__(self):
        try:
            glDeleteLists(self.gl_list, 1)
        except:
            pass #already cleared!
