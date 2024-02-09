# -*- mode: python; coding: utf-8; -*-
##---------------------------------------------------------------------------##
# Copyright 2016, LB

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from kivy.core.image import Image as CoreImage
from kivy.uix.image import *
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import *
from kivy.uix.relativelayout import *
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import *
from kivy.graphics import *
from kivy.properties import *

# -----------------------------------------
# Image widget, simplest (and fastest) way

class CardImg(Widget):
    selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(CardImg, self).__init__()

        # we expect source in kwargs.
        #print (kwargs["source"])

        if 'texture' in kwargs:
            texture = kwargs['texture']
        else:
            image = CoreImage(kwargs['source'])
            texture = image.texture

        self.texture = texture
        self.selected = False
        with self.canvas:
            self.color = Color(1.0,1.0,1.0,1.0)
            self.rect = Rectangle(texture=texture)
        self.size = texture.size

    def on_size(self,a,s):
        self.rect.size = s

    def on_pos(self,a,p):
        self.rect.pos = p

    def on_selected(self, instance, value):
        if (value):
            self.color.rgba = [0.5, 0.7, 0.7, 1.0]
        else:
            self.color.rgba = [1.0, 1.0, 1.0, 1.0]

    def move(self, pos):
        self.pos = pos

    def set_selected(self, on):
        self.selected = on

    def get_height(self):
        return self.size[1]

    def get_width(self):
        return self.size[0]

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # So wissen wir im Playground, ob eine Karte getroffen wurde.
            # Wir wollen das dort unterscheiden können. Die Selektion selbst
            # wird dort berechnet. Das ist historisch so.
            return True
        return False

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            return True
        return False

# -----------------------------------------

class ImagesCache(object):
    def __init__(self):
        self.images = {}

    def getCard(self, source):
        if not source in self.images:
            print('cache miss for:',source)
            self.images[source] = CardImg(source=source)

        if source in self.images:
            return self.images[source]
        return None

Cache = ImagesCache()

# -----------------------------------------

# positions-steuerung (muss ausserhalb der klasse sein).
# center_x:
# wir haben 8 kolonnen mit karten, d.h. center-werte sind 1/9 <-> 8/9
# und 8 feste positionen.
# center_y:
# wir haben kartenstacks. Karten in stacks positionieren sich gemaess
# einem startwert + stackposition (und ev. stackgroesse)
# und bei den 8 festen positionen ist es immer derselbe wert.

# Es gibt hier 2 moeglichkeiten:
#
# 1) img widget direkt erzeugen:
#        img2 = Image(source='./card_images/44.gif')
# oder:
# 2) core image erzeugen und texture ins widget uebertragen.
#        cimg2 = image.Image('./card_images/44.gif')
#        img2 = Image()
#        img2.texture = cimg2.texture
# oder:
# 3)
#        img2 = CardImg(source='./card_images/44.gif')
#        img2.pos_hint = {'center_x': .3, 'center_y': .6}

#    def on_touch_down(self,touch):
#        if self.collide_point(*touch.pos):
#            print('touch down event - ',touch.profile,self.source)
#            if self.selected:
#                self.selected = False
#                self.color = [1.0,1.0,1.0,1.0]
#            else:
#                self.selected = True
#                self.color = [0.7,0.7,0.7,1.0]
#            return True
#        return super(CardImg,self).on_touch_down(touch)

#    def on_touch_up(self,touch):
#        if self.collide_point(*touch.pos):
#            print('touch up event - ',touch.profile,self.source)
#            return True
#        return super(CardImg,self).on_touch_up(touch)

#    def on_touch_move(self,touch):
#        if self.collide_point(*touch.pos):
#            print('touch move event - ',touch.profile,self.source)
#            if 'pos' in touch.profile:
#              print(touch.pos)
#              offx = self.dragstart[0] - touch.pos[0]
#              offy = self.dragstart[1] - touch.pos[1]

#              x = touch.pos[0]/self.parent.size[0]
#              y = touch.pos[1]/self.parent.size[1]
#              self.pos_hint['center_x'] = x
#              self.pos_hint['center_y'] = y
#              self.parent.do_layout()

#              print(self.pos_hint)
#              pass
#            return True
#        return super(CardImg,self).on_touch_move(touch)

# -----------------------------------------

from kivy.uix.behaviors import ButtonBehavior
import kivy

