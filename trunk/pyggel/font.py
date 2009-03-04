"""
pyggle.font
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The font module contains classes to display text images.
"""

from include import *
import image, view

class Font(object):
    """A font object used for rendering text to images"""
    def __init__(self, filename=None, fsize=32):
        """Create the font
           filename can be None or the filename of the font to load (TTF)
           fsize is the size of the font"""
        view.require_init()
        self.filename = filename
        self.fsize = fsize
        self.fontname = str(self.filename) + ":" + str(self.fsize)

        self._load_font()

    def _load_font(self):
        """Load the font"""
        self.pygame_font = pygame.font.Font(self.filename, self.fsize)

    def make_text_image(self, text="", color=(1,1,1,1)):
        """Create an image.Image object with the text rendered to it.
           text is the text to render
           color is the color of the text (0-1 RGBA)"""
        if "\n" in text:
            text = text.split("\n")
            n = []
            h = self.pygame_font.get_height()
            w = 0
            tot = 0
            for i in text:
                n.append(self.pygame_font.render(i, True, (255, 255, 255)))
                nw = n[-1].get_width()
                if nw > w:
                    w = nw
                tot += h
            new = pygame.Surface((w, tot)).convert_alpha()
            new.fill((0,0,0,0))
            tot = 0
            for i in n:
                new.blit(i, (0, tot*h))
                tot += 1
            return image.Image(new, colorize=color)
            
        else:
            return image.Image(self.pygame_font.render(text, True, (255,255,255)),
                               colorize=color)

    def make_text_image3D(self, text="", color=(1,1,1,1)):
        """Create an image.Image3D object with the text rendered to it.
           text is the text to render
           color is the color of the text (0-1 RGBA)"""
        if "\n" in text:
            text = text.split("\n")
            n = []
            h = self.pygame_font.get_height()
            w = 0
            tot = 0
            for i in text:
                n.append(self.pygame_font.render(i, True, (255, 255, 255)))
                nw = n[-1].get_width()
                if nw > w:
                    w = nw
                tot += h
            new = pygame.Surface((w, tot)).convert_alpha()
            new.fill((0,0,0,0))
            tot = 0
            for i in n:
                new.blit(i, (0, tot*h))
                tot += 1
            return image.Image3D(new, colorize=color)
        else:
            return image.Image3D(self.pygame_font.render(text, True, (255,255,255)),
                                 colorize=color)

