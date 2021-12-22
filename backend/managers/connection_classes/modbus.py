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
from typing import Any, Callable, Optional
import threading, time, struct
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from backend.managers.connection_classes.base import Connection
from .const import DATATYPES
import sqlite3
from io import StringIO
from sqlite3 import Error
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.register_read_message import ReadHoldingRegistersResponse, ReadInputRegistersResponse
from pymodbus.bit_read_message import ReadCoilsResponse, ReadDiscreteInputsResponse
from pymodbus.client.sync import ConnectionException

MB_DB_SCHEMA = """
CREATE TABLE "Tags" (
      "Tag"	TEXT NOT NULL,
      "Function" TEXT,
      "Address"	NUMERIC NOT NULL,
      "EndAddress"	NUMERIC NOT NULL,
      "DataType" TEXT NOT NULL,
      "Bit"	BIT DEFAULT 0,
      "WordSwapped" BIT DEFAULT 0,
      "ByteSwapped" BIT DEFAULT 0,
      "PollGroup" NUMERIC,
      "Value" STRING,
      "Timestamp" NUMERIC,
      PRIMARY KEY("Tag")
      )
"""
TABLE_FUNC_ENUM = {'1':	'Coil',
            '2': 'Input Status',
            '3': 'Holding Register',
            '4': 'Input Register'}
MODBUS_MAX_READ = {'Coil': 2000, 
                  'Input Status': 2000,
                  'Holding Register': 125,
                  'Input Register': 125}


class TagUpdateEmitter(GObject.Object):
  def __init__(self, connection):
    super(TagUpdateEmitter, self).__init__()
    self.connection = connection
  @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST, return_type=bool,
                  arg_types=(object,),
                  accumulator=GObject.signal_accumulator_true_handled)
  def tag_update(self, *args):
    self.connection.update_tags()

