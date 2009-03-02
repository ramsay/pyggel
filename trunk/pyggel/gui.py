"""
pyggle.gui
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The gui module contains classes to create and use a simple Graphical User Interface.
"""

from include import *
import image, event, view, font
import time


class App(object):
    """A simple Application class, to hold and control all widgets."""
    def __init__(self, event_handler):
        """Create the App.
           event_handler must be the event.Handler object that the gui will use to get events,
           and each event handler may only have on App attached to it."""
        self.event_handler = event_handler
        self.event_handler.gui = self

        self.widgets = []

        self.dispatch = event.Dispatcher()
        self.dispatch.bind("new-widget", self.new_widget)

        self.next_pos = 0, 0, 0 #left, top, bottom if shift

        self.mefont = font.MEFont()
        self.regfont = font.Font()

        self.visible = True

    def get_mouse_pos(self):
        """Return mouse pos based on App position -always (0,0)"""
        return view.screen.get_mouse_pos()

    def new_widget(self, widget):
        """Add a new widget to the App."""
        if not widget in self.widgets:
            self.widgets.insert(0, widget)

    def handle_mousedown(self, button, name):
        """Callback for mouse click events from the event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_mousedown(button, name):
                    return True
        return False
    def handle_mouseup(self, button, name):
        """Callback for mouse release events from the event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_mouseup(button, name):
                    return True
        return False
    def handle_mousehold(self, button, name):
        """Callback for mouse hold events from the event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_mousehold(button, name):
                    return True
        return False

    def handle_uncaught_event(self, event):
        """Callback for uncaught_event events from event_handler."""
        if event.type == MOUSEMOTION:
            if "left" in self.event_handler.mouse.active:
                return self.handle_drag(event)
        else:
            for i in self.widgets:
                if i.visible:
                    if i.handle_uncaught_event(event):
                        return True
        return False

    def handle_drag(self, event):
        """Callback for mouse drag events."""
        for i in self.widgets:
            if i.handle_drag(event):
                return True
        return False

    def handle_keydown(self, key, string):
        """Callback for key press events from event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_keydown(key, string):
                    return True
        return False

    def handle_keyup(self, key, string):
        """Callback for key release events from event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_keyup(key, string):
                    return True
        return False

    def handle_keyhold(self, key, string):
        """Callback for key hold events from event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_keyhold(key, string):
                    return True
        return False

    def next_widget(self):
        """Cycle widgets so next widget is top one."""
        self.widgets.append(self.widgets.pop(0))
        while not self.widgets[0].visible:
            self.widgets.append(self.widgets.pop(0))

    def set_top_widget(self, widg):
        """Moves widget 'widg' to top position."""
        if widg in self.widgets:
            self.widgets.remove(widg)
        self.widgets.insert(0, widg)

    def render(self, camera=None):
        """Renders all widgets, camera can be None or the camera object used to render the scene."""
        self.widgets.reverse()
        for i in self.widgets:
            if i.visible: i.render()
        self.widgets.reverse()

    def get_next_position(self, size):
        """Get next 'pad' position, ie, the next open area that this widget can be rendered to without overlapping other widgets."""
        x, y, nh = self.next_pos
        w, h = size
        if x + w > view.screen.screen_size_2d[0]:
            x = 0
            y = nh + 1
        return x, y

    def set_next_position(self, pos, size):
        """Change the next position for the next widget."""
        x, y = pos[0] + size[0] + 1, pos[1]
        if y + size[1] > self.next_pos[2]:
            nh = y + size[1]
        else:
            nh = self.next_pos[2]

        self.next_pos = x, y, nh

    def newline(self, height=0):
        """Force the next widget to be on a new line (if pos is not explicitly set) - unless it is already there..."""
        nh = self.next_pos[2]+height
        self.next_pos = (0, nh+1, nh)


