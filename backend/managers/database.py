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
import sqlite3
from io import StringIO
from sqlite3 import Error
import re




from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql.sqltypes import Float, Numeric


AppSettingsBase = declarative_base()
class WidgetsDatabase(AppSettingsBase):
    __tablename__ = 'widgets'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('widgets.id')) # integer of parent, if NULL then top level (Display)
    widget_class = Column(String) # widget type
    build_order = Column(Integer)
    x = Column(Integer)
    y = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    description = Column(String)
    global_reference = Column(Boolean) # if True, is a global parent and all of its children are part of a global assembly



class WidgetDb():
  def __init__(self) -> None:
    self.widgets_model = WidgetsDatabase

  def __enter__(self):
    engine = create_engine(f"sqlite:///{os.path.join(os.path.dirname(__file__), 'test_project.db')}") #should create a .db file next to this one
    AppSettingsBase.metadata.create_all(engine) #creates all the tables above
    Session = sessionmaker(bind=engine)
    self.session = Session()
    return self
  
  def __exit__(self, *args):
    print(args)
    self.session.close()


with WidgetDb() as db:
  idx = None
  for x in range(10):
    row = db.widgets_model(parent_id=idx, widget_class='Base', x=10, y=10, width=10, height=10, description="Some description")
    db.session.add(row)
    db.session.commit()
    idx = row.id



