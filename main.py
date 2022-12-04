#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
##---------------------------------------------------------------------------##

# Freecell4Maemo, Copyright 2008, Roy Wood
#                 Copyright 2010, Justin Quek
# Kivy port,			Copyright 2016, Lukas Beck

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

# To Do:
# - on-screen toggle for smart move mode
# - intelligent use of empty stacks when moving columns
# - smart-move a column?
"""	
Freecell4Maemo is an implementation of the classic Freecell cardgame for the Nokia "Maemo" platform.
	
The code is pretty small, and I have tried to comment it effectively throughout, so you should have be able to
figure things out pretty easily.

Some of the more significant pieces are as follows:
	
class Rect - a rectangle; important members are top, left, width, height
class Card - a playing card; important members are cardnum(0-51), screen location/size, pixbuf
class CardStack - a stack of Card objects; important members are screen location/size, cards, "empty stack" pixbuf, stack suit
class Freecell - the main class for the app; uses the other classes as needed


Some significant points about the main "Freecell" class are:

- the __init__ method creates all the basic object members, loads all the card images, creates the GUI
- the GUI is a single window containing a GTK DrawingArea
- all drawing is done in an offscreen PixMap
- the offscreen PixMap is blitted to the DrawingArea in response to expose events
- the offscreen PixMap is created in the configure event handler, not __init__
- all GraphicContext objects are created in the configure event handler
- the configure handler also triggers a call to set the rects of the CardStacks (important for switching between fullscreen and smallscreen)
- the real game logic is in the button_press_event handler (and yes, it gets a little messy)

"""

ABOUT_TEXT = """
Freecell4Maemo:
           Copyright 2008, Roy Wood
           Copyright 2010, Justin Quek
Adapted to Android (Kivy):
           Copyright 2016-2022, Lukas Beck

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version (see <http://www.gnu.org/licenses/>).
"""

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from cardimg import *
from taskm import *
from androidperms import requestStoragePerm
from androidperms import getStoragePerm
from kivy.clock import Clock
from kivy.base import stopTouchApp
from kivy.animation import Animation
from kivy.uix.actionbar import *
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import platform

import time
import random
import logging
import math
import bisect

import json
import os
import sys

# Size of the inset border for the window
FULLSCREEN_BORDER_WIDTH = 10
SMALLSCREEN_BORDER_WIDTH = 2

# Border between upper/lower sets of cards
VERT_SEPARATOR_WIDTH = 10

# Suit IDs
CLUBS = 0
DIAMONDS = 1
SPADES = 2
HEARTS = 3

SUITNAMES = ["Clubs", "Diamonds", "Spades", "Hearts"]
CARDNAMES = [
    "Ass", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Knight", "Queen", "King"
]

SUITSYM = ["C", "D", "S", "H"]
CARDSYM = ["A", "2", "3", "4", "5", "6", "7", "8", "9","T", "J", "Q", "K"]

# Suit colours
BLACK = 0
RED = 1

# Number of cards per suit
CARDS_PER_SUIT = 13

# Card pixbufs 0-51 are the regular cards,
NUMCARDS = 52

# Cards 52-55 are the suit-back cards (aces in top right of screen)
CLUBS_BACK = 52
DIAMONDS_BACK = 53
SPADES_BACK = 54
HEARTS_BACK = 55

# Card 56 is the the blank-back card (used to draw stacks with no cards)
BLANK_BACK = 56

# Card 57 is the fancy-back card (not currently used)
FANCY_BACK = 57

# Total number of card images
TOTALNUMCARDS = FANCY_BACK

# Number of card columns
NUMCOLUMNS = 8

# Number of "free cells"
NUMFREECELLS = 4

# Number of ace cards
NUMACES = 4

# Types of cards
FREECELL_TYPE = 0
ACE_TYPE = 1
REGULAR_TYPE = 2

# Folder containing the card images
CARDFOLDER = "./card_images"

# Response constants for the "Move card or column" dialog (OK/CANCEL are the constants that the hildon.Note dialog returns)

#TOPORT?
MOVE_CARD_ID = 'single'

# MOVE_COLUMN_ID = gtk.RESPONSE_OK

#=============================================================================

from factorial import fact, factorial
'''
class fact(object):
    cache = {}

    def calc(self,n):
        if n in self.cache.keys():
            #print ("cache hit:",n)
            return self.cache[n]

        if (n==1 or n==0):
            self.cache[n] = 1
        else:
            self.cache[n] = n * self.calc(n - 1)
        return self.cache[n]

        # return 1 if (n==1 or n==0) else n * self.calc(n - 1);
        # 52! =
        # 80658175170943878571660636856403766975289505440883277824000000000000
        # d.h. ein eindeutiger Identifikator wäre (als Zahl dargestellt) so lang.

    def __call__(self,n):
        return self.calc(n)

factorial = fact()
'''
#=============================================================================

def cardnum_to_sym(cn):
    if (cn < NUMCARDS):
        cc = cn % CARDS_PER_SUIT
        c = CARDSYM[cc]
        cs = cn // CARDS_PER_SUIT
        s = SUITSYM[cs]
        return c+s
    return ""

def cardsym_to_num(ss):
    c = ss[0]
    s = ss[1]
    #print (s,c)
    for cs in range(len(SUITSYM)):
        if s == SUITSYM[cs]:
            break
    for cc in range(len(CARDSYM)):
        if c == CARDSYM[cc]:
            break
    return cs*CARDS_PER_SUIT + cc


#=============================================================================
# Darstellung mit Gross und Klein Alpha (52-er system).

def deal_to_alpha(deal):
    da = [i+65 if (i<26) else i+97-26 for i in deal]
    return bytes(da)

def alpha_to_deal(alpha):
    alphai = list(alpha)
    de = [i-65 if (i<97) else i-97+26 for i in alphai]
    return de

#=============================================================================
# Lehmer Code & Rothe Diagramm

from lehmer import Lehmer

#=============================================================================
# levensthein

# from levensthein import levensthein

#=============================================================================

# Es gibt ein python module permutation, das aktuell unterhalten wird und
# all diese Funktionalität unterstützt. Jedoch vom interface her ungeeignet.
# https://permutation.readthedocs.io/en/stable/

#=============================================================================

def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode('utf-8') # uses 'utf-8' for encoding
    else:
        value = bytes_or_str
    return value # Instance of bytes


def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode('utf-8') # uses 'utf-8' for decoding
    else:
        value = bytes_or_str
    return value # Instance of str

#=============================================================================

class LBase(object):
    def __init__(self, **kw):
        super(LBase, self).__init__()

#=============================================================================
# (projekt, tests).

