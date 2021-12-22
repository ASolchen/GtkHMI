# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Jason Engman <jengman@testtech-solutions.com>
# Copyright (c) 2021 Adam Solchenberger <asolchenberger@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
import time
from .const import DATATYPES
from typing import Any, Callable, Optional


class Connection(object):
  def __init__(self, connection_manager, idx):
    self.id = idx
    self.app = connection_manager.app
    self.connection_manager = connection_manager
    self.db_manager = connection_manager.db_manager
    self.tags = {}
  
  def update_tag(self, tag: str, val: Any, timestamp: float=time.time()):
    dt = self.tags[tag]['DataType']
    py_type = DATATYPES[dt]['Py_type'] # try to update tag to its python type
    val = py_type(val)
    self.tags[tag].update({'Value': val, 'Timestamp': timestamp})

  def read(self, tags: list)->dict:
    return {}

  def write(self, tag: str, val: Any)->None:
    return None