class DatabaseManager(GObject.Object):
  def __init__(self, app):
    super(DatabaseManager, self).__init__()
    self.app = app
    self.mem_db = None

  def init_sqlite_db(self, path):
      # Read database to tempfile
      con = sqlite3.connect(path)
      tempfile = StringIO()
      for line in con.iterdump():
          tempfile.write(u'%s\n' % line)
      con.close()
      tempfile.seek(0)
      # Create a database in memory and import from tempfile
      mem_db = sqlite3.connect(":memory:",check_same_thread=False)
      mem_db.cursor().executescript(tempfile.read())
      mem_db.commit()
      mem_db.row_factory = sqlite3.Row
      self.mem_db = mem_db
  
  @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST, return_type=bool,
                    arg_types=(object,),
                    accumulator=GObject.signal_accumulator_true_handled)
  def save_event(self, msg):
    self.add_item_to_table('EventLog','(Message)',[msg])
    #pass signal up to app for display\

  def write_sqlite_db(self, path):
    # Write database to file
    
    tempfile = StringIO()
    for line in self.mem_db.iterdump():
      tempfile.write(u"{}\n".format(line))
    tempfile.seek(0)
    with open(path, "w") as fp: #overwrite if old file exists
      fp.write("")
    con = sqlite3.connect(path)
    con.cursor().executescript(tempfile.read())
    con.commit()
    con.close()
   
  def copy_table(self,table):
    #this function copies the values out of the memory database and moves them into the mill.db database
    #This function does not insert new rows only copies
    src = self.mem_db.cursor()
    src.execute('SELECT * FROM [{tab}]'.format(tab=table))
    #handle to destination table
    dest_path = "public/mill.db"
    #dest = sqlite3.connect(dest_path).cursor()
    dest = sqlite3.connect(dest_path)
    dest.row_factory = sqlite3.Row
    #Get IDs in destination table to see if all items from copy table exist in dest table
    dest_ids = dest.execute('SELECT ID FROM [{tab}]'.format(tab=table))
    avail_dest_ids = []
    for i in dest_ids.fetchall():
      avail_dest_ids.append(i['ID'])
    query = None
    for row in src.fetchall():
      #collect header columns from table
      w_id = row['ID']
      col_names = ''
      columns = '('
      values = []
      val = '('
      #if ID already exists in table to copy then update values
      if w_id in avail_dest_ids:
        for k in row.keys():
          if k != 'ID':
            columns += k +','
            col_names += k + ' = ?, '
            values.append(row[k])
            val += "'"+str(row[k]) +"',"
        col_names = col_names[:-2]  #remove last ',' from string
        columns = columns[:-1]
        val = val[:-1]
        columns += ')'
        val += ')'
        query = "UPDATE [{t}] SET {values} WHERE [ID] = '{id}'".format(t=table,values=col_names,id = w_id)
        #print(query,values)
        dest.execute(query,values)
      #If ID doesn't exist in table then insert the new row
      else:
        for k in row.keys():
          columns += k +','
          col_names += k + ' = ?, '
          values.append(row[k])
          val += "'"+str(row[k]) +"',"
        col_names = col_names[:-2]  #remove last ',' from string
        columns = columns[:-1]
        val = val[:-1]
        columns += ')'
        val += ')'
        query = "INSERT INTO [{t}] {col} VALUES {matches}".format(t=table,col=columns,matches = val )
        dest.execute(query)
    dest.commit()
    dest.close()


  '''
  def write_db_row(self, db,column, w_id,val):
    w_id = '1'
    val = '222'
    column = 'DefaultValue'
    dest_path = "public/mill.db"
    dest = sqlite3.connect(dest_path)
    dest.row_factory = sqlite3.Row
    try:
      query = "UPDATE [{t}] SET [{col}] = ? WHERE [ID] = ?".format(t=db,col=column)
      dest.execute(query, [val,w_id])
      dest.commit()
    except Error as e:
      raise(e)
    return
  '''
  def table_exists(self, table):
    try:
      c = self.mem_db.cursor()
      sql = 'SELECT * FROM [{t}] LIMIT 1;'.format(t=table)
      c.execute(sql, [])         
      return True
    except Error as e:
      return False
  
  def item_exists(self,table,col,item):
    try:
      c = self.mem_db.cursor()
      sql = 'SELECT * FROM [{t}] WHERE {column} = "{match}" LIMIT 1;'.format(t=table,column = col,match = str(item))
      c.execute(sql, [])
      val = c.fetchall() 
      if not val:
        return False
      else:     
        return True
    except Error as e:
      return False

  def run_query(self, sql, args=[]):
    try:
      c = self.mem_db.cursor()
      c.execute(sql, args)
      return c.fetchall()
    except Error as e:
      raise(e)

  def get_rows(self, table, params, match_col=None, match=None, order_by=None, order_desc=False):
    try:
      c = self.mem_db.cursor()
      sql = 'SELECT {p_list} FROM [{table}]'.format(p_list=", ".join(params),
      table=table)
      if match_col and match:
        sql += ' WHERE "{match_col}" = "{match}"'.format(match_col=match_col, match=match)
      if order_by:
        direction = "DESC" if order_desc else "ASC"
        sql += ' ORDER BY "{col}" {dir}'.format(col=order_by, dir=direction) 
      sql += ";"
      rows = self.run_query(sql)
      results = []
      for idx, row in enumerate(rows):
        results.append({})
        for p_id, param in enumerate(params):
          results[idx][param] = row[p_id]          
      return(results)
    except Error as e:
      raise(e)
  
  def get_row_by_id(self, table, match_col=None, match=None, order_by=None, order_desc=False):
    try:
      c = self.mem_db.cursor()
      sql = 'SELECT * FROM [{table}]'.format(table=table)
      if match_col and match:
        sql += ' WHERE "{match_col}" = "{match}"'.format(match_col=match_col, match=match)
      if order_by:
        direction = "DESC" if order_desc else "ASC"
        sql += ' ORDER BY "{col}" {dir}'.format(col=order_by, dir=direction) 
      sql += ";"
      rows = self.run_query(sql)
      params = rows[0].keys()
      results = []
      for idx, row in enumerate(rows):
        results.append({})
        for p_id, param in enumerate(params):
          results[idx][param] = row[p_id]          
      return(results)
    except Error as e:
      raise(e)

  def get_tag_id(self, tagname):
    res = None
    try:
      c = self.mem_db.cursor()
      c.execute('SELECT ID FROM [Tags] WHERE Tag=?', [tagname])
      res = c.fetchone()
      if res:
        res = res[0]
    except Error as e:
      raise(e)
    return res

  def get_tag_val_by_id(self, idx):
    res = None
    try:
      c = self.mem_db.cursor()
      c.execute('SELECT Value FROM [Tags] WHERE ID=?', [idx])
      res = c.fetchone()
    except Error as e:
      raise(e)
    return res[0]

  def set_tag_val_by_name(self, tag, val):
    try:
      c = self.mem_db.cursor()
      c.execute('UPDATE [Tags] SET [Value]=? WHERE [Tag]=?', [val, tag])
    except Error as e:
      raise(e)
    return
    
  def clear_tag_subs(self, subscriber_id):
    try:
      c = self.mem_db.cursor()
      if not self.table_exists("TagSubscriptions"):
        c.execute("""CREATE TABLE "TagSubscriptions" (
          "ID"	INTEGER PRIMARY KEY AUTOINCREMENT,
          "Tag"	TEXT NOT NULL,
          "Subscriber"	TEXT,
          "ConnectionID"	INTEGER NOT NULL,
          "Address"	TEXT,
          "Value"	TEXT,
          "Timestamp"	NUMERIC,
          "DataType"	TEXT,
          CONSTRAINT fk_connectionID
            FOREIGN KEY("ConnectionID")
            REFERENCES "Connections"("ID")
            ON DELETE CASCADE
        )""")
        self.mem_db.commit()
      c.execute("DELETE FROM TagSubscriptions WHERE 'Subscriber'=?", [subscriber_id]) # clear all with this subcriber
      self.mem_db.commit()
    except Error as e:
      raise(e)

  def add_subscription(self, subscriber_id: str, connection_id: int, tag: str, address: str, datatype:str="REAL"):
    c = self.mem_db.cursor()
    c.execute("INSERT INTO TagSubscriptions ('Tag','ConnectionID','Address','Subscriber', 'DataType') VALUES (?,?,?,?,?)",
    [tag, connection_id,address,subscriber_id, datatype]) 
    self.mem_db.commit()    
    
  def get_sub_vals(self, subscriber_id, tags):
    tag_list = []
    if not self.table_exists("TagSubscriptions"):
      return
    if 1: #try
      # Add new tags here
      conx_lookup = self.get_rows("Connections", ["ID", "Connection"])
      if not len(conx_lookup):
        msg = 'No connections defined'
        self.save_event(msg)
        return
      for row in conx_lookup:
        for tag in tags:
          if re.match("\[{}\]".format(row["Connection"]), tag):
            sql = 'SELECT "Tag", "ConnectionID", "Display" FROM [TagSubscriptions] WHERE "Tag"=? AND "ConnectionID"=? AND "Subscriber"=?;'
            c = self.mem_db.cursor()
            c.execute(sql, [tag, row["ID"], subscriber_id])
      #Now get tags
      tag_dict = {}
      for tag in tags:
        sql = 'SELECT "Tag", "Value", "Timestamp" FROM [TagSubscriptions] WHERE "Tag"=? AND "Subscriber"=?;'
        c = self.mem_db.cursor()
        c.execute(sql, [tag, subscriber_id])
        res = c.fetchone()
        if res:
          tag_dict[res["Tag"]] = {"Value": res["Value"], "Timestamp": res["Timestamp"]}
          tag_list.append(res["Tag"])
    else: #except Error as e:
      raise(e)
    return tag_dict

  def update_tag_values(self, tag_updates: dict):
    #{1: {'Second': {'DataType': 'INT', 'Timestamp': 1613349742.0320673, 'Value': 22}}
    c = self.mem_db.cursor()
    for conxId in tag_updates:
      for address in tag_updates[conxId]:
        params = [str(tag_updates[conxId][address]["Value"]),
         tag_updates[conxId][address]["Timestamp"],
         tag_updates[conxId][address]["DataType"],
         conxId,
         address]
        c.execute("""UPDATE [TagSubscriptions] SET [Value]=?, [Timestamp]=?, [DataType]=?
          WHERE ConnectionID = ? AND [Address] = ?;""",
         params)
    self.mem_db.commit()
    test = self.get_rows("TagSubscriptions", ["Tag", "Address", "Value", "Timestamp", "DataType"])
    pass

  def update_db_row(self, table, data):
    #data = {'ID': 'gcode-lbl', 'ParentID': 'command-box', 'X': 10, 'Y': 15, 'Width': 200, 'Height': 50, 'Class': 'label', 'Description': '', 'Styles': 'font-30,text-color,font-bold', 'GlobalReference': '', 'BuildOrder': ''}
    c = self.mem_db.cursor()
    w_id = data["ID"]
    col_names = ''
    columns = '('
    values = []
    val = '('
    for k in data.keys():
        if k != 'ID':
          columns += k +','
          col_names += k + ' = ?, '
          values.append(data[k])
          val += "'"+str(data[k]) +"',"
    col_names = col_names[:-2]  #remove last ',' from string
    columns = columns[:-1]
    val = val[:-1]
    columns += ')'
    val += ')'
    query = "UPDATE [{t}] SET {values} WHERE [ID] = '{id}'".format(t='Widgets',values=col_names,id = w_id)
    #print('Update_db_row',query,values)    
    c.execute(query,values)
    self.mem_db.commit()
  
  def ack_all_events(self):
    try:
      c = self.mem_db.cursor()
      c.execute("UPDATE AlarmsEvents SET 'AckState' = ?, AckTimestamp = ? WHERE State=?",(True,str(time.time()),True))
      self.mem_db.commit()
    except Error as e:
      raise(e)
  
  def ack_sel_events(self,ID):
    try:
      c = self.mem_db.cursor()
      c.execute("UPDATE AlarmsEvents SET 'AckState' = ?, AckTimestamp = ? WHERE State=? AND ID = ?",(True,str(time.time()),True,ID))
      self.mem_db.commit()
    except Error as e:
      raise(e)
  
  def set_db_val_by_id(self, db,column, w_id,val):
    try:
      query = "UPDATE [{t}] SET [{col}] = ? WHERE [ID] = ?".format(t=db,col=column)
      c = self.mem_db.cursor()
      c.execute(query, [val,w_id])
      self.mem_db.commit()
    except Error as e:
      raise(e)
    return
  
  
  def add_default_param_item(self,table,id_num):
      try:
        query = "INSERT INTO [{tbl}] ('ID') VALUES ({val});".format(tbl = table,val = int(id_num))
        c = self.mem_db.cursor()
        c.execute(query) 
        self.mem_db.commit()
        #return last inserted row
        return c.lastrowid
      except Error as e:
        raise(e)
  
  def add_item_to_table(self, db, columns, val):
    value_str = '('
    for i in range(len(val)):
      value_str += '?'
      if len(val)>=1 and (i+1) != len(val): 
        value_str+=','
    value_str += ')'
    try:
      query = "INSERT INTO [{t}] {col} VALUES {values}".format(t=db,col=columns,values = value_str)
      c = self.mem_db.cursor()
      c.execute(query, val) 
      self.mem_db.commit()
      #return last inserted row
      return c.lastrowid
    except Error as e:
      raise(e)

  def add_item_ext_table(self,db, table,columns, val):
    #dest_path = "public/mill.db"
    dest_path = db
    dest = sqlite3.connect(dest_path)
    dest.row_factory = sqlite3.Row
    value_str = '('
    for i in val:
      value_str += "'"+str(i) +"',"
    value_str = value_str[:-1]  #remove extra comma
    value_str += ')'
    try:      
      query = "INSERT INTO [{t}] {col} VALUES {matches}".format(t=table,col=columns,matches = value_str )
      dest.execute(query)
      dest.commit()
      dest.close()
    except Error as e:
      raise(e)
  
  def delete_item_from_table(self, tbl, column, val):
    try:
      query = "DELETE FROM [{t}] WHERE {col} = {match}".format(t=tbl,col=column,match = val)
      c = self.mem_db.cursor()
      c.execute(query) 
      self.mem_db.commit()
    except Error as e:
      raise(e)
 
  def delete_item_ext_table(self,db, tbl , column, val):
    #dest_path = "public/mill.db"
    dest_path = db
    dest = sqlite3.connect(dest_path)
    dest.row_factory = sqlite3.Row
    try:      
      query = "DELETE FROM [{t}] WHERE {col} = {match}".format(t=tbl,col=column,match = val)
      c = dest.cursor()
      dest.execute(query)
      dest.commit()
      dest.close()
    except Error as e:
      raise(e)

