class ImageButton(ButtonBehavior, Image):
    def __init__(self,bkgnd=(0,0,0,1),**kw):

        # fit_mode: erst ab version 2.2.1 - android benutzt aber noch 2.2.0!
        allow_stretch = True
        keep_ratio = False
        if kivy.__version__ < "2.2.1":
            # print ('version is than 2.2.0 or lower')
            if "fit_mode" in kw:
                if kw["fit_mode"] == "contain":
                    # fit_mode='contain' emulieren:
                    allow_stretch = True
                    keep_ratio = True
                if kw["fit_mode"] == "fill":
                    # fit_mode='contain' emulieren:
                    allow_stretch = True
                    keep_ratio = False
                if kw["fit_mode"] == "scale_down":
                    # fit_mode='contain' emulieren:
                    allow_stretch = False
                    keep_ratio = False
                if kw["fit_mode"] == "cover":
                    # fit_mode='contain' emulieren:
                    allow_stretch = True
                    keep_ratio = True
                del kw["fit_mode"]

        super(ImageButton, self).__init__(**kw)
        if kivy.__version__ < "2.2.1":
            self.allow_stretch = allow_stretch
            self.keep_ratio = keep_ratio
        self.bind(size=self.update_rect, pos=self.update_rect)
        with self.canvas.before:
            Color(bkgnd[0],bkgnd[1],bkgnd[2],bkgnd[3])
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

# -----------------------------------------
# Label.

from kivy.uix.label import Label

class TitleLabel(Widget):
    def __init__(self,bkgnd=(0,0,0,1),**kw):
        super(TitleLabel, self).__init__(**kw)

        text = 'FREECELL4'
        text = 'FreeCell4'
        text = 'FC4'
        ltext = [c for c in text]
        self.textL = '\n'.join(ltext)
        self.textP = ' '.join(ltext)

        self.label = Label(text=self.textL,halign="center")
        self.label.texture_update()

        self.bind(size=self.update_rect,pos=self.update_rect)
        with self.canvas.before:
            Color(bkgnd[0],bkgnd[1],bkgnd[2],bkgnd[3])
            self.brect = Rectangle(size=self.size, pos=self.pos)
        with self.canvas:
            Color(bkgnd[0],bkgnd[1]+0.33,bkgnd[2],bkgnd[3])
            PushMatrix()
            self.rot = Rotate(angle=0)
            self.rect = Rectangle(texture=self.label.texture)
            PopMatrix()

    def make_contain(self, s, p, texture, rect):
        taspect = texture.size[0]/texture.size[1]
        waspect = s[0]/s[1]
        r = rect
        if waspect < taspect:
            s1 = s[1]*waspect/taspect
            r.size = (s[0], s1)
            r.pos = (p[0], p[1]+(s[1]-s1)/2.0)
        else:
            s0 = s[0]/waspect*taspect
            r.size = (s0, s[1])
            r.pos = (p[0]+(s[0]-s0)/2.0, p[1])

    def update_rect(self, instance, value):
        self.brect.pos = instance.pos
        self.brect.size = instance.size
        if instance.size[0]>instance.size[1]:
            self.label.text = self.textP
            self.label.font_direction = "ltr"
            self.rot.angle=0
        else:
            self.label.text = self.textP
            self.label.font_direction = "ltr"
            self.rot.angle=90
            self.rot.origin=(instance.pos[0]+instance.size[0]/2.0,instance.pos[1]+instance.size[1]/2.0)
        self.label.texture_update()
        self.rect.texture = self.label.texture
        self.make_contain(instance.size,instance.pos,self.label.texture,self.rect)

# -----------------------------------------
# Zeile mit Knoepfen, anstelle von gtk menu

class ButtonLine(BoxLayout):
    def __init__(self,initsize=1.0):
        super(ButtonLine, self).__init__()
        self.orientation = 'horizontal'
        #self.orientation = 'vertical'
        if self.orientation == 'horizontal':
            self.size_hint = (initsize, 0.1)
        else:
            self.size_hint = (0.1, initsize)

class ButtonColm(BoxLayout):
    def __init__(self,initsize=1.0):
        super(ButtonColm, self).__init__()
        #self.orientation = 'horizontal'
        self.orientation = 'vertical'
        if self.orientation == 'horizontal':
            self.size_hint = (initsize, 0.1)
        else:
            self.size_hint = (0.1, initsize)