class MEFontImage(object):
    """A font image that renders more slowly,
       but allows faster and more efficient changing of text, as well as imbedded image 'smilies'"""
    def __init__(self, fontobj, text="", colorize=(1,1,1,1)):
        """Create the text
           fontobj is the MEFont object that created this text
           text is the text string to render
           colorize is the color (0-1 RGBA) of the text"""
        self.fontobj = fontobj
        self.rotation = (0,0,0)
        self.scale = 1
        self.visible = True

        self._pos = (0,0)
        self._colorize = (1,1,1,1)
        self.glyphs = []
        self._comp_glyphs = []

        self.colorize = colorize
        self.pos = (0,0)
        self.text = text

    def get_text(self):
        return self._text
    def set_text(self, text):
        self._text = text
        self.glyphs = self.make_list_of_glyphs_and_smileys(text)
        n = [[]]
        height = 0
        for i in self.glyphs:
            if i == "\n":
                n[-1] = [n[-1], height]
                height = 0
                n.append([])
            else:
                n[-1].append(i)
                if i.get_height() > height:
                    height = i.get_height()
        n[-1] = [n[-1], height]
        self.glyphs = n
        self.compile_glyphs()
    text = property(get_text, set_text)
    def compile_glyphs(self):
        self._comp_glyphs = []
        downdent = 0
        for line in self.glyphs:
            line, height = line
            indent = 0
            for glyph in line:
                x, y = self.pos
                x += indent
                y += downdent
                glyph.pos = (x, y)
                indent += glyph.get_width()
                self._comp_glyphs.append(glyph)
            downdent += height
    def get_pos(self):
        return self._pos
    def set_pos(self, pos):
        self._pos = pos
        self.compile_glyphs()
    pos = property(get_pos, set_pos)
    def get_col(self):
        return self._colorize
    def set_col(self, col):
        self._colorize = col
        for glyph in self._comp_glyphs:
            glyph.colorize = self._colorize
    colorize = property(get_col, set_col)

    def make_list_of_glyphs_and_smileys(self, text):
        g = []
        skip = 0
        num = 0
        smiley_positions = {}
        for s in self.fontobj.smileys:
            last = 0
            while 1:
                n = text.find(s, last)
                if n >= 0:
                    smiley_positions[n] = s
                    last = n + len(s)
                else:
                    break

        for i in text:
            if skip:
                skip -= 1
            elif num in smiley_positions:
                a = smiley_positions[num]
                g.append(self.fontobj.smileys[a].copy())
                skip = len(a)-1
            elif i == "\n":
                g.append(i)
            else:
                g.append(self.fontobj.glyphs[i].copy())
            num += 1
        return g

    def render(self, camera=None):
        """Render the object
           camera can be None or the camera object used in the scene to render this
               Only here to maintain compatability with other 2d gfx"""
        fo = self.fontobj
        glPushMatrix()
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        try:
            glScalef(self.scale[0], self.scale[1], 1)
        except:
            glScalef(self.scale, self.scale, 1)
        downdent = 0
        for glyph in self._comp_glyphs:
            glyph.render()
        glPopMatrix()

    def copy(self):
        """Copy the text image"""
        n = MEFontImage(self.fontobj, self.text, self.colorize)
        n.pos = self.pos
        n.rotation = self.rotation
        n.scale = self.scale
        n.visible = self.visible
        return n

    def get_width(self):
        """Return the max width of the text - in pixels"""
        width = 0
        for line in self.glyphs:
            line = line[0]
            indent = 0
            for glyph in line:
                indent += glyph.get_width()
            if indent > width:
                width = indent
        return width
                

    def get_height(self):
        """return the max height of the text - in pixels"""
        downdent = 0
        for line in self.glyphs:
            downdent += line[1]
        return downdent

    def get_size(self):
        """Return the size of the text - in pixels"""
        return (self.get_width(), self.get_height())

    def get_rect(self):
        """Return a pygame.Rect of the font image"""
        return pygame.rect.Rect(self.pos, self.get_size())

class MEFont(object):
    """A font the produces text images that render a little slower, but are much faster to change text,
       and support image 'smilies'"""
    def __init__(self, filename=None, fsize=32):
        """Create the font object
           filename can be None or the filename of the font to load (TTF)
           fsize is the size of the font
           smilies is a dict of name:image smilies"""
        view.require_init()
        self.filename = filename
        self.fsize = fsize

        self.smileys = {}

        self.acceptable = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`1234567890-=+_)(*&^%$#@!~[]\\;',./<>?:\"{}| "
        self._load_font()

    def add_smiley(self, name, smiley):
        """Add a smiley to the font.
           smiley must be a pygame.Surface, the path to an image or a pyggel.image.Image.
           Smileys are used in text by writing '[smiley_name]some text'"""
        if isinstance(smiley, image.Image) or\
           isinstance(smiley, image.Animation):
            self.smileys[name] = smiley
        else:
            self.smileys[name] = image.Image(smiley)

    def _load_font(self):
        """Load the font, and create glyphs"""
        self.pygame_font = pygame.font.Font(self.filename, self.fsize)

        L = {}
        for i in self.acceptable:
            L[i] = image.Image(self.pygame_font.render(i, True, (255,255,255)))

        self.glyphs = L

    def make_text_image(self, text="", color=(1,1,1,1)):
        """Return a MEFontImage that holds the text
           text is the text to render
           color = the color of the text (0-1 RGBA)"""
        return MEFontImage(self, text, color)
