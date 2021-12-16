# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Jason Engman <jengman@testtech-solutions.com>
# Copyright (c) 2021 Adam Solchenberger <asolchenberger@testtech-solutions.com>
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
import re
import time
from typing import Any, Callable, Optional
from backend.managers.connection_classes.base import Connection
from backend.managers.connection_classes.const import DATATYPES


class HMI_Connection(Connection):
    
  def read(self, tags: list)->dict:
    results = {}
    ts = time.time()
    for tag in tags:
      if tag == "Second":
        results[tag] =  {"Value": time.localtime().tm_sec, "Timestamp": ts, "DataType": "INT"}
        break
      if tag == "Minute":
        results[tag] =  {"Value": time.localtime().tm_min, "Timestamp": ts, "DataType": "INT"}
        break
      if tag == "Hour":
        results[tag] =  {"Value": time.localtime().tm_sec, "Timestamp": ts, "DataType": "INT"}
        break
      if tag == "Day":
        results[tag] =  {"Value": time.localtime().tm_mday, "Timestamp": ts, "DataType": "INT"}
        break
      if tag == "Month":
        results[tag] =  {"Value": time.localtime().tm_mon, "Timestamp": ts, "DataType": "INT"}
        break
      if tag == "Year":
        results[tag] =  {"Value": time.localtime().tm_year, "Timestamp": ts, "DataType": "INT"}
        break
      if tag == "blinkSlow":
        results[tag] =  {"Value": bool((time.localtime().tm_sec / 2)%2), "Timestamp": ts, "DataType": "BOOL"}
        break
      if tag == "blinkFast":
        results[tag] =  {"Value": bool(time.localtime().tm_sec%2), "Timestamp": ts, "DataType": "BOOL"}
        break
      if tag in self.tags:
        results[tag] = self.tags[tag] #dynamic tags?
        break
      res = self.connection_manager.db_manager.get_rows("Tags", ["Value", "DataType"], match_col="Tag", match=tag)
      if len(res):
        val = DATATYPES[res[0]["DataType"]]["Py_type"](res[0]["Value"])
        results[tag] = {"Value": val, "Timestamp": ts, "DataType": res[0]["DataType"]}
    return results

  def write(self, address: str, val: Any, datatype:[Optional]="REAL")->None:
    #write a single tag by address to the tag subscriptions
    tag_update ={self.id:    
      {address: {"Value": str(val), "Timestamp": time.time(), "DataType": datatype}
      }
    }
    #self.connection_manager.db_manager.update_tag_values(tag_update)
    self.connection_manager.db_manager.set_tag_val_by_name(address,val)