# -----------------------------------------
# Settings.
'''
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
from kivy.uix.switch import Switch

class SettingsPage(BoxLayout):
    def __init__(self):
        super(SettingsPage, self).__init__()
        self.orientation = 'vertical'
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.header = Button(text='Settings')
        self.header.size_hint = (1.0,0.1)
        self.add_widget(self.header)

        self.btn1 = Switch()
        self.btn1.size_hint = (1.0,0.1)
        self.add_widget(self.btn1)
        self.add_widget(BoxLayout())

        with self.canvas.before:
            Color(0.5, 0.7, 0.5, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def add_setting(self,widget):
        pass
        self.add_widget(widget)

    def addButton(self,widget,size=1.0):
        pass
        self.add_widget(widget)

'''
# -----------------------------------------
# Spielfeld.

class PlayGround(RelativeLayout):
    lastHitPos = ListProperty([])
    longPress = NumericProperty(0)

    def __init__(self):
        super(PlayGround, self).__init__()
        self.lastHitPos = []
        self.statuspanel = StackLayout(orientation='lr-bt')

        self.add_widget(self.statuspanel)
        if kivy.__version__ < "2.2.1":
            self.lock = Image(source="icons/padlock.png",size_hint=(0.12, 0.12))
            self.lock.allow_stretch = True
            self.lock.keep_ratio = True
        else:
            self.lock = Image(source="icons/padlock.png",size_hint=(0.12, 0.12),fit_mode="contain")

    def on_lastHitPos(self, instance, value):
        #print ('lastHitPos',value)
        pass

    def on_touch_down(self, touch):
        if super(PlayGround, self).on_touch_down(touch):
            tx = touch.px - self.pos[0]
            ty = touch.py - self.pos[1]
            self.lastHitPos = (tx, ty)
            return True
        if self.collide_point(*touch.pos):
            # Achtung die Korrdinaten sind screen koordinaten !!
            tx = touch.px - self.pos[0]
            ty = touch.py - self.pos[1]
            self.lastHitPos = (tx, ty)
            # print('touch down event - ',touch.profile,touch.pos,self.lastHitPos)
            return False
        return False

    def on_touch_up(self,touch):
        if super().on_touch_up(touch):
            return True
        if self.collide_point(touch.x,touch.y):
            if (touch.time_end-touch.time_start) > 0.6:
                self.longPress = touch.time_end
                return True
        return False

    def on_longPress(self, instance, timestamp):
        print('longPressed at {time}'.format(time=timestamp))

    def refreshStatus(self):
        self.remove_widget(self.statuspanel)
        self.add_widget(self.statuspanel)

    def setLockIcon(self, on = True):
        if on:
            self.statuspanel.add_widget(self.lock)
            print ('set Lock Icon')
        else:
            self.statuspanel.remove_widget(self.lock)
            print ('remove Lock Icon')
        self.refreshStatus()

    def on_pos(self, instance, value):
        #print ('pos changed',value)
        pass

    def on_size(self, instance, value):
        #print ('size changed',value)
        pass

        #img = CardImg(source='./card_images/43.gif')
        #img2 = CardImg(source='./card_images/44.gif')
        #img2.pos_hint = {'center_x': .3, 'center_y': .6}

        #self.add_widget(img)
        #self.add_widget(img2)

    #def on_pos(self,pos):
    #  pass

# -----------------------------------------
# ActionLine mit action buttions.

class ActionLine(ButtonColm):
    def __init__(self,initsize=1.0):
        self.buttons = []
        self.invertOrder = True
        super(ActionLine, self).__init__(initsize)

    def addButton(self,widget,size=1.0):
        self.buttons.append([widget,size])
        if self.orientation == "vertical":
            widget.size_hint = (1.0,size)
        else:
            widget.size_hint = (size,1.0)
        self.add_widget(widget)

    def on_orientation(self,instance,value):
        # fix orientation of children
        for but in self.buttons:
            if self.orientation == "vertical":
                but[0].orientation = "horizontal"
                but[0].size_hint = (1.0,but[1])
            else:
                but[0].orientation = "vertical"
                but[0].size_hint = (but[1],1.0)

        # invert order of children
        if self.invertOrder:
            self.children.reverse()

# -----------------------------------------
# Program area mit action line

