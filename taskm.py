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

from kivy.properties import *
from kivy._event import *
from kivy.clock import Clock


class Task(EventDispatcher):
    done = BooleanProperty(False)

    def __init__(self, name):
        super(Task, self).__init__()
        self.done = False
        self.name = name

    def start(self):
        #print ('start of ',self.name)
        self.done = False

    def stop(self):
        #print ('stop of ',self.name)
        self.done = True

    def on_done(self, instance, value):
        #print ('on_done',instance,value)
        pass


class TaskQ(EventDispatcher):
    waitQ = ListProperty([])
    runQ = ListProperty([])

    def __init__(self, **kwargs):
        super(TaskQ, self).__init__(**kwargs)
        self.waitQ = []
        self.waitQlen = 0
        self.runQ = []
        self.runQlen = 0
        self.runQmax = 10
        # e.g.
        self.runSeq = 0.13  # e.g.

    def scheduleNext(self, dt):
        if (self.waitQlen > 0):
            if (self.runQlen < self.runQmax):
                #print ('scheduleNext')
                self.runQ.append(self.waitQ[0])
                del self.waitQ[0]

        if (self.waitQlen > 0 or self.runQlen > 0):
            Clock.schedule_once(self.scheduleNext, self.runSeq)

    def on_runQ(self, instance, value):
        lastlen = self.runQlen
        self.runQlen = len(self.runQ)

        if (self.runQlen > lastlen):
            self.runQ[-1].bind(done=self.taskStopped)
            self.runQ[-1].start()

    def on_waitQ(self, instance, value):
        lastlen = self.waitQlen
        self.waitQlen = len(self.waitQ)

        if (self.waitQlen > 0 and self.runQlen == 0):
            self.scheduleNext(0)

    def taskQsAreEmpty(self):
        return (self.waitQlen == 0 and self.runQlen == 0)

    def taskInsert(self, task):
        print('taskInsert called', task)
        self.waitQ.append(task)

    def taskStopped(self, instance, value):
        if (value == True):
            idx = 0
            while (idx < self.runQlen):
                if (self.runQ[idx] is instance):
                    break
                idx += 1

            if (idx < self.runQlen):
                print('taskStopped', instance, 'index', idx)
                del self.runQ[idx]
            else:
                print('taskStopped: index out of range!')