class LStoreDb(LBase):
    def __init__(self, path, **kw):
        super(LStoreDb, self).__init__(**kw)
        self.path = path

    def strToBase(self,s, b):
        return (int(s,b))

    def numberToBase(self,n, b):
        if n == 0:
            return [0]
        digits = []
        while n:
            digits.append(int(n % b))
            n //= b
        return digits[::-1]

    def pack4to3(self,deal):
        cdeal = []
        cbin = ""
        for k in range(0,len(deal),4):
            a = deal[k]
            b = deal[k+1]
            c = deal[k+2]
            d = deal[k+3]
            abcd = "{0:06b}{1:06b}{2:06b}{3:06b}".format(a,b,c,d)
            #print (abcd)

            x = ((a << 2) & 0xfc) | ((b >> 4) & 0x03)
            y = ((b << 4) & 0xf0) | ((c >> 2) & 0x0f)
            z = ((c << 6) & 0xc0) | ((d) & 0x3f)
            xyz = "{0:08b}{1:08b}{2:08b}".format(x,y,z)
            #print (xyz)

            cdeal.append(x)
            cdeal.append(y)
            cdeal.append(z)
            cbin += xyz;

        #print (cbin,len(cbin))
        return cdeal

    def show(self,deal):

        print ('Deal:')
        print ('As Numbers:')
        print (deal)
        print ('As Card Symbols:')

        # Darstellung mit Symbolen wie in der Literatur oft verwendet.
        ss = [cardnum_to_sym(c) for c in deal]
        # print (ss)
        print (" ".join(ss))
        # print (" ".join(ss).split(" "))
        # print ([cardsym_to_num(t) for t in ss])

        # Buchstaben Darstellung.
        print ('As Alfa Representation')
        alpha = deal_to_alpha(deal)
        print (alpha.decode(),len(alpha))
        d2 = alpha_to_deal(alpha)
        #print (d2,len(d2))
        alpha2 = deal_to_alpha(d2)
        #print (alpha2,len(alpha2))
        #print ('')

        # levensthein als qualitätsmerkmal (ungeeignet!)
        #ldd = levensthein(str(alpha),'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
        #print ('Levensthein Difference:',ldd)
        
        #   Ein anderer (hauruck-)Ansatz wäre die zahlen binär zu codieren. Wir
        # kommen mit 6 bit/wert durch, und könnten so auch 4 auf 3 bytes packen.
        # Das gibt 52*6 = 312 bits, oder 39 bytes.
        #   Oder: druckbare Repräsentation kann auch erhalten werden, wenn wir
        # die Permutation zu 52 in die Ascii Buchstaben packen. Es reicht genau
        # für alle Buchstaben in gross und klein.

        cdeal = self.pack4to3(deal)
        #print (cdeal,len(cdeal))
        #print (bytes(cdeal),len(bytes(cdeal)))
        #print([hex(i) for i in cdeal])
        hs = "".join(["{0:02x}".format(i) for i in cdeal])
        #print(hs)
        #print(bytes(cdeal))

        #f = fact()
        #print (f.calc(5))
        #print (f.calc(7))
        #print (f.calc(52))
        #print (factorial(7))
        #print (factorial(9))

        lm = Lehmer(perm=deal)

        print('As Lehmer Code:')
        print(lm.getCode())
        print ("Anzahl Sequenzen (aus Lehmer):", lm.getQuality())
        print('As Index:')
        print(lm.getIndex())

        #d = deal_from_lehmer(l)
        #l2 = lehmer_from_index(s)

        #lehmer_from_deal2(deal)

        return 0

    # TBD
    def store(self,date,solved,deal,moves):
        # date: timestamp
        # solved: true or false
        # deal: (52-ersystem? - es würden alle buchstaben reichen)
        pass

    def recall(self,date):
        pass


#=============================================================================

class LStore(LBase):
    def __init__(self, path, **kw):
        super(LStore, self).__init__(**kw)
        self.path = path
        self.state = {}

    def setEntry(self, subject, value):
        self.state[subject] = value

    def getEntry(self, subject):
        if subject in self.state:
            return self.state[subject]
        else:
            return None

    def store(self):
        try:
            fj = open(self.path, mode = 'w')
        except IOError:
            return

        try:
            json.dump(self.state, fj)
        except Exception:
            pass

        try:
            fj.close()
        except Exception:
            pass

    def load(self):
        ret = True
        try:
            fj = open(self.path)
        except IOError:
            ret = False
            return ret

        try:
            self.state = json.load(fj)
        except Exception:
            ret = False

        try:
            fj.close()
        except Exception:
            pass

        return ret

#=============================================================================


class menubar(ActionBar):
    def __init__(self, **kw):
        super(menubar, self).__init__(**kw)
        self.menu = None

    def setMenu(self, menu):

        # Letztes Menu entfernen
        last = self.menu
        if (last != None):
            self.remove_widget(last)
            self.menu = None

        # Neues Menu einfuegen
        if (menu != None):
            self.add_widget(menu)
            self.menu = menu
            menu.setBar(self)


#=============================================================================

class menu(ActionView, LBase):
    def __init__(self, prev, **kw):
        super(menu, self).__init__(**kw)
        class MyActionPrevious(ActionPrevious, LBase):
            pass
        self.ap = ap = MyActionPrevious(with_previous=prev, **kw)
        self.add_widget(ap)
        self.bar = None
        self.uppermenu = None

    def addItem(self, mi):
        mi.setBar(self.bar)
        self.add_widget(mi)

    def setBar(self, bar):
        self.bar = bar

    def prev(self, menu):
        self.uppermenu = menu
        self.ap.bind(on_release=self.upper)
        pass

    def upper(self, event):
        #print('upper')
        self.bar.setMenu(self.uppermenu)


#=============================================================================


class menuGroup(ActionGroup, LBase):
    def __init__(self, menu, **kw):
        super(menuGroup, self).__init__(**kw)
        #self.bar = menu.bar
        self.bar = None
        menu.addItem(self)

    def addItem(self, mi):
        mi.setBar(self.bar)
        self.add_widget(mi)

    def setBar(self, bar):
        self.bar = bar


#=============================================================================


class menuItem(ActionButton, LBase):
    def __init__(self, menu, **kw):
        super(menuItem, self).__init__(**kw)
        self.bar = None
        self.submenu = None
        self.menu = menu
        self.menu.addItem(self)
        if 'command' in kw:
            self.setCommand(kw['command'])
        if 'submenu' in kw:
            self.setSubMenu(kw['submenu'])

    def setBar(self, bar):
        self.bar = bar

    def onClick(self, event):
        #print('click')
        self.bar.setMenu(self.submenu)
        return True

    def setSubMenu(self, submenu):
        #print('submenu')
        self.submenu = submenu
        self.submenu.prev(self.menu)
        self.bind(on_release=self.onClick)
        pass

    def setCommand(self, cmd):
        #print('command')
        self.bind(on_release=cmd)


#=============================================================================

from kivy.uix.button import Button


class menuButton(Button, ActionItem, LBase):
    def __init__(self, menu, **kw):
        super(menuButton, self).__init__(**kw)

        self.bar = None
        self.submenu = None
        self.menu = menu
        self.menu.addItem(self)
        if 'command' in kw:
            self.setCommand(kw['command'])
        if 'submenu' in kw:
            self.setSubMenu(kw['submenu'])
        self.size_hint = (None, 1.0)
        self.background_down = 'atlas://data/images/defaulttheme/action_item_down'
        self.background_normal = 'atlas://data/images/defaulttheme/action_item'

    def setBar(self, bar):
        self.bar = bar

    def onClick(self, event):
        #print('click')
        self.bar.setMenu(self.submenu)
        return True

    def setSubMenu(self, submenu):
        #print('submenu')
        self.submenu = submenu
        self.submenu.prev(self.menu)
        self.bind(on_release=self.onClick)
        pass

    def setCommand(self, cmd):
        #print('command')
        self.bind(on_release=cmd)


#=============================================================================


class Rect(object):
    # A basic rectangle object

    def __init__(self, left=0, top=0, width=0, height=0):
        self.left = int(left)
        self.top = int(top)
        self.width = int(width)
        self.height = int(height)

    def setRect(self, left=0, top=0, width=0, height=0):
        self.left = int(left)
        self.top = int(top)
        self.width = int(width)
        self.height = int(height)