class Widget(object):
    """Base class all gui elements should inherit from."""
    def __init__(self, app):
        """Create the Widget.
           app must be the App object that this widget is part of."""
        self.app = app
        self.dispatch = event.Dispatcher()

        self.visible = True

        self.app.dispatch.fire("new-widget", self)

    def handle_mousedown(self, button, name):
        """Handle a mouse down event from the App."""
        return False
    def handle_mouseup(self, button, name):
        """Handle a mouse release event from the App."""
        return False
    def handle_mousehold(self, button, name):
        """Handle a mouse hold event from the App."""
        return False

    def handle_drag(self, event):
        """Handle a mouse drag event from the App."""
        return False

    def handle_uncaught_event(self, event):
        """Handle an uncaught event from the App."""
        return False

    def handle_keydown(self, key, string):
        """Handle a key press event from the App."""
        return False
    def handle_keyup(self, key, string):
        """Handle a key release event from the App."""
        return False
    def handle_keyhold(self, key, string):
        """Handle a key hold event from the App."""
        return False

    def render(self, offset=(0,0)):
        """Render the widget."""
        pass

class Label(Widget):
    """A simple text label widget."""
    def __init__(self, app, text, pos=None):
        """Create the Label.
           app must be the App object that this widget is a part of
           text must be the text string to render (supports smileys, via the app.mefont object)
           pos must be None or the 2d (x,y) position of the label
               if None, the gui will automaticall assign a position that it tries to fit on screen
               without overlapping other widgets"""
        Widget.__init__(self, app)

        self.text = text
        self.text_image = self.app.mefont.make_text_image(text)

        if pos == None:
            self.text_image.pos = self.app.get_next_position(self.text_image.get_size())
            self.app.set_next_position(self.text_image.pos, self.text_image.get_size())
        else:
            self.text_image.pos = pos

        self.pos = self.text_image.pos

    def render(self, offset=(0,0)):
        """Render the Label."""
        x, y = self.pos
        x += offset[0]
        y += offset[1]
        self.text_image.pos = (x, y)
        self.text_image.render()
        self.text_image.pos = self.pos

class Button(Label):
    """A simple button widget."""
    def __init__(self, app, text, pos=None, callbacks=[]):
        """Create the Button.
           app must be the App object that this widget is a part of
           text must be the text string to render (supports smileys, via the app.mefont object)
           pos must be None or the 2d (x,y) position of the button
               if None, the gui will automaticall assign a position that it tries to fit on screen
               without overlapping other widgets
           callbacks must be a list/tuple of functions/methods to call when the button is clicked"""
        Label.__init__(self, app, text, pos)
        self.text_image_click = self.text_image.copy()
        self.text_image_click.colorize=(1,0,0,1)

        self.use_image = self.text_image

        for i in callbacks:
            self.dispatch.bind("click", i)

        self._mdown = False

    def handle_mousedown(self, button, name):
        """Handle a mouse down event from the App."""
        if name == "left":
            if self.use_image.get_rect().collidepoint(self.app.get_mouse_pos()):
                self.use_image = self.text_image_click
                self._mdown = True
                return True

    def handle_mousehold(self, button, name):
        """Handle a mouse hold event from the App."""
        if name == "left":
            if self._mdown and self.use_image.get_rect().collidepoint(self.app.get_mouse_pos()):
                self.use_image = self.text_image_click
                return True
            self.use_image = self.text_image

    def handle_mouseup(self, button, name):
        """Handle a mouse release (possible click) event from the App.
           If clicked, will execute all callbacks (if any) supplied."""
        if name == "left":
            if self._mdown and self.use_image.get_rect().collidepoint(self.app.get_mouse_pos()):
                self._mdown = False
                self.dispatch.fire("click")
                self.use_image = self.text_image
                return True
            self._mdown = False

    def render(self, offset=(0,0)):
        """Render the button."""
        x, y = self.pos
        x += offset[0]
        y += offset[1]
        self.use_image.pos = (x, y)
        self.use_image.render()
        self.use_image.pos = self.pos