class ModbusBaseConnection(Connection):
  '''helper class for modbus connections'''

  def __init__(self, connection_manager, idx):
    super().__init__(connection_manager, idx)
    self.mem_db = sqlite3.connect(":memory:",check_same_thread=False)
    c = self.mem_db.cursor()
    c.execute(MB_DB_SCHEMA)
    self.mem_db.commit()
    self.tag_update_emmiter = TagUpdateEmitter(self)
    self.poll_lock = False
    self.poll_rate = 1.0
    self.poll_groups_for_poll_thread = {}
    self.poll_thread_writes= []
    self.connection_err = False
    self.connection_handle = None
    self.active = False
    self.taglist = [] #compared each time to know if optimize is needed
    self.poll_groups ={'1':	{},
            '2': {},
            '3': {},
            '4': {}}
    self.read_functions ={
      'Coil': {},
      'Input Status': {},
      'Holding Register':{},
      'Input Register': {}
    }
    self.poll_thread = threading.Thread(target=self.poll, args=(self,))
    
  
    
  def optimize_poll_groups(self, tags: list):
    '''look up tags in the db table, put in the memdb tables'''
    while self.poll_lock:
      time.sleep(0.01) #wait for poll thread to be idle.
    self.poll_lock = True # lock poll thread while re-optimizing
    self.poll_groups_for_poll_thread= {'1':	{},
            '2': {},
            '3': {},
            '4': {}}
    c = self.mem_db.cursor()
    c.execute("DELETE FROM [Tags];") # drop all tags, re-optimize
    self.mem_db.commit()
    for tag in tags:
      params = self.db_manager.get_rows("ModbusTCPTags",["Tag", "ConnectionID", "DataType", "Function", "Address", "Bit", "WordSwapped", "ByteSwapped"],
      match_col="Tag", match=tag)
      if len(params) and (self.id == int(params[0].get('ConnectionID'))):
        params = params[0]
        try:
          if params.get('Function') in ['Coil', 'Input Status']:
            end_addr = params.get('Address')
          else:
            ##################################################################################################################################
            ####################  This insert needs to be updated because tags doesn't contain WordSwapped / Byte Swapped.  What are we trying to do here, these values only all
            ####################  exist together in the ModbusTCPTags view in the database
            ################################################################################################################################
            end_addr = params.get('Address')+(DATATYPES[params.get('DataType', 'INT')]['ModbusRegisters'] -1), #end address
          c.execute("INSERT INTO [Tags] ('Tag', 'DataType', 'Function', 'Address', 'EndAddress', 'Bit', 'WordSwapped', 'ByteSwapped') VALUES (?,?,?,?,?,?,?,?);",
            [params.get('Tag'),params.get('DataType'),params.get('Function'),
            params.get('Address'),
            end_addr,
            params.get('Bit'),
            params.get('WordSwapped'),params.get('ByteSwapped')])
        except KeyError:
          #Throw error?
          pass
    self.mem_db.commit()
    #put all tags into pollgroups in the db
    for func in '1234':
      res = [1]
      group_addr = 0
      poll_group = 1
      max_read = MODBUS_MAX_READ[TABLE_FUNC_ENUM[func]]
      while res:
        res = c.execute( #get the first address of the group
          f"SELECT [Address] FROM [Tags] WHERE [Function] = '{TABLE_FUNC_ENUM[func]}' AND [Address] >= {group_addr} ORDER BY [Address] ASC LIMIT 1").fetchone()
        if res:
          group_address = res[0]
          max_end_address = group_addr+max_read-1
          c.execute(f'UPDATE [Tags] SET [PollGroup]={poll_group} WHERE [EndAddress] <= {max_end_address}')
          group_addr = max_end_address + 1
          poll_group += 1      
    self.mem_db.commit()
    #put all function pollgroups in self.poll_groups for the polling thread
    for func in '1234':
      res = c.execute(
        f"SELECT [Pollgroup] FROM [Tags] WHERE [Function] = '{TABLE_FUNC_ENUM[func]}' GROUP BY [PollGroup]").fetchall()
      for group_res in res:
        addr_min = None
        addr_max = None
        group = group_res[0]
        tag_res = c.execute(
        f"SELECT MIN([Address]) FROM [Tags] WHERE [Function] = '{TABLE_FUNC_ENUM[func]}' AND [Pollgroup] = '{group}'").fetchone()
        if tag_res:
          addr_min = tag_res[0]
        tag_res = c.execute(
        f"SELECT MAX([EndAddress]) FROM [Tags] WHERE [Function] = '{TABLE_FUNC_ENUM[func]}' AND [Pollgroup] = '{group}'").fetchone()
        if tag_res:
          addr_max = tag_res[0]
        if not (addr_min is None or addr_max is None):
          self.poll_groups[func][group] = {'Address': addr_min, 'Length': 1+(addr_max-addr_min), 'Values': [], 'Timestamp': time.time()}
    self.poll_lock = False


  @staticmethod
  def byte_swap(data: bytes):
    while(len(data)%2):
      data += b'\x00'
    new_data = b''
    for i in range(0,len(data),2):
      new_data += struct.pack('BB', data[i+1], data[i])
    return new_data

  @staticmethod
  def word_swap(data: bytes):
    while(len(data)%4):
      data += b'\x00'
    new_data = b''
    for i in range(0,len(data),4):
      new_data += struct.pack('BBBB', data[i+2], data[i+3], data[i], data[i+1])
    return new_data

  @staticmethod
  def taglists_equal(l1: list, l2: list)->bool:
    s1=set(l1)
    s2=set(l2)
    return bool(not(len(s1-s2) or len(s2-s1)))

  def update_tags(self, *args):
    """fired by update poll via the TagUpdateEmitter"""
    while self.poll_lock:
      time.sleep(0.01)
      print('Waiting....')
    c  = self.mem_db.cursor()
    for func in '1234':
      for group_num in self.poll_groups[func]:
        group = self.poll_groups[func][group_num]
        ts = group.get('Timestamp')
        #get tags for this group
        res = c.execute(
        f"SELECT [Tag], [Address], [DataType], [ByteSwapped], [WordSwapped], [Bit] FROM [Tags] WHERE [Function] = '{TABLE_FUNC_ENUM[func]}' AND [PollGroup] = '{group_num}'").fetchall()
        for tag_res in res:
          addr = int(tag_res[1])
          d_type = tag_res[2]
          b_swap = bool(tag_res[3])
          w_swap = bool(tag_res[4])
          bit_offset = tag_res[5]
          offset = addr - group.get('Address') # how many registers or bits into this group is this tag
          if func in ['3', '4']: #registers
            _mb_len = DATATYPES[d_type].get('ModbusRegisters')
            _buff_len = DATATYPES[d_type].get('Bytes')
            _registers = group.get('Values')[offset:offset+_mb_len+1]
            if d_type == 'BOOL':
              val = bool(0x0001<<bit_offset & _registers[0])
            else:
              if len(_registers) == _mb_len:
                _buff = struct.pack('H'*_mb_len, *_registers)
                if b_swap:
                  _buff = self.byte_swap(_buff)
                if w_swap:
                  _buff = self.word_swap(_buff)
                val = DATATYPES[d_type].get('Py_type')(struct.unpack(DATATYPES[d_type].get('struct_fmt'),_buff)[0])
              else:
                val = 'NULL'
          else:
            if len(group.get('Values')) > offset:
              val = DATATYPES[d_type].get('Py_type')(group.get('Values')[offset])
            else:
              val = 'NULL'
          c.execute(f"UPDATE [Tags] SET [Value]={val}, [Timestamp]={ts} WHERE [Tag] = '{tag_res[0]}'")

        self.mem_db.commit()



  def read(self, tags: list)->dict:
    results = {}
    bad_tag = {"Value":None, "Timestamp": time.time(), "DataType": 'INT'}
    if not self.taglists_equal(self.taglist, tags):
      self.optimize_poll_groups(tags)
      self.taglist = tags
    c = self.mem_db.cursor()
    for tag in tags: # get them from the class' db
      results[tag] = bad_tag
      if self.connection_handle:
        res = c.execute("SELECT [Value], [Timestamp], [Datatype] FROM [Tags] WHERE [Tag] = ?;", [tag]).fetchone()
        if res:
          val = None
          if not res[0] is None:
            val =  DATATYPES[res[2]]['Py_type'](res[0]) #convert to python data type 
          ts = res[1] if not res[1] is None else time.time() #timestamp the bad quality          
          results[tag] = {"Value":val, "Timestamp": ts, "DataType": res[2]}
        #else: #Throw error?
    return results

  def write(self, tag, val):
    #queue controller writes
    queue = None
    #find the tag in the project db
    res = self.db_manager.get_rows("ModbusTCPTags",["Tag", "ConnectionID", "DataType", "Function", "Address", "Bit", "WordSwapped", "ByteSwapped"],
      match_col="Tag", match=tag)
    if not len(res):
      #Throw error?
      return
    tag = res[0]
    #format to modbus coil or register
    #the queue entry is a dict. e.g. {'Function': '3', 'Address': 100, 'Value': [100,100]} or
    #                                {'Function': '3', 'Address': 50, 'Value': [1], 'Bit': 5} <- this will read the reg first then set Bit 5 True, to overwrite the reg
    #                                {'Function': '1', 'Address': 50, 'Value': [1]}<- this will write 1 to coil 50
    if tag['Function'] == 'Holding Register': #Holding Reg
      if tag['DataType'] == "BOOL": #bit packed HR
        queue = {'Function': '3', 'Address': tag['Address'], 'Value': [int(bool(val))], 'Bit': tag['Bit']}
      else:
        _fmt = DATATYPES[tag['DataType']].get('struct_fmt')
        _buff = struct.pack(_fmt, val)
        if len(_buff) % 2: _buff += '\x00' #pad to fit 16-bit reg
        if tag['ByteSwapped']:
          _buff = self.byte_swap(_buff)
        if tag['WordSwapped']:
          _buff = self.word_swap(_buff)
        queue = {'Function': '3', 'Address': tag['Address'], 'Value': struct.unpack('H'*int(len(_buff)/int(2)), _buff)}
    elif tag['Function'] == 'Coil': #Coil
      queue = {'Function': '1', 'Address': tag['Address'], 'Value': bool(val)}
    #pack as bytes, then unpack as 16-bit int
    if not queue is None:
      while self.poll_lock:
        time.sleep(0.01) #wait for poll_lock to free
      self.poll_lock = True
      #add write to the queue
      self.poll_thread_writes.append(queue)
      self.poll_lock = False

  def update_hold_reg_tags(self):
    if not self.connection_handle:
      return
    for group_num in self.poll_groups['3']:
      group = self.poll_groups['3'][group_num]
      response = self.connection_handle.read_holding_registers(group['Address'], group['Length'], unit=self.station_id)
      if type(response) == ReadHoldingRegistersResponse:
        group['Values']= response.registers
        group['Timestamp']= time.time()

  def update_coil_tags(self):
    if not self.connection_handle:
      return
    for group_num in self.poll_groups['1']:
      group = self.poll_groups['1'][group_num]
      response = self.connection_handle.read_coils(group['Address'], group['Length'], unit=self.station_id)
      if type(response) == ReadCoilsResponse:
        group['Values']= response.bits
        group['Timestamp']= time.time()

  def update_input_stat_tags(self):
    if not self.connection_handle:
      return
    for group_num in self.poll_groups['2']:
      group = self.poll_groups['2'][group_num]
      response = self.connection_handle.read_discrete_inputs(group['Address'], group['Length'], unit=self.station_id)
      if type(response) == ReadDiscreteInputsResponse:
        group['Values']= response.bits
        group['Timestamp']= time.time()
        
  def update_input_reg_tags(self):
    if not self.connection_handle:
      return
    for group_num in self.poll_groups['4']:
      group = self.poll_groups['4'][group_num]
      response = self.connection_handle.read_input_registers(group['Address'], group['Length'], unit=self.station_id)
      if type(response) == ReadInputRegistersResponse:
        group['Values']= response.registers
        group['Timestamp']= time.time()

  def write_holding_regs(self, tag):
    if tag.get('Bit'):
      response = self.connection_handle.read_holding_registers(tag.get('Address'), 1, unit=self.station_id)
      if type(response) == ReadHoldingRegistersResponse:
        temp = response.registers[0]
        if (tag.get('Value')[0]): #set bit
          temp |= 0x0001<<tag.get('Bit')
        else: # clear bit
          temp &= (0xffff-(0x0001<<tag.get('Bit')))
        return self.connection_handle.write_registers(tag.get('Address'), temp, unit=self.station_id)
    else:
      return self.connection_handle.write_registers(tag.get('Address'), tag.get('Value', []), unit=self.station_id)

  def write_coils(self, tag):
    return self.connection_handle.write_coils(tag.get('Address'), tag.get('Value', []), unit=self.station_id)

  def poll(self, *args):
    while(self.connect_cmd): #while polling
      t=time.time()
      if not self.connection_handle:
        self.connect_controller()
      elif self.connection_handle:
        try:
          self.poll_lock = True
          #do polling here
          #write any values to controller
          for tag_write in self.poll_thread_writes:
            if tag_write.get('Function') == '3':
              self.write_holding_regs(tag_write)
            if tag_write.get('Function') == '1':
              self.write_coils(tag_write)
          self.poll_thread_writes = []          
          #read the required tags from the subs plus any direct reads
          self.update_coil_tags()
          self.update_input_stat_tags()
          self.update_hold_reg_tags()
          self.update_input_reg_tags()
        except ConnectionException as e:
          self.connection_handle = None
          event_msg = "Modbus Controller comm err: {}".format(e)
          self.connection_manager.emit("new_event", event_msg)
      self.poll_lock = False
      if self.connection_handle:
        self.tag_update_emmiter.emit('tag_update', True)
      dt = time.time()-t
      to = max(0.1, (self.pollrate - dt)) if self.connection_handle else 1.0
      time.sleep(to)
    #closing

  def connect(self,*args):
    self.connect_cmd = True
    if not self.poll_thread.is_alive():
      self.poll_thread.daemon=True
      self.poll_thread.start()
    self.active = True

  def disconnect(self,*args):
    self.connect_cmd = False
    while self.poll_thread.is_alive():
        time.sleep(0.01)
    if self.connection_handle:
      self.connection_handle.close()
    self.connection_handle = None
    self.active = False
  
  def update_conn_settings(self,db,setting,val,*args):
    if setting == 'PORT':
      self.port = val
    self.db_manager.set_db_val_by_id(db,setting,self.id,val)  #update memory db
    self.db_manager.copy_table(db)  

