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

from kivy.uix.image import *
from kivy.uix.boxlayout import *
from kivy.uix.relativelayout import *
from kivy.uix.floatlayout import *
from kivy.graphics import *
from kivy.properties import *

# -------------------------------------
# Image widget, anstelle von gtk pixbuf


class CardImg(Image):
    selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(CardImg, self).__init__(**kwargs)
        self.allow_stretch = 1
        self.keep_ratio = 0
        self.size = self.texture.size
        self.size_hint = (1.0 / 9.0, 1.0 / 4.0)
        self.selected = False

    def on_selected(self, instance, value):
        if (value):
            self.color = [0.7, 0.7, 0.7, 1.0]
        else:
            self.color = [1.0, 1.0, 1.0, 1.0]
        self.canvas.ask_update()

    def move(self, pos):
        self.pos = pos

    def set_selected(self, on):
        self.selected = on

    def get_height(self):
        return self.size[1]

    def get_width(self):
        return self.size[0]


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
# Actions Managment


class Action:
    def __init__(self, start, trigger):
        self.start = start
        self.trigger = trigger

    def endCallback(self):
        #print ('trigger')
        self.trigger
        pass

    def run(self):
        #print ('start')
        self.start


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
# Spielfeld.


class PlayGround(RelativeLayout):
    lastHitPos = ListProperty([])

    def __init__(self):
        super(PlayGround, self).__init__()
        self.lastHitPos = []

    def on_lastHitPos(self, instance, value):
        #print ('lastHitPos',value)
        pass

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Achtung die Korrdinaten sind screen koordinaten !!
            tx = touch.px - self.pos[0]
            ty = touch.py - self.pos[1]
            #self.lastHitPos = touch.pos
            self.lastHitPos = (tx, ty)
            # print('touch down event - ',touch.profile,touch.pos,self.lastHitPos)

        return super(PlayGround, self).on_touch_down(touch)

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
# Hauptfenster mit gruenem Hintergrund.

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform

class MainWindow(BoxLayout):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.orientation = 'vertical'
        self.bind(size=self._update_rect, pos=self._update_rect)
        # (see p4a issue 1724):
        self.bind(size=Clock.schedule_once(self._ur, 0.1))
        self.full = False

        with self.canvas.before:
            Color(0, 0.7, 0.1, 1)  # gruen wie ein Spieltisch sollte das sein.
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def _ur(self, d):
        self._update_rect(self, 0)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

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

    def on_touch_down(self,touch):
        ret = False
        if touch.is_double_tap:
          print('Touch is a double tap !')
          print(' - interval is',touch.double_tap_time)
          print(' - distance between previous is',touch.double_tap_distance)
          self.full = not self.full
          Clock.schedule_once(self._fs, 0.1)
        else:
          for c in self.children:
            ret = c.on_touch_down(touch)
            if ret:
                break
        return ret
    '''