class Checkbox(Widget):
    """Basic checkbox selection widget."""
    def __init__(self, app, pos=None):
        """Create the Checkbox.
           app must be the App object that this widget is a part of
           pos must be None or the 2d (x,y) position of the button
               if None, the gui will automaticall assign a position that it tries to fit on screen
               without overlapping other widgets"""
        Widget.__init__(self, app)

        self.off = self.app.regfont.make_text_image("O")
        self.on = self.app.regfont.make_text_image("X")

        if pos == None:
            self.off.pos = self.app.get_next_position(self.off.get_size())
            self.app.set_next_position(self.off.pos, self.off.get_size())
            self.on.pos = self.off.pos
        else:
            self.off.pos = pos
            self.on.pos = pos
        self.pos = self.off.pos

        self.state = 0
        self.clicked = False

    def handle_mousedown(self, button, name):
        """Handle a mouse press event from the App."""
        if name == "left":
            if self.off.get_rect().collidepoint(self.app.get_mouse_pos()):
                self.clicked = True
                return True
    def handle_mouseup(self, button, name):
        """Handle a mouse release event from the App."""
        if name == "left":
            if self.clicked and self.off.get_rect().collidepoint(self.app.get_mouse_pos()):
                self.clicked = False
                self.state = not self.state
                if self.state:
                    self.dispatch.fire("check", self)
                else:
                    self.dispatch.fire("uncheck", self)
                return True
            self.clicked = False

    def render(self, offset=(0,0)):
        """Render the checkbox."""
        x, y = self.pos
        x += offset[0]
        y += offset[1]
        self.off.pos = (x, y)
        self.off.render()
        self.off.pos = self.pos
        if self.state:
            self.on.pos = (x, y)
            self.on.render()
            self.on.pos = self.pos

class Radio(Widget):
    """Basic Radio widget."""
    def __init__(self, app, options=[], pos=None):
        """Create the Radio.
           app must be the App object that this widget is a part of
           options must be a list of strings for each option this radio can have
           pos must be None or the 2d (x,y) position of the button
               if None, the gui will automaticall assign a position that it tries to fit on screen
               without overlapping other widgets"""
        Widget.__init__(self, app)

        self.option = 0
        self.checks = []
        self.labels = []
        height = 0
        width = 0
        for i in options:
            x = Checkbox(app, (0,height))
            x.dispatch.bind("check", self.handle_check)
            self.checks.append(x)
            n = Label(app, i, (int(x.off.get_width()*1.25), height))
            self.labels.append(n)
            height += max([x.off.get_height(), n.text_image.get_height()])
            w = x.off.get_width() + n.text_image.get_width() + 1
            if w > width:
                width = w

        if pos == None:
            x, y = self.app.get_next_position((width, height))
            self.app.set_next_position((x,y), (width, height))
        else:
            x, y = pos
        self.pos = (x, y)
        for i in self.checks:
            a, b = i.pos
            a += x
            b += y
            i.pos = (a, b)
        for i in self.labels:
            a, b = i.text_image.pos
            a += x
            b += y
            i.pos = (a, b)

    def handle_mousedown(self, button, name):
        """Handle a mouse press event from the App."""
        for i in self.checks:
            x = i.handle_mousedown(button, name)
            if x:
                return True
    def handle_mouseup(self, button, name):
        """Handle a mouse release event from the App."""
        for i in self.checks:
            x = i.handle_mouseup(button, name)
            if x:
                return True
    def handle_check(self, check):
        """Handle a check click from one of the options."""
        for i in self.checks:
            if not i is check:
                i.state = 0
        self.option = self.checks.index(check)

    def render(self, offset=(0,0)):
        """Render the radio."""
        for i in self.checks + self.labels:
            i.render(offset)

class MultiChoiceRadio(Radio):
    """Basic Multiple choice radio widget."""
    def __init__(self, app, options=[], pos=None):
        """Create the MultiChoiceRadio.
           app must be the App object that this widget is a part of
           options must be a list of strings for each option this radio can have
           pos must be None or the 2d (x,y) position of the button
               if None, the gui will automaticall assign a position that it tries to fit on screen
               without overlapping other widgets"""
        Radio.__init__(self, app, options, pos)

        self.states = []
        for i in self.checks:
            self.states.append(False)
            i.dispatch.bind("uncheck", self.handle_uncheck)

    def handle_check(self, check):
        """Handle a check click from one of the options."""
        self.states[self.checks.index(check)] = True

    def handle_uncheck(self, check):
        """Handle a check unclick from one of the options."""
        self.states[self.checks.index(check)] = False

