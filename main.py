#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
##---------------------------------------------------------------------------##

# Freecell4Maemo, Copyright 2008, Roy Wood
#                 Copyright 2010, Justin Quek
# Kivy port,      Copyright 2016, Lukas Beck

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

import os
from src.freecell import FreeCellApp, STORAGESUBDIR

if __name__ == "__main__":

    try:
        os.mkdir(STORAGESUBDIR)
    except OSError:
        pass

    FreeCellApp().run()