class ModbusTCP_Connection(ModbusBaseConnection):
  def __init__(self, connection_manager, idx):
    super().__init__(connection_manager, idx)
    params = self.db_manager.get_rows("ModbusTCPConnectionsParams",["Host", "Port", "StationID", "Pollrate", "AutoConnect"], match_col="ID", match=self.id)
    if not len(params):
      raise KeyError("ModbusTCP connection parameters missing in project database for ID: {}".format(self.id))
    params = params[0]
    self.port = int(params["Port"])
    self.pollrate = float(params["Pollrate"])
    self.auto_connect = bool(int(params["AutoConnect"]))
    self.host = params["Host"]
    self.station_id = int(params["StationID"])
    if self.auto_connect:
      self.connect()
    
  def connect_controller(self):
    try:
      self.connection_handle = ModbusTcpClient(self.host, self.port)
    except ConnectionException as e:
      self.connection_handle = None
      event_msg = "ModbusTCP Controller comm err: {}".format(e)
      self.connection_manager.emit("new_event", event_msg)

class ModbusRTU_Connection(ModbusBaseConnection):
  def __init__(self, connection_manager, idx):
    self.serial_port = 'COM1'
    self.station_id = 1
    self.stop_bits = 1
    self.byte_size = 8
    self.parity = 'N'
    self.baudrate = 9600
    self.time_out = 3.0
    self.retries = 3
    super().__init__(connection_manager, idx)
    params = self.db_manager.get_rows("ModbusRTUConnectionsParams",["SerialPort", "StationID", "Pollrate","BaudRate","StopBit","Parity","ByteSize","Timeout","AutoConnect"], match_col="ID", match=self.id)
    if not len(params):
      #raise KeyError("ModbusRTU connection parameters missing in project database for ID: {}".format(self.id))
      event_msg = "ModbusRTU connection parameters missing in project database for ID: {}".format(self.id)
      self.connection_manager.emit("new_event", event_msg)
    params = params[0]
    self.serial_port = (params["SerialPort"])
    self.pollrate = float(params["Pollrate"])
    self.auto_connect = bool(int(params["AutoConnect"]))
    self.station_id = int(params["StationID"])
    self.baudrate = int(params["BaudRate"])
    self.time_out = int(params["Timeout"])
    self.stop_bits = int(params["StopBit"])
    self.byte_size = int(params["ByteSize"])
    self.parity = params["Parity"]
    if self.auto_connect:
      self.connect()
  def connect_controller(self):
    try:
      self.connection_handle = ModbusSerialClient(method="rtu", port = self.serial_port, stopbits=self.stop_bits, bytesize=self.byte_size,
                                                  parity=self.parity, baudrate=self.baudrate, timeout=self.time_out)
    except ConnectionException as e:
      self.connection_handle = None
      event_msg = "ModbusRTU Controller comm err: {}".format(e)
      self.connection_manager.emit("new_event", event_msg)