class Input(Label):
    """Basic text input widget."""
    def __init__(self, app, start_text="", width=100, pos=None):
        """Create the Input widget.
           app must be the App object that this widget is a part of
           start_text must be the string of text the input box starts with
           width must be the max width (in pixels) if the box
           pos must be None or the 2d (x,y) position of the button
               if None, the gui will automaticall assign a position that it tries to fit on screen
               without overlapping other widgets"""
        Label.__init__(self, app, start_text, pos)

        self.width = width
        self.height = self.app.mefont.pygame_font.get_height()

        if pos == None:
            self.app.set_next_position(self.pos, (self.width, self.height))

        self.working = len(self.text)
        self.working_image = image.Animation([[self.app.regfont.make_text_image("|"), .5],
                                              [self.app.regfont.make_text_image("|",color=(0,0,0,0)), .5]])
        self.xwidth = self.width - self.working_image.get_width()

        self.key_hold_lengths = {}
        self.key_hold_length = 100 #milliseconds...

        self.active = False
        self._mdown = False

    def get_clip(self):
        """Return the "clip" of view - to limit rendering outside of the box."""
        rx = 1.0 * view.screen.screen_size[0] / view.screen.screen_size_2d[0]
        ry = 1.0 * view.screen.screen_size[1] / view.screen.screen_size_2d[1]

        x, y = self.pos
        w = self.width
        h = self.height

        return int(x*rx), view.screen.screen_size[1]-int(y*ry)-int(h*ry), int(w*rx), int(h*ry)

    def calc_working_pos(self):
        """Calculate the position of the text cursor - ie, where in the text are we typing... and the text offset."""
        if self.text and self.working > 0:
            width = 0
            for i in self.text_image.glyphs[0][0][0:self.working]:
                width += i.get_width()
            x, y = width, self.pos[1]
            if self.text_image.get_width() > self.xwidth:
                x = self.pos[0] - (self.text_image.get_width() - self.xwidth)+x

            wx, wy = x-int(self.working_image.get_width()/2), y

            if self.text_image.get_width() > self.xwidth:
                x, y = self.text_image.pos
                x = self.pos[0] - (self.text_image.get_width() - self.xwidth)
                if self.working_image.pos[0] < 0:
                    x -= self.working_image.pos[0]
                    self.working_image.pos = 5, self.working_image.pos[1]
                px, py = x, y
            else:
                px, py = self.pos

            n = 0
            while wx < self.pos[0]:
                w = self.text_image.glyphs[0][0][n].get_width()
                wx += w
                px += w
                n += 1
            return (wx, wy), (px, py)
        else:
            return (self.pos[0]-int(self.working_image.get_width()/2), self.pos[1]), self.pos

    def move_working(self, x):
        """Move the working position of the cursor."""
        self.working_image.reset()
        self.working += x
        if self.working < 0:
            self.working = 0
        if self.working > len(self.text):
            self.working = len(self.text)

    def can_use(self, key, string):
        """Return whether or not this kind of event is captured by the widget."""
        if string and string in self.app.mefont.acceptable:
            return True
        if key in (K_LEFT, K_RIGHT, K_END, K_HOME, K_DELETE,
                   K_BACKSPACE, K_RETURN):
            return True
        return False

    def submit_text(self):
        if self.text:
            self.dispatch.fire("submit", self.text)
            self.text = ""
            self.text_image.text = ""
            self.working = 0

    def handle_keydown(self, key, string):
        """Handle a key click event from the App."""
        if not self.can_use(key, string):
            return False
        if self.active:
            if string and string in self.app.mefont.acceptable:
                self.text = self.text[0:self.working] + string + self.text[self.working::]
                self.text_image.text = self.text
                self.working += 1
            if key == K_LEFT:
                self.move_working(-1)
            if key == K_RIGHT:
                self.move_working(1)
            if key == K_DELETE:
                self.text = self.text[0:self.working] + self.text[self.working+1::]
                self.text_image.text = self.text
            if key == K_BACKSPACE:
                if self.working:
                    self.text = self.text[0:self.working-1] + self.text[self.working::]
                    self.move_working(-1)
                    self.text_image.text = self.text
            if key == K_HOME:
                self.working = 0
            if key == K_END:
                self.working = len(self.text)
            if key == K_RETURN:
                self.submit_text()
            return True
        return False

    def handle_keyhold(self, key, string):
        """Handle a key hold event from the App."""
        if not self.can_use(key, string):
            return False
        if self.active:
            if key in self.key_hold_lengths:
                if time.time() - self.key_hold_lengths[key] >= self.key_hold_length * 0.001:
                    self.handle_keydown(key, string)
                    self.key_hold_lengths[key] = time.time()
            else:
                self.key_hold_lengths[key] = time.time()
            return True
        return False


    def handle_keyup(self, key, string):
        """Handle a key release event from the App."""
        if not self.can_use(key, string):
            return False
        if self.active:
            if key in self.key_hold_lengths:
                del self.key_hold_lengths[key]
            return True
        return False

    def handle_mousedown(self, button, name):
        """Handle mouse down event from the App."""
        if name == "left":
            r = pygame.Rect(self.pos, (self.width, self.height))
            if r.collidepoint(self.app.get_mouse_pos()):
                self._mdown = True
                return True
            else:
                self.active = False

    def handle_mouseup(self, button, name):
        """Handle mouse release event from the App."""
        if name == "left":
            m = self._mdown
            self._mdown = False
            r = pygame.Rect(self.pos, (self.width, self.height))
            if m and r.collidepoint(self.app.get_mouse_pos()):
                self.active = True
                return True

    def render(self, offset=(0,0)):
        """Render the Input widget."""
        wpos, tpos = self.calc_working_pos()
        tpx, tpy = tpos
        tpx += offset[0]
        tpy += offset[1]
        self.text_image.pos = (tpx, tpy)
        view.screen.push_clip(self.get_clip())
        Label.render(self)
        self.text_image.pos = tpos
        if self.active:
            wpx, wpy = wpos
            wpx += offset[0]
            wpy += offset[1]
            self.working_image.pos = (wpx, wpy)
            self.working_image.render()
            self.working_image.pos = wpos
        view.screen.pop_clip()