#		print('Rect::setRect',left,top,width,height)

    def enclosesXY(self, x, y):
        # Determine if a point lies within the Rect
        return ((x >= self.left) and (x < self.left + self.width)
                and (y >= self.top) and (y < self.top + self.height))

    def getTopLeft(self):
        return (self.left, self.top)

    def getLeftTopWidthHeight(self):
        return (self.left, self.top, self.width, self.height)

    def unionWith(self, otherRect):
        # Modify the Rect to include another Rect
        left = min(self.left, otherRect.left)
        right = max(self.left + self.width, otherRect.left + otherRect.width)
        top = min(self.top, otherRect.top)
        bottom = max(self.top + self.height, otherRect.top + otherRect.height)

        self.left = left
        self.top = top
        self.width = (right - left)
        self.height = (bottom - top)


def cardSize(drawable):
    cw = drawable.size[0] / 10.0
    ch = 97.0 * cw / 73.0
    return (cw, ch)


def cardSizeHint(drawable):
    cwch = cardSize(drawable)
    rcw = cwch[0] / drawable.size[0]
    rch = cwch[1] / drawable.size[1]
    return (rcw, rch)


class Card(object):
    # A Card object defined by card number (0-51), screen location and size, and pixbuf
    # Note that the cards are ordered A,2,3,4,5,6,7,8,9,10,J,Q,K
    # The suits are ordered Clubs, Diamonds, Spades, Hearts

    def __init__(self, cardNum, left=0, top=0, width=0, height=0, pixBuf=None):
        self.cardNum = cardNum
        self.rect = Rect(left, top, width, height)
        self.pixBuf = pixBuf
        self.cardImage = None

    def getSuit(self):
        return self.cardNum // CARDS_PER_SUIT

    def getSuitColour(self):
        return (self.cardNum // CARDS_PER_SUIT) % 2

    def getValue(self):
        return self.cardNum % CARDS_PER_SUIT

    def setRect(self, left=0, top=0, width=0, height=0):
        self.rect.setRect(left, top, width, height)
        # print('Card::setRect',left,top,width,height)

    def enclosesXY(self, x, y):
        # Determine if a point lies within the Card
        return self.rect.enclosesXY(x, y)

    def drawCard(self, drawable, xyPt=None):
        # Draw the Card in the given drawable, using the supplied GC

        if (xyPt != None):
            left, top = xyPt
        else:
            left, top = self.rect.getTopLeft()

        self.drawCardImg(drawable, left, top)

    def drawCardImg(self, drawable, left, top):
        #		print (self.cardNum,self.pixBuf)
        #		print (left,top,drawable.size)
        #		print (self.rect.height)

        leftp = 1.0 * (left)
        topp = 1.0 * (drawable.size[1] - top - self.rect.height)
        left = 1.0 * (left) / (1.0 * drawable.size[0])
        top = 1.0 * (drawable.size[1] - top - self.rect.height) / (
            1.0 * drawable.size[1])

        # print (left,top)

        tmpca = CardImg(source=self.pixBuf)
        tmpca.size_hint = cardSizeHint(drawable)

        #		tmpca.pos_hint = {'x': left, 'y': top}
        tmpca.pos = [leftp, topp]
        #print ('pos-hint',tmpca.pos_hint,'pos',tmpca.pos)
        # man kann mit pos oder pos_hint arbeiten, es geht beides. Aber der Wert
        # muss vor dem Einbringen des widgets in den Container erfolgen. pos_hint
        # hat den Nachteil, dass die Animation nicht laeuft, wenn dieser Parameter
        # nicht {} ist.

        if (self.cardImage != None):
            drawable.clear_widgets([self.cardImage])
        drawable.add_widget(tmpca)
        self.cardImage = tmpca
        #print ('pos',self.cardImage.pos,'size',self.cardImage.size)

    def clearSelection(self):
        #		print ('card deselect',self.pixBuf)
        if self.cardImage != None:
            self.cardImage.selected = False
#			print ('card deselected',self.pixBuf)

    def setSelection(self, x, y):
        #		print ('card select',self.pixBuf)
        if self.cardImage != None:
            if self.enclosesXY(x, y):
                self.cardImage.selected = True


#				print ('card selected',self.pixBuf)

    def getTopLeft(self):
        return self.rect.getTopLeft()

    def getLeftTopWidthHeight(self):
        return self.rect.getLeftTopWidthHeight()

    def getRect(self):
        left, top, w, h = self.rect.getLeftTopWidthHeight()
        return Rect(left, top, w, h)

    def printCard(self):
        srcCardVal = self.getValue()
        srcSuit = self.getSuit()
        srcSuitColour = self.getSuitColour()
        print("%s %s" % (SUITNAMES[srcSuit], CARDNAMES[srcCardVal]))


class CardStack(object):
    # An object representing a stack of cards
    # The CardStack contains a list of Card objects, possesses an onscreen location
    # The CardStack can draw itself; if there are no Cards, then the emptyStackPixBuf is displayed
    # The CardStack's yOffset controls the vertical offset of cards in the stack

    def __init__(self, left, top, emptyStackPixBuf, stackSuit, yOffset=0):
        self.left = int(left)
        self.top = int(top)
        self.emptyStackCardImage = None
        self.emptyStackPixBuf = emptyStackPixBuf
        self.stackSuit = stackSuit
        self.cards = []
        self.yOffset = yOffset

        # (folgendes dient nur der bemessung des rects).
        tmpimg = CardImg(source=emptyStackPixBuf)
        self.cardWidth = tmpimg.get_width()
        self.cardHeight = tmpimg.get_height()
        del tmpimg

        #		print ('CardStack init',self.left,self.top,self.cardWidth,self.cardHeight)

        self.rect = Rect(self.left, self.top, self.cardWidth, self.cardHeight)

    def getNumCards(self):
        return len(self.cards)

    def clearStack(self):
        self.cards = []

    def getRect(self):
        left, top, w, h = self.rect.getLeftTopWidthHeight()
        return Rect(left, top, w, h)

    def getLeftTopWidthHeight(self):
        left, top, w, h = self.rect.getLeftTopWidthHeight()
        return left, top, w, h

    def setLeftTop(self, left, top, width, height):
        #		print ('CardStack::setLeftTop',left,top)
        self.left = left
        self.top = top
        self.cardWidth = width
        self.cardHeight = height
        if (self.yOffset > 0):
            self.yOffset = self.cardHeight / 4.8
        #print ('yOffset',self.yOffset)

        self.rect = Rect(self.left, self.top, self.cardWidth,
                         self.cardHeight + self.yOffset * len(self.cards))

        for i in range(len(self.cards)):
            self.cards[i].setRect(self.left, self.top + self.yOffset * i,
                                  self.cardWidth, self.cardHeight)

    def pushCard(self, card):
        card.setRect(self.left, self.top + self.yOffset * len(self.cards),
                     self.cardWidth, self.cardHeight)
        self.cards.append(card)
        self.rect = Rect(self.left, self.top, self.cardWidth,
                         self.cardHeight + self.yOffset * len(self.cards))

    def getCardValueSuitColour(self, cardIndex):
        # Get the card value, suit, and colour of a card on the CardStack; negative cardIndex values work the expected way (e.g. -1 is last/top card); if a bad index value is supplied, return the stack suit (i.e. ace stack suit)
        if (cardIndex >= len(self.cards) or abs(cardIndex) > len(self.cards)):
            return -1, self.stackSuit, self.stackSuit % 2
        else:
            card = self.cards[cardIndex]
            return card.getValue(), card.getSuit(), card.getSuitColour()

    def getTopCardRect(self):
        # Get the rect of top card on the CardStack; return bare rect if there are no cards
        if (len(self.cards) > 0):
            return self.cards[-1].getRect()
        else:
            left, top, w, h = self.rect.getLeftTopWidthHeight()
            return Rect(left, top, w, h)

    def getNextTopCardLeftTop(self):
        # Get the top/left of the next card location on the stack (useful for animation)
        if (len(self.cards) > 0):
            x, y, w, h = self.cards[-1].getLeftTopWidthHeight()
            return (x, y + self.yOffset)
        else:
            return (self.left, self.top)

    def popCard(self):
        # Remove the top card on the CardStack; return the popped Card or None
        if (len(self.cards) > 0):
            card = self.cards[-1]
            del self.cards[-1]
            self.rect.setRect(self.left, self.top, self.cardWidth,
                              self.cardHeight + self.yOffset * len(self.cards))
            return card
        else:
            return None

    def enclosesXY(self, x, y):
        # Determine if a point lies within the CardStack
        return self.rect.enclosesXY(x, y)

    def clearSelection(self):
        #		print ('stack deselect')
        if self.emptyStackCardImage != None:
            self.emptyStackCardImage.selected = False
        for c in self.cards:
            c.clearSelection()

    def setSelection(self, x, y):
        #		print ('stack select')
        if self.emptyStackCardImage != None:
            if (self.rect.enclosesXY(x, y)):
                self.emptyStackCardImage.selected = False
        if (self.cards != []):
            self.cards[-1].setSelection(x, y)

    def printselmsg(self, instance, value):
        print('card selected', instance, value)

    def drawpixBuf(self, drawable, left, top):

        tmpimg = CardImg(source=self.emptyStackPixBuf)
        tmpimg.bind(selected=self.printselmsg)

        pleft = 1.0 * (left)
        ptop = 1.0 * (drawable.size[1] - top - self.rect.height)
        left = 1.0 * (left) / (1.0 * drawable.size[0])
        top = 1.0 * (drawable.size[1] - top - self.rect.height) / (
            1.0 * drawable.size[1])

        # print (left,top,self.emptyStackPixBuf);

        tmpimg.size_hint = cardSizeHint(drawable)
        #			tmpimg.pos_hint = {'x': left, 'y': top}
        tmpimg.pos = (pleft, ptop)

        if (self.emptyStackCardImage != None):
            drawable.clear_widgets([self.emptyStackCardImage])
        drawable.add_widget(tmpimg)
        self.emptyStackCardImage = tmpimg

    def drawStack(self, drawable):
        # Zuunterst das empty stack image setzen
        left, top = self.rect.getTopLeft()
        if (self.yOffset > 0):
            top = top - self.yOffset * len(self.cards)
        self.drawpixBuf(drawable, left, top)
        # Alle Karten darueber
        for c in self.cards:
            c.drawCard(drawable)

    def drawStackOld(self, drawable):
        # Draw the stack (or the "empty stack" image) in the given drawable, using the supplied GC
        if (len(self.cards) <= 0):
            left, top = self.rect.getTopLeft()
            self.drawpixBuf(drawable, left, top)
        elif (self.yOffset == 0):
            self.cards[-1].drawCard(drawable)
        else:
            for c in self.cards:
                c.drawCard(drawable)

    def drawTopCard(self, drawable):
        # Draw the top card (or the "empty stack" image) in the given drawable, using the supplied GC
        if (len(self.cards) <= 0):
            left, top = self.rect.getTopLeft()
            self.drawpixBuf(drawable, left, top)
        else:
            self.cards[-1].drawCard(drawable)


class MoveCardTask(Task):
    def __init__(self, name, drawingArea, card, fromX, fromY, toX, toY):
        super(MoveCardTask, self).__init__(name)
        self.drawingArea = drawingArea
        self.card = card
        self.fromX = fromX
        self.fromY = fromY
        self.toX = toX
        self.toY = toY

    def start(self):
        super(MoveCardTask, self).start()

        self.card.drawCard(self.drawingArea)
        xf = self.fromX
        yf = self.drawingArea.size[1] - self.fromY - self.card.rect.height
        xt = self.toX
        yt = self.drawingArea.size[1] - self.toY - self.card.rect.height
        #self.card.cardImage.pos_hint = {}
        self.card.cardImage.pos = (xf, yf)

        #anim = Animation(x=xt,y=yt,duration=0.17,t='in_out_quad')
        anim = Animation(x=xt, y=yt, duration=0.17, t='in_out_expo')
        #anim = Animation(x=xt,y=yt,duration=0.17,t='out_quad')
        #anim = Animation(x=xt,y=yt,duration=0.17,t='out_back')
        #anim = Animation(x=xt,y=yt,duration=0.17,t='in_bounce')
        #anim = Animation(x=xt,y=yt,duration=0.17,t='in_expo')
        #anim = Animation(x=xt,y=yt,duration=0.2,t='out_expo')
        if (self.card.cardImage != None):
            anim.bind(on_complete=self.animEnd)
            anim.start(self.card.cardImage)
            # print ('start anim:')
            # self.card.printCard()
        else:
            print('start anim, not started: card image == None !')

    def animEnd(self, instance, value):
        self.stop()


from saf import SaF

class FreeCell(object):

    # Handle of android return key
    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            # redirect to the game undo Function
            self.undoMove()
            return True  # consumed
        else:
            return False  # delegate

    def getStorage(self):
        fstorage = ".freecell4maemo"
        if requestStoragePerm():
            logging.info('FreeCell: storage perm granted')

            from android.storage import primary_external_storage_path
            primary_ext_storage = primary_external_storage_path()
            fstorage = primary_ext_storage+"/"+fstorage
            if not os.path.exists(fstorage):
                os.makedirs(fstorage)
        else:
            logging.info('FreeCell: storage perm denied')

            if not os.path.exists(fstorage):
                os.makedirs(fstorage)

        logging.info(fstorage)
        return fstorage

    def __init__(self):
        # Init the rendering objects to None for now; they will be properly populated during the expose_event handling
        self.greenColour = None
        self.redColour = None
        self.blackColour = None
        self.whiteColour = None
        self.tmpPixmap = None
        self.gameover = False  # jkq
        self.animIsComplete = False
        self.startCardOrder = None

        #self.saf = SaF()

        if platform=='android':

            # tests mit saf:
            #self.saf.act_intent()
            #self.saf.set_intent()
            # soweit ginge das: der picker dialog erscheint. Und die
            # Callback routine wird aufgerufen und liefert auch etwas
            # vernünftiges.
            # wir könne aber mit diesen andgaben nichts vernünftiges
            # tun. Direkter zugriff auf die pfade ist nicht möglich, sondern
            # man muss das android api benutzen.
            # ausserdem besteht ein synchronisation problem beim programm
            # start (aber das ist das gleiche wie auch bei requestStoragePerm
            # unten)

            #from plyer import storagepath
            #sdcard = str(storagepath.get_external_storage_dir())
            #logging.info(sdcard)
            # -> geht auch (plyer in buildozer.spec angeben)

            # another test (-> das war eine ente!)
            #from jnius import autoclass
            #context = autoclass('android.content.Context')
            #path_file = context.getExternalFilesDir(None)
            #path = path_file.getAbsolutePath()
            #logging.info(path)

            fstorage = self.getStorage()
            self.store = LStore(fstorage+'/current.json')
        else:
            self.store = LStore('.freecell4maemo/current.json')

        # Taskq fuer Animationssequenzen
        self.taskQ = TaskQ()

        # Load the cards
        self.cardPixbufs = [("%s/%02d.png" % (CARDFOLDER, i))
                            for i in range(TOTALNUMCARDS)]

        # Muster fuer erste einstellungen.
        tmp = CardImg(source=self.cardPixbufs[0])
        self.cardHeight = tmp.get_height()
        self.cardWidth = tmp.get_width()

        # Each group of cards (freecells, aces, columns) is stored in a list of CardStacks
        # We also keep track of a bounding rect for each group and use this rect when doing hit-testing of mouse clicks

        # Set up the "free cells" (4 cells in top left of screen)
        self.freecellStacks = [
            CardStack(0, 0, self.cardPixbufs[BLANK_BACK], -1, 0)
            for i in range(NUMFREECELLS)
        ]
        self.freeCellsRect = None

        # Set up the "aces" (4 cells in top right of screen); order is important!
        self.acesStacks = [
            CardStack(0, 0, self.cardPixbufs[CLUBS_BACK + i], i, 0)
            for i in range(NUMACES)
        ]
        self.acesRect = None

        # Set up the columns
        self.mainCardStacks = [
            CardStack(0, 0, self.cardPixbufs[BLANK_BACK], -1,
                      self.cardHeight // 5) for i in range(NUMCOLUMNS)
        ]
        self.mainCardsRects = None

        # Keep track of all card stack moves so we can undo moves
        self.undoStack = []

        # Initial Moves as member
        self.moves = []

        '''
        # try opening the save file
        newgame = not self.read_current_game()

        # Initialize the cards
        self.setupCards(newgame)
        '''

        # Default to manual play mode
        self.smartPlayMode = False

        # These get set properly during the configure event handler
        self.windowWidth = 0
        self.windowHeight = 0
        self.windowFullscreen = False

        # Create menus

        #self.header = ButtonLine()
        #self.hbutton = Button(text='Freecell for Maemo on Android')

        grey0 = 'icons/grey1.jpg'
        grey1 = 'icons/grey2.jpg'
        grey2 = 'icons/grey4.jpg'

        # Knöpfe am rechten Rand.

        self.menu = ButtonColm()

        self.undo = Button(text='Undo', background_normal=grey1)
        self.undo.bind(on_press=self.undo_move_cb)
        self.menu.add_widget(self.undo)

        self.automove = Button(text='Auto', background_normal=grey2)
        self.automove.bind(on_press=self.auto_move_cb)
        self.menu.add_widget(self.automove)

        # Menubar

        self.header = menubar()
        self.hmenu = menu(
            False,
            app_icon='icons/gnome-freecell48.png',
            text='Freecell for Maemo on Android',
            background_image=grey0)
        self.header.setMenu(self.hmenu)

        #self.done = menuButton(self.hmenu,text='Exit',command=self.exit_menu_cb)
        self.restartgame = menuButton(
            self.hmenu, text='Restart', command=self.restart_game_menu_cb)
        self.newgame = menuButton(
            self.hmenu, text='New', command=self.new_game_menu_cb)
        self.about = menuButton(
            self.hmenu, text='About', command=self.about_menu_show)
        self.aboutBox = None

        self.read_settings()

        # Main part of window is a DrawingArea

        self.drawingArea = PlayGround()
        self.mainWindow = MainWindow()
        self.widgetLine = ButtonLine()

        # (Randsicherung)
        # self.mainWindow.add_widget(Button(size_hint=(1.0, 0.01)))

        self.widgetLine.size_hint = (1.0, 1.0)
        self.mainWindow.add_widget(self.header)
        self.mainWindow.add_widget(self.widgetLine)

        self.drawingArea.size_hint = (0.9, 1.0)
        self.menu.size_hint = (0.1, 1.0)
        self.widgetLine.add_widget(self.drawingArea)
        self.widgetLine.add_widget(self.menu)

        self.drawingArea.bind(lastHitPos=self.drawingAreaClick)
        self.drawingArea.bind(size=self.configure_event_cb)

        Window.bind(on_keyboard=self.key_input)

        # Track the currently selected card
        self.selectedCardRect = Rect()
        self.selectedCardStack = None
        self.selectedCardType = None

        self.debugMode = False

        #self.initMoves()

    def initMoves(self):
        # jkq
        logging.info('FreeCell: initial moves %s' % self.moves)
        if len(self.moves) > 0:
            for (src, dst) in self.moves:
                logging.debug('FreeCell: initial move: %s, %s' % (src, dst))
                src_stack = self.retrieve_stack(src[0])
                dst_stack = self.retrieve_stack(dst[0])
                self.moveCardOld(src_stack[src[1]], dst_stack[dst[1]])
        self.moves = []

    def compare_stack(self, stack):
        for s in range(NUMFREECELLS):
            if stack == self.freecellStacks[s]:
                return (0, s)
        for s in range(NUMACES):
            if stack == self.acesStacks[s]:
                return (1, s)
        for s in range(NUMCOLUMNS):
            if stack == self.mainCardStacks[s]:
                return (2, s)
        return (-1, -1)

    def retrieve_stack(self, stack):
        if stack == 0:
            #print 'free'
            return self.freecellStacks
        elif stack == 1:
            #print 'aces'
            return self.acesStacks
        elif stack == 2:
            #print 'main'
            return self.mainCardStacks
        else:
            # pray we never get here!
            return None

    def save_settings(self):
        pass

    def read_settings(self):
        pass

    def save_current_game(self):
        moves = []
        for (src, dst) in self.undoStack:
            move = (self.compare_stack(src), self.compare_stack(dst))
            moves.append(move)

        # logging.info('FreeCell: save %s' % self.startCardOrder)
        # logging.info('FreeCell: save %s' % moves)

        self.store.setEntry('moves',moves)
        self.store.setEntry('deal',self.startCardOrder)
        self.store.store()

    def read_current_game(self):
        self.store.load()
        self.moves = self.store.getEntry('moves')
        if self.moves is None:
            return False
        self.startCardOrder = self.store.getEntry('deal')
        if self.startCardOrder is None:
            return False
        # ev. weitere Konsistenztests. Notwendig wenn wir es
        # zulassen, das gespeicherte Spiele geladen werden.
        return True

    def save_game(self):
        logging.info("FreeCell: save_game")
        self.save_current_game()
        self.save_settings()

        if self.checkGameOver():
            # ev. spiel-lösungen in db sammeln.
            pass

    def exit_menu_cb(self, widget):
        logging.info("FreeCell: exit_menu_cb")
        self.save_game()
        stopTouchApp()

    def restart_game_menu_cb(self, widget):
        logging.info('FreeCell: restart_game_menu_cb')
        self.undoStack = []
        self.acesStacks = [
            CardStack(0, 0, self.cardPixbufs[CLUBS_BACK + i], i, 0)
            for i in range(NUMACES)
        ]
        self.freecellStacks = [
            CardStack(0, 0, self.cardPixbufs[BLANK_BACK], -1, 0)
            for i in range(NUMFREECELLS)
        ]
        self.setupCards(False)
        self.setCardRects()
        self.redrawOffscreen()
        self.updateRect(None)

    def about_menu_hide(self, instance, pos):
        if (self.aboutBox != None):
            self.aboutBox.dismiss()
            self.aboutBox = None
            return False

    def about_menu_show(self, widget):
        if (self.aboutBox == None):
            self.aboutBox = Popup(
                title='About',
                content=Label(
                    text=ABOUT_TEXT,
                    text_size=(0.9 * self.drawingArea.size[0], None)),
                size_hint=(0.9, 0.9),
                auto_dismiss=False)
            self.aboutBox.bind(on_touch_down=self.about_menu_hide)
            self.aboutBox.open()

    def new_game_menu_cb(self, widget):
        self.undoStack = []
        self.acesStacks = [
            CardStack(0, 0, self.cardPixbufs[CLUBS_BACK + i], i, 0)
            for i in range(NUMACES)
        ]
        self.freecellStacks = [
            CardStack(0, 0, self.cardPixbufs[BLANK_BACK], -1, 0)
            for i in range(NUMFREECELLS)
        ]
        self.setupCards()
        self.setCardRects()
        self.redrawOffscreen()
        self.updateRect(None)

    # Tastatur: nicht angebunden.

    def key_press_cb(self, widget, event, *args):
        if (event.keyval == gtk.keysyms.F6):
            if (self.windowFullscreen):
                self.mainWindow.unfullscreen()
            else:
                self.mainWindow.fullscreen()

        elif (event.keyval == gtk.keysyms.Up):
            #print "Up!"
            self.smartPlayMode = False
            self.updateRect(self.starRect)

        elif (event.keyval == gtk.keysyms.Down):
            #print "Down!"
            self.smartPlayMode = True
            self.updateRect(self.starRect)

        elif (event.keyval == gtk.keysyms.Left):
            #print "Left!"
            pass

        elif (event.keyval == gtk.keysyms.Right):
            #print "Right!"
            pass

        elif (event.keyval == gtk.keysyms.BackSpace):
            #print "Backspace!"
            self.undoMove()

        elif (event.keyval == gtk.keysyms.space):
            #print "Space!"
            self.autoMoveCardsHome()

        elif (event.keyval == gtk.keysyms.KP_Enter):
            #print "Return!"
            self.autoMoveCardsHome()

        elif (event.keyval == gtk.keysyms.F7):
            #print "Zoom +!"
            self.debugMode = False

        elif (event.keyval == gtk.keysyms.F8):
            #print "Zoom -!"
            self.debugMode = True

    def undo_move_cb(self, widget):
        self.undoMove()

    def auto_move_cb(self, widget):
        logging.info('FreeCell: auto_move_cb')
        #gobject.timeout_add(500, self.auto_move_wrapper)
        #Clock.schedule_once(self.auto_move_wrapper, 0.1)
        self.autoMoveCardsHome()

    def auto_move_wrapper(self, dst):
        self.autoMoveCardsHome()
        return False

    def autoMoveCardsHome(self):
        # Move cards to the ace stacks, where possible

        if not (self.taskQ.taskQsAreEmpty()):
            return

        cardStacks = self.freecellStacks + self.mainCardStacks

        while (True):
            movedACard = False

            for srcStack in cardStacks:
                srcCardValue, srcCardSuit, srcCardSuitColour = srcStack.getCardValueSuitColour(
                    -1)
                if (srcCardSuit >= 0):
                    aceCardValue, aceCardSuit, aceCardSuitColour = self.acesStacks[
                        srcCardSuit].getCardValueSuitColour(-1)
                    if (srcCardValue == aceCardValue + 1):
                        # tempRect = srcStack.getTopCardRect()
                        # self.flashRect(tempRect)
                        self.moveCard(srcStack, self.acesStacks[srcCardSuit])
                        movedACard = True

            if (movedACard != True):
                break

        self.clearCardSelection()
        #self.checkGameOver()

    def checkGameOver(self):
        # Game over?
        ret = False
        numFullAceStacks = 0

        for stack in self.acesStacks:
            cardVal, cardSuit, cardColour = stack.getCardValueSuitColour(-1)
            if (cardVal == CARDS_PER_SUIT - 1):
                numFullAceStacks += 1

        if (numFullAceStacks == NUMACES):
            self.gameover = True  # jkq
            ret = True

        return ret

    def undoMove(self):

        if not (self.taskQ.taskQsAreEmpty()):
            return

        # Undo a move
        if len(self.undoStack) > 0:
            srcStack, dstStack = self.undoStack[-1]
            self.moveCard(dstStack, srcStack)
            # The call to moveCard actually records the undo as a move, so
            # we need to pop the last TWO entries in the stack to correct this.
            del self.undoStack[-1]
            del self.undoStack[-1]
            self.clearCardSelection()

    def setupCards(self, doShuffle=True):
        # Shuffle deck, distribute cards into the columns

        if (doShuffle):
            self.gameover = False  # jkq
            cards = [i for i in range(NUMCARDS)]
            random.SystemRandom().shuffle(cards)
            self.startCardOrder = cards
            self.moves = []

            LStoreDb('').show(cards)
        else:
            cards = self.startCardOrder
            LStoreDb('').show(cards)

        for i in range(NUMCOLUMNS):
            self.mainCardStacks[i].clearStack()

        for i in range(NUMCARDS):
            cardNum = cards[i]
            cardCol = i % NUMCOLUMNS
            newCard = Card(cardNum, pixBuf=self.cardPixbufs[cardNum])
            self.mainCardStacks[cardCol].pushCard(newCard)

    def getStackListEnclosingRect(self, cardStackList):
        # Get a rect that encloses all the cards in the given list of CardStacks

        rect = cardStackList[0].getRect()
        for i in range(1, len(cardStackList)):
            rect.unionWith(cardStackList[i].getRect())
        return rect

    def setCardRects(self):
        # Set the position of all card stacks; this is done in response to a configure event

        sizeHint = cardSize(self.drawingArea)
        cardWidth = sizeHint[0]
        cardHeight = sizeHint[1]
        vertSeparatorWidth = 1.0 * VERT_SEPARATOR_WIDTH * cardWidth / self.cardWidth

        logging.info('FreeCell: setCardRects %d %d %d' %
                     (cardWidth, cardHeight, vertSeparatorWidth))

        # Set location of main stacks of cards
        cardHorizSpacing = self.windowWidth / 8.0
        for i in range(NUMCOLUMNS):
            x = int(i * cardHorizSpacing + (cardHorizSpacing - cardWidth) // 2)
            self.mainCardStacks[i].setLeftTop(
                x, vertSeparatorWidth + cardHeight + vertSeparatorWidth,
                cardWidth, cardHeight)

        # Set location of free cells and aces
        cardHorizSpacing = self.windowWidth / 8.5
        for i in range(NUMFREECELLS):
            x = i * cardHorizSpacing + (cardHorizSpacing - cardWidth) // 2
            self.freecellStacks[i].setLeftTop(x, vertSeparatorWidth, cardWidth,
                                              cardHeight)

            x = int((i + NUMFREECELLS + 0.5) * cardHorizSpacing +
                    (cardHorizSpacing - cardWidth) // 2)
            self.acesStacks[i].setLeftTop(x, vertSeparatorWidth, cardWidth,
                                          cardHeight)

        # Get the enclosing rects for click-testing
        self.mainCardsRects = self.getStackListEnclosingRect(self.acesStacks)
        self.freeCellsRect = self.getStackListEnclosingRect(
            self.freecellStacks)
        self.acesRect = self.getStackListEnclosingRect(self.acesStacks)

    def delete_event_cb(self, widget, event, data=None):
        # False means okay to delete
        return False

    def updateRect(self, rect):
        # Queue a redraw of an onscreen rect
        if (rect == None):
            x, y, w, h = 0, 0, self.windowWidth, self.windowHeight
        else:
            x, y, w, h = rect.getLeftTopWidthHeight()

    def redrawOffscreen(self):
        # Redraw the game board and all card stacks

        #print('da',self.drawingArea.pos,self.drawingArea.size)
        #print('mw',self.mainWindow.pos,self.mainWindow.size)

        self.drawingArea.clear_widgets()  # zuerst aufraeumen.

        for cardStack in self.acesStacks:
            cardStack.drawStack(self.drawingArea)

        for cardStack in self.freecellStacks:
            cardStack.drawStack(self.drawingArea)

        for cardStack in self.mainCardStacks:
            cardStack.drawStack(self.drawingArea)

    def configure_event_cb(self, widget, event):
        # Handle the window configuration event at startup or when changing to/from fullscreen

        logging.info("FreeCell: configure_event_cb")

        # Allocate a Pixbuf to serve as the offscreen buffer for drawing of the game board

        # x, y, width, height = widget.get_allocation()
        x = widget.x
        y = widget.y
        width = widget.size[0]
        height = widget.size[1]

        #print ('mw',self.mainWindow.pos,self.mainWindow.size)
        #print ('da',widget.pos,widget.size)
        #print ('bu',self.menu.pos,self.menu.size)
        #print ('he',self.header.pos,self.header.size)

        # Screen geometry has changed, so note new size, set CardStack locations, redraw screen
        self.windowWidth = width
        self.windowHeight = height

        logging.info(
            "configure_event_cb: self.windowWidth = %d, self.windowHeight = %d"
            % (self.windowWidth, self.windowHeight))
        logging.debug(
            "configure_event_cb: self.windowWidth = %d, self.windowHeight = %d"
            % (self.windowWidth, self.windowHeight))

        # Resize has occurred, so set new card rects
        self.setCardRects()

        # Redraw everything
        self.redrawOffscreen()
        return True

    def clearCardSelection(self):
        # Clear the current card selection (drawn inverted)

        #		logging.info("clearCardSelection: (%d,%d) %dx%d" %(self.selectedCardRect.getLeftTopWidthHeight()))

        if (self.selectedCardRect != None):
            self.updateRect(self.selectedCardRect)
        self.clearSelections()
        self.selectedCardRect = None
        self.selectedCardType = None
        self.selectedCardStack = None

    def setCardSelection(self, stackType, cardStack, cardRect, x, y):
        self.setSelections(x, y)
        self.selectedCardRect = cardRect
        self.selectedCardType = stackType
        self.selectedCardStack = cardStack

    #-----------------------------------------------------

    def moveCard(self, srcStack, dstStack):
        self.moveCardNew(srcStack, dstStack)

    #-----------------------------------------------------

    def moveCardNew(self, srcStack, dstStack):

        if (srcStack == dstStack):
            return

        srcCardVal, srcSuit, srcSuitColour = srcStack.getCardValueSuitColour(
            -1)
        dstCardVal, dstSuit, dstSuitColour = dstStack.getCardValueSuitColour(
            -1)
        logging.info("moveCard: move %s %s to %s %s" %
                     (SUITNAMES[srcSuit], CARDNAMES[srcCardVal],
                      SUITNAMES[dstSuit], CARDNAMES[dstCardVal]))

        # Logik:
        self.undoStack.append((srcStack, dstStack))

        x, y, w, h = srcStack.getTopCardRect().getLeftTopWidthHeight()
        fromX, fromY = x, y
        toX, toY = dstStack.getNextTopCardLeftTop()

        card = srcStack.popCard()
        dstStack.pushCard(card)

        # Visualisierung vorbereiten:
        mt = MoveCardTask('MoveCardTask', self.drawingArea, card, fromX, fromY,
                          toX, toY)
        self.taskQ.taskInsert(mt)

    #-----------------------------------------------------

    def moveCardOld(self, srcStack, dstStack):
        # Move a card from one stack to another

        # Das ist das Original von Maemo. Wird noch benutzt, um den Anfangszustand
        # aufzubauen, ohne Animation.

        if (srcStack == dstStack):
            return

#		srcCardVal, srcSuit, srcSuitColour = srcStack.getCardValueSuitColour(-1)
#		dstCardVal, dstSuit, dstSuitColour = dstStack.getCardValueSuitColour(-1)
#		logging.info("moveCard: move %s %d to %s %d" % (SUITNAMES[srcSuit], srcCardVal, SUITNAMES[dstSuit], dstCardVal))

        self.undoStack.append((srcStack, dstStack))

        x, y, w, h = srcStack.getTopCardRect().getLeftTopWidthHeight()
        fromX, fromY = x, y
        toX, toY = dstStack.getNextTopCardLeftTop()

        card = srcStack.popCard()
        srcStack.drawTopCard(self.drawingArea)

        #self.animateCardMove(card, toX, toY)

        dstStack.pushCard(card)
        dstStack.drawTopCard(self.drawingArea)

    def clearSelections(self):
        for i in range(len(self.freecellStacks)):
            self.freecellStacks[i].clearSelection()
        for i in range(len(self.acesStacks)):
            self.acesStacks[i].clearSelection()
        for i in range(len(self.mainCardStacks)):
            self.mainCardStacks[i].clearSelection()

    def setSelections(self, x, y):
        for i in range(len(self.freecellStacks)):
            self.freecellStacks[i].setSelection(x, y)
        for i in range(len(self.acesStacks)):
            self.acesStacks[i].setSelection(x, y)
        for i in range(len(self.mainCardStacks)):
            self.mainCardStacks[i].setSelection(x, y)

    def xyToCardStackInfo(self, x, y):
        # Determine the card/stack at a given (x,y); return the type, rect, cardStack of the target
        hitType = None
        hitRect = None
        hitStack = None

        if (self.freeCellsRect.enclosesXY(x, y)):
            for i in range(len(self.freecellStacks)):
                hitStack = self.freecellStacks[i]
                if (hitStack.enclosesXY(x, y)):
                    hitRect = self.freecellStacks[i].getRect()
                    hitType = FREECELL_TYPE
                    break

        elif (self.acesRect.enclosesXY(x, y)):
            for i in range(len(self.acesStacks)):
                hitStack = self.acesStacks[i]
                if (hitStack.enclosesXY(x, y)):
                    hitRect = self.acesStacks[i].getRect()
                    hitType = ACE_TYPE
                    break

        else:
            for i in range(len(self.mainCardStacks)):
                hitStack = self.mainCardStacks[i]
                if (hitStack.enclosesXY(x, y)):
                    hitRect = self.mainCardStacks[i].getTopCardRect()
                    hitType = REGULAR_TYPE
                    break

        return (hitType, hitRect, hitStack)

    def drawingAreaClick(self, instance, value):
        #print ('touch down',value)
        x = value[0]
        y = self.drawingArea.size[1] - value[1]
        #print ('touch down',x,y)
        self.button_press_event(instance, x, y)

    #??
    def button_press_event(self, widget, x, y):
        # def button_press_event_cb(self, widget, event):
        # This is the big, ugly one-- all the gameplay rules are implemented here...

        #	x, y = event.x, event.y
        #!!
        dstType, dstRect, dstStack = self.xyToCardStackInfo(x, y)
        #print('button_press_event',dstType,dstRect,dstStack)

        if (dstType == None):
            # Didn't click on a valid target, so clear the previous click selection and bail
            self.clearCardSelection()

        elif (self.selectedCardType == None):

            if not (self.taskQ.taskQsAreEmpty()):
                return True

            # There was no previous selection, so select target (if valid) and bail
            if (dstStack.getNumCards() > 0):
                if (not self.smartPlayMode):
                    self.setCardSelection(dstType, dstStack, dstRect, x, y)

                else:
                    # Move the card to an ace stack, main stack, or free cell stack, if possible
                    movedCard = False
                    origDstType, origDstStack, origDstRect = dstType, dstStack, dstRect

                    # Call it srcStack to make this clearer
                    srcStack = dstStack
                    srcCardVal, srcCardSuit, srcCardSuitColour = srcStack.getCardValueSuitColour(
                        -1)

                    # Try the aces stack first
                    dstStack = self.acesStacks[srcCardSuit]
                    dstCardVal, dstSuit, dstSuitColour = dstStack.getCardValueSuitColour(
                        -1)

                    if (dstCardVal == srcCardVal - 1):
                        self.moveCard(srcStack, dstStack)
                        self.clearCardSelection()
                        movedCard = True

                    if (movedCard == False):
                        # Try a non-empty main stack
                        for dstStack in self.mainCardStacks:
                            dstCardVal, dstSuit, dstSuitColour = dstStack.getCardValueSuitColour(
                                -1)
                            if (dstCardVal >= 0
                                    and dstCardVal == srcCardVal + 1
                                    and dstSuitColour != srcCardSuitColour):
                                self.moveCard(srcStack, dstStack)
                                self.clearCardSelection()
                                movedCard = True
                                break

                    if (movedCard == False):
                        # Try an empty main stack or a freecell stack
                        tmpStacks = self.mainCardStacks + self.freecellStacks
                        for dstStack in tmpStacks:
                            if (dstStack.getNumCards() <= 0):
                                self.moveCard(srcStack, dstStack)
                                self.clearCardSelection()
                                movedCard = True
                                break

                    if (movedCard == False):
                        self.setCardSelection(dstType, origDstStack, dstRect)
        else:
            if not (self.taskQ.taskQsAreEmpty()):
                return True

            # A card is currently selected, so see if it can be moved to the target
            srcStack = self.selectedCardStack
            srcNumCards = srcStack.getNumCards()
            srcCardVal, srcSuit, srcSuitColour = srcStack.getCardValueSuitColour(
                -1)
            dstNumCards = dstStack.getNumCards()
            dstCardVal, dstSuit, dstSuitColour = dstStack.getCardValueSuitColour(
                -1)
            dstSrcDelta = dstCardVal - srcCardVal
            logging.debug(
                "srcSuit = %d, srcSuitColour = %d, srcCardVal = %d, srcNumCards = %d"
                % (srcSuit, srcSuitColour, srcCardVal, srcNumCards))
            logging.debug(
                "dstSuit = %d, dstSuitColour = %d, dstCardVal = %d, dstSrcDelta = %d"
                % (dstSuit, dstSuitColour, dstCardVal, dstSrcDelta))

            numFreeCells = 0
            for cardStack in self.freecellStacks:
                if (cardStack.getNumCards() <= 0):
                    numFreeCells += 1

            runLength = 0
            for i in range(srcNumCards):
                cardVal, cardSuit, cardSuitColour = srcStack.getCardValueSuitColour(
                    srcNumCards - i - 1)
                logging.debug(
                    "card #%d: cardVal = %d, cardSuit = %d, cardSuitColour = %d"
                    % (srcNumCards - i - 1, cardVal, cardSuit, cardSuitColour))
                if (cardVal == srcCardVal + i
                        and cardSuitColour == (srcSuitColour + i) % 2):
                    runLength += 1
                else:
                    break

            suitColoursWork = (srcSuitColour == (
                dstSuitColour + dstSrcDelta) % 2)
            srcRunMeetsDst = dstSrcDelta > 0 and runLength >= dstSrcDelta

            logging.info(
                "dstSrcDelta = %d, numFreeCells = %d, runLength = %d, suitColoursWork = %s"
                % (dstSrcDelta, numFreeCells, runLength, suitColoursWork))

            if (dstType == FREECELL_TYPE):
                # Move selected card to a free cell, if it is open
                if (dstNumCards <= 0 or self.debugMode):
                    self.moveCard(srcStack, dstStack)

            elif (dstType == ACE_TYPE):
                # Move selected card to an ace stack, if it matches suit and is in order
                logging.debug(
                    "srcSuit=%d, dstSuit=%d, dstNumCards=%d, srcCardVal=%d, dstCardVal=%d"
                    % (srcSuit, dstSuit, dstNumCards, srcCardVal, dstCardVal))
                if srcSuit == dstSuit and srcCardVal == dstCardVal + 1:
                    self.moveCard(srcStack, dstStack)

            elif (dstNumCards <= 0 and runLength <= 1):
                # Move a single card to an empty stack
                self.moveCard(srcStack, dstStack)

            elif (dstNumCards <= 0 and runLength > 1):
                dialogResult = MOVE_CARD_ID

                # Diese Auswahl ist unnoetig und eher stoerend. - weggelassen. Wir
                # transferieren immer soviele wie moeglich. Falls das im Spielverlauf
                # nicht gewuenscht ist, kann der Spieler immer noch ueber die freien
                # Zellen mit Einzelkarten operieren. Das braucht gleichviel Klicks, aber
                # die nervige Rückfrage, welche den Spielfluss stört, entfällt so.

                if (numFreeCells > 0):
                    # Move a card or a column to an empty stack?
                    #					self.cardOrColumnDialog.show()
                    #					dialogResult = self.cardOrColumnDialog.run()
                    #					self.cardOrColumnDialog.hide()
                    dialogResult = 'multi'

                # Repaint the mess made by the dialog box


#				gtk.gdk.window_process_all_updates()
#				x, y, w, h = 0, 0, self.windowWidth, self.windowHeight
#				self.drawingArea.window.draw_drawable(self.drawingArea.get_style().fg_gc[gtk.STATE_NORMAL], self.offscreenPixmap, x, y, x, y, w, h)

                if (dialogResult == MOVE_CARD_ID):
                    # Just move a single card after all
                    self.moveCard(srcStack, dstStack)
                else:
                    # Nope, move the run
                    tempStacks = []
                    for i in range(min(numFreeCells, runLength - 1)):
                        for j in range(NUMFREECELLS):
                            if (self.freecellStacks[j].getNumCards() <= 0):
                                self.moveCard(srcStack, self.freecellStacks[j])
                                tempStacks.insert(0, self.freecellStacks[j])
                                break
                    self.moveCard(srcStack, dstStack)
                    for s in tempStacks:
                        self.moveCard(s, dstStack)

            elif (srcRunMeetsDst and suitColoursWork
                  and numFreeCells >= dstSrcDelta - 1):
                # Move a column onto another card (column could be just a single card, really)
                logging.debug("Column move")
                tempStacks = []
                for i in range(dstSrcDelta - 1):
                    for j in range(NUMFREECELLS):
                        if (self.freecellStacks[j].getNumCards() <= 0):
                            self.moveCard(srcStack, self.freecellStacks[j])
                            tempStacks.insert(0, self.freecellStacks[j])
                            break
                self.moveCard(srcStack, dstStack)
                for s in tempStacks:
                    self.moveCard(s, dstStack)

            # Clear selection
            self.clearCardSelection()

            logging.debug(
                "-----------------------------------------------------------------------------"
            )

        self.checkGameOver()
        return True


class FreeCellApp(App):
    def __init__(self):
        super(FreeCellApp, self).__init__()
        self.freeCell = None
        self.root = None

    def on_start(self):
        logging.info("FreeCellApp: on_start")

        newgame = not self.freeCell.read_current_game()
        self.freeCell.setupCards(newgame)
        self.freeCell.initMoves()
        pass

    def on_stop(self):
        logging.info("FreeCellApp: on_stop")
        if self.freeCell is not None:
            self.freeCell.save_game()

    def on_pause(self):
        logging.info("FreeCellApp: on_pause")
        if self.freeCell is not None:
            self.freeCell.save_game()
        return True

    def on_resume(self):
        logging.info("FreeCellApp: on_resume")
        pass

    def build(self):
        logging.info("FreeCellApp: build()")
        self.freeCell = FreeCell()
        self.root = self.freeCell.mainWindow        
        return self.root


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    try:
        os.mkdir('.freecell4maemo')
    except OSError:
        pass

    logging.info("FreeCellApp: before run()")
    FreeCellApp().run()
    logging.info("FreeCellApp: after run()")
