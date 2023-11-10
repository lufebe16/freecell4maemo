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
from kivy.uix.stacklayout import StackLayout
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
            self.color = [0.5, 0.7, 0.7, 1.0]
            #self.color = [1.0, 0.3, 0.9, 1.0]
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

from kivy.uix.behaviors import ButtonBehavior
import kivy

class ImageButton(ButtonBehavior, Image):
    def __init__(self,bkgnd=(0,0,0,1),**kw):

        # fit_mode: erst ab version 2.2.1 - android benutzt aber noch 2.2.0!
        if kivy.__version__ < "2.2.1":
            # print ('version is than 2.2.0 or lower')
            if "fit_mode" in kw:
                if kw["fit_mode"] == "contain":
                    # fit_mode='contain' emulieren:
                    self.allow_stretch = True
                    self.keep_ratio = True
                if kw["fit_mode"] == "fill":
                    # fit_mode='contain' emulieren:
                    self.allow_stretch = True
                    self.keep_ratio = False
                del kw["fit_mode"]

        super(ImageButton, self).__init__(**kw)
        self.bind(size=self.update_rect, pos=self.update_rect)
        with self.canvas.before:
            Color(bkgnd[0],bkgnd[1],bkgnd[2],bkgnd[3])
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_press(self):
        print ('on_press')
        #print ('on_press',widget)
        pass

    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        pass

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        pass


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
            return True
        if self.collide_point(*touch.pos):
            # Achtung die Korrdinaten sind screen koordinaten !!
            tx = touch.px - self.pos[0]
            ty = touch.py - self.pos[1]
            #self.lastHitPos = touch.pos
            self.lastHitPos = (tx, ty)
            # print('touch down event - ',touch.profile,touch.pos,self.lastHitPos)
            return True
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
        print ('on_orientation',instance,value)
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
        # (see p4a issue 1724):
        self.bind(size=Clock.schedule_once(self._ur, 0.1))
        self.full = False
        self.game = game
        self.add_widget(self.game)

        with self.canvas.before:
            Color(0, 0.7, 0.1, 1)  # gruen wie ein Spieltisch sollte das sein.
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def _ur(self, d):
        self._update_rect(self, 0)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        if instance.size[0] > instance.size[1]:
            self.game.orientation = "horizontal"
        else:
            self.game.orientation = "vertical"
        #print('_update_rect',instance.size)

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
        if touch.is_double_tap:
            print('Touch is a double tap !')
            print(' - interval is',touch.double_tap_time)
            print(' - distance between previous is',touch.double_tap_distance)
            self.full = not self.full
            #Clock.schedule_once(self._fs, 0.1)
        else:
            for c in self.children:
                ret = c.on_touch_down(touch)
                if ret:
                    break
            return ret

    '''
    def on_touch_up(self,touch):
        pass
        print('Touch up !')
        for c in self.children:
            ret = c.on_touch_up(touch)

        if self.collide_point(touch.x,touch.y):
            print ('on_touch_up Layout')
            if (touch.time_end-touch.time_start) > 0.5:
                print ('on_touch_up Layout - long press')
                return True

        return ret
    '''