class ProgramArea(ButtonLine):
    def __init__(self,header,table,action,size,initsize=1.0):
        super(ProgramArea, self).__init__(initsize)
        self.table = table
        self.header = [header,size]
        self.action = [action,size]
        self.addHeader()
        self.add_widget(table)
        self.addAction()
        self.actionStack = []
        self.oriEventId = None

    def setOrientation(self):
        if self.orientation == "vertical":
            self.action[0].orientation = "horizontal"
            self.action[0].size_hint = (1.0,self.action[1])
            self.header[0].orientation = "horizontal"
            self.header[0].size_hint = (1.0,self.header[1])
        else:
            self.action[0].orientation = "vertical"
            self.action[0].size_hint = (self.action[1],1.0)
            self.header[0].orientation = "vertical"
            self.header[0].size_hint = (self.header[1],1.0)

    def addHeader(self):
        self.setOrientation()
        self.add_widget(self.header[0])

    def remHeader(self):
        self.remove_widget(self.header[0])

    def addAction(self):
        self.setOrientation()
        self.add_widget(self.action[0])

    def remAction(self):
        self.remove_widget(self.action[0])

    def pushAction(self,action,size):
        self.remAction()
        self.actionStack.append(self.action)
        self.action = [action,size]
        self.addAction()

    def popAction(self):
        if self.actionStack:
            self.remAction()
            self.action = self.actionStack[-1]
            del self.actionStack[-1]
            self.addAction()

    def on_orientation(self,instance,value):
        self.setOrientation()

# -----------------------------------------
# Hauptfenster mit gruenem Hintergrund.

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform

class MainWindow(BoxLayout):
    def __init__(self, game):
        super(MainWindow, self).__init__()
        self.orientation = 'vertical'
        self.bind(size=self._update_rect, pos=self._update_rect)
        self.full = False
        self.game = game
        self.add_widget(self.game)
        self.debug = False

        with self.canvas.before:
            Color(0, 0.7, 0.1, 1)  # gruen wie ein Spieltisch sollte das sein.
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def _update_rect(self, instance, value):
        print('_update_rect',instance.pos)
        print('_update_rect',instance.size)

        self.rect.pos = instance.pos
        self.rect.size = instance.size

        if instance.size[0] > instance.size[1]:
            self.game.orientation = "horizontal"
        else:
            self.game.orientation = "vertical"

    '''
    def _fs(self, d):
        if platform == 'android':
            if self.full:
                Window.borderless = True
                Window.fullscreen = True
            else:
                Window.fullscreen = False
                Window.borderless = False
        else:
            if self.full:
                #Window.borderless = True
                Window.fullscreen = True
            else:
                Window.fullscreen = False
                #Window.borderless = False
                #Window.resizable = True

    '''
    def on_touch_down(self,touch):
        ret = False
        if super(MainWindow, self).on_touch_down(touch):
            return True

        if touch.is_double_tap:
            print('Touch is a double tap !')
            #print(' - interval is',touch.double_tap_time)
            #print(' - distance between previous is',touch.double_tap_distance)
            self.full = not self.full
            #Clock.schedule_once(self._fs, 0.1)
            return True

        if touch.is_triple_tap:
            print('Touch is a triple tap !')
            #print(' - interval is',touch.double_tap_time)
            #print(' - distance between previous is',touch.double_tap_distance)
            '''
            self.debug = not self.debug
            if self.debug:
                text="debug mode enabled"
            else:
                text="debug mode disabled"

            from kivy.app import App
            from toast import Toast
            da = App.get_running_app().freeCell.drawingArea
            label = Toast(text=text)
            label.show(parent=da,duration=3.5,offset=(0.0,0.0))
            '''
            return True

        # debug:
        if self.debug:
            self.parent.angle = (self.parent.angle + 5.0) % 360.0
        if 0:
            from kivy.animation import Animation
            def lin(a):
                return a
            anim = Animation(angle=self.parent.angle-45.0,t=lin,d=3.0)
            anim.start(self.parent)

        print(ret)
        return ret

    def on_touch_up(self,touch):
        if super(MainWindow, self).on_touch_up(touch):
            return True
        '''
        print('Touch up !')
        for c in self.children:
            ret = c.on_touch_up(touch)

        if self.collide_point(touch.x,touch.y):
            print ('on_touch_up Layout')
            if (touch.time_end-touch.time_start) > 0.5:
                print ('on_touch_up Layout - long press')
                return True
        '''
        return False

# -------------------------------------------------------------------------------
# Just for a test: Kann ich ein basisfenster machen, welches die ganze situation
# um 90,180,270 grad drehen kann?

