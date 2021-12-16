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
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
import re
import time
from .const import DATATYPES
from .base import Connection
from .hmi import HMI_Connection
from .grbl import Grbl_Connection
from .ethernet_ip import EthernetIP_Connection
from .modbus import ModbusRTU_Connection, ModbusTCP_Connection
from .ads import ADS_Connection
#from .opc_ua import OPCUA_Connection
from typing import Any, Callable, Optional

class ConnectionManager(GObject.Object):
  def __init__(self, app):
    super(ConnectionManager, self).__init__()
    self.app = app
    ports = self.get_serial_ports()
    self.db_manager = app.db_manager
    self.connection_type_enum ={
      1: HMI_Connection,
      2: ModbusTCP_Connection,
      3: ModbusRTU_Connection,
      4: EthernetIP_Connection,
      5: ADS_Connection,
      6: Grbl_Connection,
      #7: OPCUA_Connection,
    }

    self.poll_thread = None
    self.connections = {}
    self.signals = [app.connect("db_ready", self.start), ]

  @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST, return_type=bool,
                    arg_types=(object,),
                    accumulator=GObject.signal_accumulator_true_handled)
  def tag_update(self, tag_update):
    pass #put something here to run on signal

  @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST, return_type=bool,
                    arg_types=(object,),
                    accumulator=GObject.signal_accumulator_true_handled)
  def new_event(self, msg):
    self.app.display_event(msg)
    #pass signal up to app for display

  def start(self, app, db_manager):
    #this is called once the database is ready to be used
    self.db_manager = db_manager
    #connect to controllers here
    res = self.db_manager.get_rows("Connections", ["ID","ConnectionTypeID", "Connection"])
    for conx in res:
      self.connections[conx["Connection"]] = self.connection_type_enum[conx["ConnectionTypeID"]](self, conx["ID"])
    self.connections["APP"] = self.app # gives hmi scripts access to app, tread lightly
    GObject.timeout_add(500, self.update_sub_tags)

  def update_sub_tags(self):
    #poll interval for the connection manager to ask the connections for tag updates
    if not self.db_manager.table_exists("TagSubscriptions"):
      return []
    connection_updates = {}
    rows = self.db_manager.run_query("SELECT [ConnectionID] FROM [TagSubscriptions] GROUP BY [ConnectionID];")
    for row in rows:
      conx_id= row["ConnectionID"]
      conx_rows = self.db_manager.get_rows("Connections", ["Connection"], match_col="ID", match=conx_id)
      try:
        conx = conx_rows[0]["Connection"]
      except IndexError:
        continue
      try:
        tag_rows = self.db_manager.run_query("SELECT [Address] FROM [TagSubscriptions] WHERE [ConnectionID] = {} GROUP BY [Address];".format(conx_id))
      except IndexError:
        continue
      addresses = list(map(lambda tag_row: tag_row["Address"], tag_rows))
      connection_updates[conx_id] = self.read_once(addresses, connection=conx) #get values from the connections using address
    self.db_manager.update_tag_values(connection_updates) #update them in the table
    return True

  def parse_tagname(self, tag: str)->tuple:
    result = {}
    conx = ''
    if tag.startswith("["):
      conx = re.findall("\[[a-zA-Z0-9_]+\]", tag)
      if not len(conx):
        raise KeyError("ConnectionManager.read_once(), no such connection in {}".format(tag))
      tag = tag.replace(conx[0], "")
      conx = conx[0].replace("[","").replace("]","")
    else: #find in Tags table of the database
      rows = self.db_manager.get_rows("Tags", ["ConnectionID", "DataType"], match_col="Tag", match=tag)
      try:
        conxId = rows[0]["ConnectionID"]
      except IndexError:
        return None, tag      
      datatype = rows[0]["DataType"]
      rows = self.db_manager.get_rows("Connections", ["Connection"], match_col="ID", match=conxId)
      #future get tag's "address" from db?
      conx = rows[0]["Connection"]
    return conx, tag

  def read_once(self, tags: list, connection:Optional[str]=None)->dict:
    #read directly from connection and does not add tag to subscriptions
    #tag list only without curly braces
    tag_vals = {}
    tags_to_read = {} # send connections each a list of tags to read
    for tag in tags:
      if connection is None:
        conx, tag = self.parse_tagname(tag) # not passed connection name, try to lookup
      else:
        conx = connection # explicitly passed connection name
      if not conx in tags_to_read:
        tags_to_read[conx] = []
      tags_to_read[conx].append(tag)
    for conx in tags_to_read:
      if conx in self.connections:
          res = self.connections[conx].read(tags_to_read[conx])
          for tag in res:
            tag_vals[tag] = res[tag]
    return tag_vals
    
  def read(self, tags: list, subscriber_id: str)->dict:
    #should come from the display
    #parse out the tags needed from each controller
    #controller tags are like [CNC]sometag
    #if the first char isn't [ then this is a database tag, else its a dynamic tag
    if not self.db_manager.table_exists("TagSubscriptions"):
      return []
    results = {}
    ts = time.time()
    conx_ids = {}
    for connection in self.connections:
      rows = self.db_manager.get_rows("Connections", ["ID"], match_col="Connection", match=connection)
      conx_ids[connection] = None if not len(rows) else int(rows[0]["ID"])
    for tag in tags:
      results[tag] = {"Value": None, "Timestamp": ts, "DataType": "ERROR"}
      conx, address = self.parse_tagname(tag) #we store the full tag, address with connection in the subs table
      conx_id = conx_ids[conx]
      sql = "SELECT [Tag], [Value], [Timestamp], [DataType] FROM TagSubscriptions WHERE [ConnectionID] = '{}' AND [Subscriber] = '{}' AND [Tag] = '{}';".format(conx_id, subscriber_id, tag)
      tag_rows = self.db_manager.run_query(sql)
      if len(tag_rows): #this subscriber is already subscribed to this tag
        try:
          data_type = tag_rows[0]["DataType"]
          #*****this code was added to deal with Bool values being read out of the database as a string and getting fucked up
          if data_type == 'BOOL' and type(tag_rows[0]["Value"]) == str:
            temp = tag_rows[0]["Value"]
            if temp.lower() in ("true", "1"):
              val = True
            else:
              val = False
          else:
            val = None if tag_rows[0]["Value"] is None else DATATYPES[data_type]["Py_type"](tag_rows[0]["Value"]) # cast val as a native python type
        except ValueError:
          val = None
        results[tag] = {"Value": val, "Timestamp": tag_rows[0]["Timestamp"], "DataType": data_type}
      else: #this is the first time this subscriber asked for this tag, add it to the subs
        self.db_manager.add_subscription(subscriber_id, conx_id, tag, address)
    return results

  def write(self, tag, value):
    conxId = None
    #if the tag is in the database, use that for data type, connection, etc.
    rows = self.db_manager.get_rows("Tags", ["ConnectionID", "DataType"], match_col="Tag", match=tag)
    if len(rows):
      conxId = rows[0]["ConnectionID"]
      datatype = rows[0]["DataType"]
      value = DATATYPES[datatype]["Py_type"](value)
      rows = self.db_manager.get_rows("Connections", ["Connection"], match_col="ID", match=conxId)
      if len(rows):
        self.connections[rows[0]["Connection"]].write(tag, value)
      else:
        raise KeyError("No matching connection ID for tag: {}".format(tag))
    #if not in the database but does have square brackets, this is a dynamic tag
    else:
      #parse out the [controller] from the tagname
      conx = re.findall("\[[a-zA-Z0-9_]+\]", tag)
      if len(conx):
        tag = tag.replace(conx[0], "")
        conx = conx[0].replace("[","").replace("]","")
        #send a write(tag, value) to that controller
        rows = self.db_manager.get_rows("Tags", ["ConnectionID", "DataType"], match_col="Tag", match=tag)
        if len(rows):
          datatype = rows[0]["DataType"]
        else:
          datatype = 'REAL'
        self.connections[conx].write(tag, value)
      else:
        raise KeyError("No matching connection for tag: {}".format(tag))

  @staticmethod
  def get_tags_required(expression: str)->list:
    # reads a script expression and returns a list of tags required to evaluate
    pat = '\{[\[\]a-zA-Z0-9_-]+\}'
    res = re.findall(pat, expression)
    tags = []
    for tag in res:
      tags.append(tag.replace("{", "").replace("}", ""))
    return tags
  
  def evaluate_expression(self, widget: object, expression: str, subscriber_id: str, return_type="REAL"):
    #reads the expression, parses out the tags required, then replaces thier values and runs it
    #returns value if successful or None if tag read or script error
    expression_val = None
    if expression:
      tags = ConnectionManager.get_tags_required(expression)
      if len(tags):
        update = self.read(tags, subscriber_id)
        if len(update):
          for tag in tags:
            if not tag in update or type(update[tag]["Value"]) == type(None):
              #log error? expression cannot be evaluated with all tags
              return None
            wildcard = '{'+f'{tag}'+'}'
            if update[tag]["DataType"] == 'STRING':
              expression = expression.replace(wildcard,"'"+str(update[tag].get("Value"))+"'")
            else:
              expression = expression.replace(wildcard,str(update[tag].get("Value")))
        else:
          return
      try:
        temp_self = self
        self = widget #temp reassign self to the widget
        locs = locals()
        if return_type == 'BOOL':
          code = f'expression_val = bool({expression})' #eval as py type
        else:
          code = f'expression_val = {expression}' #eval as py type
        exec(code, globals(), locs)
        expression_val = locs["expression_val"]
        self = temp_self
      except Exception as e:
        self.app.display_event(e)
        expression_val = None
    return expression_val

  def get_serial_ports(self):
    import platform, os
    serial_device_ports = []
    os_type = platform.system()
    if os_type == 'Linux':
      serial_device_ports = os.listdir('{0}dev'.format(os.path.sep))
      serial_device_ports = [x for x in serial_device_ports if 'ttyUSB' in x or 'ttyACM' in x or 'arduino' in x]
      serial_device_ports = ['{0}dev{0}{1}'.format(os.path.sep,x) for x in serial_device_ports]
    elif os_type == 'Windows':
      try:
        import winreg
      except ImportError:
        import _winreg as winreg
      import itertools
      path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
      try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
      except WindowsError:
        key = None
      if key is not None:
        for i in itertools.count():
          try:
            val = winreg.EnumValue(key, i)
            # Only return USBSER devices
            if 'Serial' in val[0]:
              serial_device_ports.append(str(val[1]))
          except EnvironmentError:
            break
      return serial_device_ports






