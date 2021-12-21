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
import os
import gi, time
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from backend.managers.database_models.project_database import ProjectDatabase
from backend.managers.database_models.subscription_database import SubscriptionDb


class DatabaseManager(GObject.Object):
  def __init__(self, app):
    super(DatabaseManager, self).__init__()
    self.app = app
    self.subcription_db = SubscriptionDb() #in-memory database for now, could be remote server
    self.project_db = ProjectDatabase()
  
  def open(self, path):
    self.project_db.open(path)
  def write_sqlite_db(self, path):
    pass
   
  def get_rows(self, *args):
    return []

  def copy_table(self,table):
    pass

  def table_exists(self, table):
    return False
  
  def item_exists(self,table,col,item):
    return False
  
  def get_row_by_id(self, table, match_col=None, match=None, order_by=None, order_desc=False):
    pass

  def get_tag_id(self, tagname):
    res = None
    return res

  def get_tag_val_by_id(self, idx):
    pass

  def set_tag_val_by_name(self, tag, val):
    pass
    
  def clear_tag_subs(self, subscriber_id):
    pass

  def add_subscription(self, subscriber_id: str, connection_id: int, tag: str, address: str, datatype:str="REAL"):
    pass    
    
  def get_sub_vals(self, subscriber_id, tags):
    tag_dict = {}
    return tag_dict

  def update_tag_values(self, tag_updates: dict):
    #{1: {'Second': {'DataType': 'INT', 'Timestamp': 1613349742.0320673, 'Value': 22}}
    
    pass


  
  def ack_all_events(self):
    pass
  
  def ack_sel_events(self,ID):
    pass
  
  def set_db_val_by_id(self, db,column, w_id,val):
    pass
  
  
  def add_default_param_item(self,table,id_num):
    pass
  
  def add_item_to_table(self, db, columns, val):
    pass

  def add_item_ext_table(self,db, table,columns, val):
    pass
  
  def delete_item_from_table(self, tbl, column, val):
    pass
 
  def delete_item_ext_table(self,db, tbl , column, val):
    #dest_path = "public/mill.db"
    pass

