from kivy.uix.scatterlayout import Scatter
from kivy.graphics.transformation import Matrix
import math

class BaseWindow(Scatter):
    angle = NumericProperty(0.0)
    # bringt nichts:
    # angle = BoundedNumericProperty(
    #    0.0,comparator=angequ,errorhandler=angerr,min=-90.0,max=450.0)

    def __init__(self, wmain, **kw):
        super(BaseWindow, self).__init__(**kw)

        # keine interaktion mit user!
        self.do_scale = False
        self.do_rotation = False
        self.do_translation = False

        # locals
        self.relock = False
        self.wmain = wmain
        self.add_widget(wmain)
        self.bind(size=self._update, pos=self._update)
        self.angle = 0.0

        # debug
        # self.angle = 277.0

    def middle(self,pos,size):
        return (pos[0]+size[0]/2.0,pos[1]+size[1]/2.0)

    def collide_point(self, x, y):
        # Maskierung von scatterlayout aushebeln
        return True

    def mytransform(self):
        # wir brauchen einen reetrancy lock sonst himmelfahrt.
        if self.relock: return
        self.relock = True

        print('self.angle =',self.angle)

        # alte transformation zurücksetzen. Basisdimensionen sichern
        self.transform = Matrix()
        p = self.pos
        s = self.size

        # Grössenänderung in -x/y abh. von der Drehung berechnen.
        # Kann eine bel. Funktion sein, jedoch müssen die korrekten Werte
        # bei 0,90,180 und 270 grad durchlaufen werden.
        def mkvd(ang,val):
            ang = 2.0*ang
            ang = (ang-90.0)*math.pi/180.0
            return val*(math.sin(ang)+1.0)/2.0

        ds = (s[1]-s[0])
        vds = mkvd(self.angle,ds)

        # Grösse auf das Hauptfenster anwenden.
        ws = (s[0]+vds,s[1]-vds)
        self.wmain.size = ws
        # print('vds =',vds,' ws =',self.wmain.size)

        # Transformation der Grösse und Position ins Zentrum
        d = (s[0]-ws[0],s[1]-ws[1])
        t = Matrix().translate(p[0]+(d[0]/2.0),p[1]+(d[1]/2.0),0)

        # Drehung ums Zentrum
        a = self.middle(p,s)
        t1 = Matrix().translate(a[0],a[1],0)
        t2 = t1.inverse()
        r = Matrix().rotate(self.angle*math.pi/180.0,0,0,1)

        # alles zusammenstellen
        m = Matrix()
        m = m.multiply(t1)
        m = m.multiply(r)
        m = m.multiply(t2)
        m = m.multiply(t)

        # koordinaten inspizieren. also alle ecken ansehen.
        # und scalierungsmatrix aufsetzen.
        p0 = m.transform_point(p[0],p[1],0)
        p1 = m.transform_point(p[0]+ws[0],p[1],0)
        p2 = m.transform_point(p[0]+ws[0],p[1]+ws[1],0)
        p3 = m.transform_point(p[0],p[1]+ws[1],0)
        maxx = max(p0[0],p1[0],p2[0],p3[0])
        minx = min(p0[0],p1[0],p2[0],p3[0])
        maxy = max(p0[1],p1[1],p2[1],p3[1])
        miny = min(p0[1],p1[1],p2[1],p3[1])
        sx = s[0]/(maxx-minx)
        sy = s[1]/(maxy-miny)
        ss = min(sx,sy)
        # print ('sx,sy,ss=',sx,sy,ss)

        # transformation mit skalierung neu aufsetzen
        m = Matrix()
        m = m.multiply(t1)
        m.scale(ss,ss,1)
        m = m.multiply(r)
        m = m.multiply(t2)
        m = m.multiply(t)

        # anwenden
        self.apply_transform(m)

        # print('self.size =',self.size)
        # print('self.pos  =',self.pos)
        # print('self.wmain.size =',self.wmain.size)
        # print('self.wmain.pos  =',self.wmain.pos)

        # remove lock
        self.relock = False

    def on_angle(self, instance, value):
        print('on_angle')
        '''
        if value >= 360.0:
            self.angle = value - 360.0
        if value < 0.0:
            self.angle = value + 360.0
        '''
        self.mytransform()

    def _update(self, instance, value):
        print('_update')
        self.mytransform()

# ------------------------------------------------------------------------------
