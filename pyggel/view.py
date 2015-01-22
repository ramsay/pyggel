"""
pyggel.view
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The view module contains functions and objects used to manipulate initiation, settings,
and changing of the screen window and OpenGL states.
"""

from include import *

class View(object):
    """Store all of the information necessary for handling the window"""
    def __init__(self,
                 screen_size=(640,480),
                 screen_size_2d=(640,480),
                 
                 fullscreen=False,
                 hwrender=True,
                 decorated=True,
                 lighting=True,
                 fog=True,fog_color=(.5,.5,.5,.5),

                 view_angle=45,
                 close_view=0.1,
                 far_view=100.0,

                 clear_color=(0,0,0,0),

                 icon=None,
                 title="PYGGEL App"):

        if screen_size and not screen_size_2d:
            screen_size_2d = screen_size

        self.screen_size = screen_size
        self.screen_size_2d = screen_size_2d

        self.rect = pygame.rect.Rect(0,0,*self.screen_size)
        self.rect2d = pygame.rect.Rect(0,0,*self.screen_size_2d)

        self.fullscreen = fullscreen
        self.hwrender = hwrender
        self.decorated = decorated

        self.lighting = lighting
        self.fog = fog
        self.fog_color = fog_color
        #TODO: fog settings (depth, etc.)

        self.view_angle = view_angle
        self.close_view = close_view
        self.far_view = far_view

        self.clear_color = clear_color

        self.icon = icon
        self.title = title

        self.clips = [(0,0,self.screen_size[0], self.screen_size[1])]

        self.have_init = False

    def get_screen_params(self):
        """Return the pygame window initiation parameters needed."""
        params = OPENGL|DOUBLEBUF
        if self.fullscreen:
            params = params|FULLSCREEN
        if self.hwrender:
            params = params|HWSURFACE
        if not self.decorated:
            params = params|NOFRAME
        return params

    def build(self):

        pygame.init() #make sure this causes no issues, per issue #18

        self.build_screen()
        self.build_icon()
        self.build_title()

        self.build_gl()

        pygame.display

    def build_icon(self):
        if type(self.icon) is type(""):
            pygame.display.set_icon(pygame.image.load(self.icon))
        elif self.icon:
            pygame.display.set_icon(self.icon)

    def build_title(self):
        pygame.display.set_caption(self.title)

    def build_screen(self):
        pygame.display.set_mode(self.screen_size, self.get_screen_params())

    def build_gl(self):
        glEnable(GL_TEXTURE_2D) #do we want to swap to 3D?
        #TODO: I think multitexturing is what we need for this not 3D

        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

        self.build_lighting()

        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glEnable(GL_SCISSOR_TEST)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

        glPointSize(10)

        self.build_background_color()

##        clear_screen()
##        set_fog_color()
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_DENSITY, .35)
        glHint(GL_FOG_HINT, GL_NICEST)
        glFogf(GL_FOG_START, 10.0)
        glFogf(GL_FOG_END, 125.0)
##        set_fog(True)
        glAlphaFunc(GL_GEQUAL, .5)
##        set_background_color()

        self.build_fog()
        self.build_fog_color()
        self.build_background_color()

        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        glFrontFace(GL_CCW)
        glCullFace(GL_BACK)
        glEnable(GL_CULL_FACE)

        self.have_init = True

    def build_lighting(self):
        if self.lighting:
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)

    def toggle_lighting(self):
        self.lighting = not self.lighting
        self.build_lighting()

    def build_background_color(self):
        rgba = self.background_color
        if len(rgba) == 3:
            #convert to rgba
            rgba = (rgba[0], rgba[1], rgba[2], 1)

        glClearColor(*rgba)

    def build_fog(self):
        if self.fog:
            glEnable(GL_FOG)
        else:
            glDisable(GL_FOG)

    def toggle_fog(self):
        self.fog = not self.fog
        self.build_fog()

    def build_fog_color(self):
        glFogfv(GL_FOG_COLOR, self.fog_color)

    def set2d(self):
        """Enable 2d rendering."""
        screen_size = self.screen_size
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glOrtho(0, screen_size[0], screen_size[1], 0, -50, 50)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)

    def set3d(self):
        """Enable 3d rendering."""
        screen_size = self.screen_size
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0,0,*screen_size)
        gluPerspective(self.view_angle, 1.0*screen_size[0]/screen_size[1], self.close_view, self.far_view)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_DEPTH_TEST)

    def clear_screen(self):#scene=None
        """Clear buffers."""
        glDisable(GL_SCISSOR_TEST)
##        if scene and scene.graph.skybox:
##            glClear(GL_DEPTH_BUFFER_BIT)
##        else:
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        glEnable(GL_SCISSOR_TEST)

    def refresh_screen(self):
        """Flip the screen buffer, displaying any changes since the last clear."""
##        if self.cursor and self.cursor_visible and pygame.mouse.get_focused():
##            glPushMatrix()
##            glDisable(GL_LIGHTING)
##            screen.cursor.pos = screen.get_mouse_pos2d()
##            rx = 1.0 * screen.screen_size[0] / screen.screen_size_2d[0]
##            ry = 1.0 * screen.screen_size[1] / screen.screen_size_2d[1]
##            glScalef(rx, ry, 1)
##            if screen.cursor_center:
##                x, y = screen.cursor.pos
##                x -= int(screen.cursor.get_width() / 2)
##                y -= int(screen.cursor.get_height() / 2)
##                screen.cursor.pos = (x, y)
##            screen.cursor.render()
##            if screen.lighting:
##                glEnable(GL_LIGHTING)
##            glPopMatrix()
        #TODO: custom mouse cursors as above, but in the GUI
        pygame.display.flip()

        