class Frame(App, Widget):
    """A Simple Frame widget. A Frame is basically an App inside an App - allowing you to position other widgets inside it.
       The only difference is that a Frame is also a widget - it has a pos and size attribute. Frames are nestable."""
    def __init__(self, app, pos=None, size=(10,10)):
        """Create the Frame.
           app must be the App object that this widget is a part of
           pos must be None (to position inside the parent app) or x,y pos of widget
           size must be the pixel size of the Frame"""
        Widget.__init__(self, app)

        if pos == None:
            pos = self.app.get_next_position(size)
            self.app.set_next_position(pos, size)

        self.widgets = []

        self.dispatch.bind("new-widget", self.new_widget)

        self.pos = pos
        self.size = size

        self.next_pos = 0, 0, 0 #left, top, bottom if shift

        self.mefont = self.app.mefont
        self.regfont = self.app.regfont

    def get_mouse_pos(self):
        """Return mouse pos based on Frame's position."""
        x, y = self.app.get_mouse_pos()
        x -= self.pos[0]
        y -= self.pos[1]
        return (x, y)

    def get_clip(self):
        """Return the "clip" of view - to limit rendering outside of the box."""
        rx = 1.0 * view.screen.screen_size[0] / view.screen.screen_size_2d[0]
        ry = 1.0 * view.screen.screen_size[1] / view.screen.screen_size_2d[1]

        x, y = self.pos
        w, h = self.size

        return int(x*rx), view.screen.screen_size[1]-int(y*ry)-int(h*ry), int(w*rx), int(h*ry)

    def handle_uncaught_event(self, event):
        """Callback for uncaught_event events from App."""
        for i in self.widgets:
            if i.visible:
                if i.handle_uncaught_event(event):
                    return True
        return False

    def render(self, offset=(0,0)):
        """Renders all widgets in the Frame."""
        self.widgets.reverse()
        x, y = self.pos
        x += offset[0]
        y += offset[1]
        view.screen.push_clip(self.get_clip())
        for i in self.widgets:
            if i.visible: i.render((x, y))
        view.screen.pop_clip()
        self.widgets.reverse()

    def get_next_position(self, size):
        """Get next 'pad' position, ie, the next open area that this widget can be rendered to without overlapping other widgets."""
        x, y, nh = self.next_pos
        w, h = size
        if x + w > self.size[0]:
            x = 0
            y = nh + 1
        return x, y