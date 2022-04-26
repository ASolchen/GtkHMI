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
import re
import threading
import serial
import time
import struct
from typing import Any, Callable, Optional
from backend.managers.connection_classes.base import Connection
from backend.managers.connection_classes.const import DATATYPES
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf

CNC_BUFFER_SZ = 128

class Grbl_Connection(Connection):

    def __init__(self, manager: object, idx: str):
        super(Grbl_Connection, self).__init__(manager, idx)
        params = self.db_manager.get_rows("GrblConnectionsParams",["Port", "PendantPort", "Pollrate", "AutoConnect"], match_col="ID", match=self.id)
        if not len(params):
            raise KeyError("Grbl connection parameters missing in project database for ID: {}".format(self.id))
        params = params[0]
        self.port = params["Port"]
        self.pollrate = float(params["Pollrate"])
        self.auto_connect = (params["AutoConnect"])
        self.settings_read_req = True # read all settings on connect
        self.connection_err = False
        self.connect_cmd = False
        self.connection_handle = None 
        self.poll_thread = threading.Thread(target=self.poll, args=(self,))
        #self.poll_thread.daemon=True
        self.WCO = [0,0,0]
        self.state_enum = {'Disconnected':0,
        'Idle': 1,
        'Run':2,
        'Hold:0': 3,
        'Hold:1': 3.1,
        'Jog':4,
        'Alarm':5,
        'Door:0':6,
        'Door:1':6.1,
        'Door:2':6.2,
        'Door:3':6.3,
        'Check':7,
        'Home':8,
        'Sleep':9}
        self.tags = {
            '$0':    {"Value": 10, "Timestamp": 0.0, "DataType": "INT"},
            '$1':    {"Value": 25, "Timestamp": 0.0, "DataType": "INT"},
            '$2':    {"Value": 0, "Timestamp": 0.0, "DataType": "INT"},
            '$3':    {"Value": 0, "Timestamp": 0.0, "DataType": "INT"},
            '$4':    {"Value": 0, "Timestamp": 0.0, "DataType": "INT"},
            '$5':    {"Value": 1, "Timestamp": 0.0, "DataType": "INT"},
            '$6':    {"Value": 0, "Timestamp": 0.0, "DataType": "INT"},
            '$10':    {"Value": 1, "Timestamp": 0.0, "DataType": "INT"},
            '$11':    {"Value": 0.010, "Timestamp": 0.0, "DataType": "REAL"},
            '$12':    {"Value": 0.002, "Timestamp": 0.0, "DataType": "REAL"},
            '$13':    {"Value": 0, "Timestamp": 0.0, "DataType": "INT"},
            '$20':    {"Value": 0, "Timestamp": 0.0, "DataType": "INT"},
            '$21':    {"Value":0, "Timestamp": 0.0, "DataType": "INT"},
            '$22':    {"Value":0, "Timestamp": 0.0, "DataType": "INT"},
            '$23':    {"Value":0, "Timestamp": 0.0, "DataType": "INT"},
            '$24':    {"Value":25.000, "Timestamp": 0.0, "DataType": "REAL"},
            '$25':    {"Value":500.000, "Timestamp": 0.0, "DataType": "REAL"},
            '$26':    {"Value":250, "Timestamp": 0.0, "DataType": "INT"},
            '$27':    {"Value":1.000, "Timestamp": 0.0, "DataType": "REAL"},
            '$30':    {"Value":1000, "Timestamp": 0.0, "DataType": "INT"},
            '$31':    {"Value":0, "Timestamp": 0.0, "DataType": "INT"},
            '$32':    {"Value":0, "Timestamp": 0.0, "DataType": "INT"},
            '$100':    {"Value":100.000, "Timestamp": 0.0, "DataType": "REAL"},
            '$101':    {"Value":100.000, "Timestamp": 0.0, "DataType": "REAL"},
            '$102':    {"Value":100.000, "Timestamp": 0.0, "DataType": "REAL"},
            '$110':    {"Value":5000.000, "Timestamp": 0.0, "DataType": "REAL"},
            '$111':    {"Value":5000.000, "Timestamp": 0.0, "DataType": "REAL"},
            '$112':    {"Value":1000.000, "Timestamp": 0.0, "DataType": "REAL"},
            '$120':    {"Value":10.000, "Timestamp": 0.0, "DataType": "REAL"},
            '$121':    {"Value":10.000, "Timestamp": 0.0, "DataType": "REAL"},
            '$122':    {"Value":10.000, "Timestamp": 0.0, "DataType": "REAL"},
            '$130':    {"Value":200.000, "Timestamp": 0.0, "DataType": "REAL"},
            '$131':    {"Value":200.000, "Timestamp": 0.0, "DataType": "REAL"},
            '$132':    {"Value":200.000, "Timestamp": 0.0, "DataType": "REAL"},
            'state':    {"Value":0, "Timestamp": 0.0, "DataType": "INT"},
            'pendant-ticks':    {"Value":0, "Timestamp": 0.0, "DataType": "UDINT"},
            'manual-ticks-init':    {"Value":0.0, "Timestamp": 0.0, "DataType": "REAL"},
            'manual-sp-init':    {"Value":0.0, "Timestamp": 0.0, "DataType": "REAL"},
            'pendant-mm-rev':    {"Value":10.0, "Timestamp": 0.0, "DataType": "REAL"},
            'MPos-X':    {"Value":0.0, "Timestamp": 0.0, "DataType": "REAL"},
            'MPos-Y':    {"Value":0.0, "Timestamp": 0.0, "DataType": "REAL"},
            'MPos-Z':    {"Value":0.0, "Timestamp": 0.0, "DataType": "REAL"},
            'WPos-X':    {"Value":0.0, "Timestamp": 0.0, "DataType": "REAL"},
            'WPos-Y':    {"Value":0.0, "Timestamp": 0.0, "DataType": "REAL"},
            'WPos-Z':    {"Value":0.0, "Timestamp": 0.0, "DataType": "REAL"},
            'WCO-X':    {"Value":0.0, "Timestamp": 0.0, "DataType": "REAL"},
            'WCO-Y':    {"Value":0.0, "Timestamp": 0.0, "DataType": "REAL"},
            'WCO-Z':    {"Value":0.0, "Timestamp": 0.0, "DataType": "REAL"},
            'manual-X':    {"Value":False, "Timestamp": 0.0, "DataType": "BOOL"},
            'manual-Y':    {"Value":False, "Timestamp": 0.0, "DataType": "BOOL"},
            'manual-Z':    {"Value":False, "Timestamp": 0.0, "DataType": "BOOL"},
            'manual-X-sp':    {"Value":0.0, "Timestamp": 0.0, "DataType": "REAL"},
            'manual-Y-sp':    {"Value":0.0, "Timestamp": 0.0, "DataType": "REAL"},
            'manual-Z-sp':    {"Value":0.0, "Timestamp": 0.0, "DataType": "REAL"},
            'jogspeed-X':    {"Value":500, "Timestamp": 0.0, "DataType": "REAL"},
            'jogdist-X':    {"Value":1.0, "Timestamp": 0.0, "DataType": "REAL"},
            'jogspeed-Y':    {"Value":500, "Timestamp": 0.0, "DataType": "REAL"},
            'jogdist-Y':    {"Value":1.0, "Timestamp": 0.0, "DataType": "REAL"},
            'jogspeed-Z':    {"Value":100, "Timestamp": 0.0, "DataType": "REAL"},
            'jogdist-Z':    {"Value":0.2, "Timestamp": 0.0, "DataType": "REAL"},
            'eu':    {"Value":0, "Timestamp": 0.0, "DataType": "INT"}, # 0=mm 1=inches
            'spindle-run':    {"Value":False, "Timestamp": 0.0, "DataType": "BOOL"},
            'coolant':    {"Value":False, "Timestamp": 0.0, "DataType": "BOOL"},
            'override-spindle':    {"Value":100.0, "Timestamp": 0.0, "DataType": "REAL"},
            'override-feed':    {"Value":100.0, "Timestamp": 0.0, "DataType": "REAL"},
            'override-rapids':    {"Value":100.0, "Timestamp": 0.0, "DataType": "REAL"},
            'pin-X':    {"Value":False, "Timestamp": 0.0, "DataType": "BOOL"},
            'pin-Y':    {"Value":False, "Timestamp": 0.0, "DataType": "BOOL"},
            'pin-Z':    {"Value":False, "Timestamp": 0.0, "DataType": "BOOL"},
            'pin-P':    {"Value":False, "Timestamp": 0.0, "DataType": "BOOL"},
            'pin-D':    {"Value":False, "Timestamp": 0.0, "DataType": "BOOL"},
            'pin-H':    {"Value":False, "Timestamp": 0.0, "DataType": "BOOL"},
            'pin-R':    {"Value":False, "Timestamp": 0.0, "DataType": "BOOL"},
            'pin-S':    {"Value":False, "Timestamp": 0.0, "DataType": "BOOL"},
            'block-in-avail':    {"Value":0, "Timestamp": 0.0, "DataType": "INT"},
            'chars-avail':    {"Value":0, "Timestamp": 0.0, "DataType": "INT"},
            'spindle-speed':    {"Value":0, "Timestamp": 0.0, "DataType": "REAL"},
            'feedrate':    {"Value":0, "Timestamp": 0.0, "DataType": "REAL"}, 
        }
        self.pendant = Pendant(self, params["PendantPort"], self.connection_manager)
        self.realtime_cmd = None
        self.blocks_to_send_private = [] #gcode blocks or lines to send (not threadsafe)
        self.blocks_to_send = [] #gcode blocks or lines to send
        self.block_lock = False
        self.blocks_sent = [] #blocks that have been sent but not completed
        if self.auto_connect:
            self.connectDevice()

    def read(self, tags):
        results = {}
        ts = time.time()
        for tag in tags:
            try:
                if tag != 'state' and not self.tags['state']['Value']: #is disconnected, return None
                    raise KeyError
                results[tag] = self.tags[tag]
                results[tag]['Timestamp'] = ts
            except KeyError:                
                pass
        return results

    def write(self, tag, val):
        #catch all for controller writes
        if tag.startswith("$"):
            self.realtime_cmd = "{}={}".format(tag,val) #settings tags
            self.settings_read_req = True
            return
        if tag in self.tags:
            self.tags[tag]["Value"] = DATATYPES[self.tags[tag]["DataType"]]["Py_type"](val) #cast val to that type
            return
        if tag == 'resume_cmd':
            self.realtime_cmd = "~\n"
            return
        if tag == 'hold_cmd':
            self.realtime_cmd = "!\n"
            return
        if tag == 'reset_cmd':
            self.realtime_cmd = "\x18\n"
            self.blocks_to_send = self.blocks_to_send_private = []
            return
        if tag == 'alm_reset_cmd':
            self.realtime_cmd = "$X\n"
            return
        if tag == 'home_cmd':
            self.realtime_cmd = "$H\n"
            return
        if tag == 'jog-X-pos':
            self.realtime_cmd = "$J=G91X{}F{}\n".format(self.tags["jogdist-X"]['Value'], self.tags["jogspeed-X"]['Value'])
            return
        if tag == 'jog-X-neg':
            self.realtime_cmd = "$J=G91X-{}F{}\n".format(self.tags["jogdist-X"]['Value'], self.tags["jogspeed-X"]['Value'])
            return
        if tag == 'jog-Y-pos':
            self.realtime_cmd = "$J=G91Y{}F{}\n".format(self.tags["jogdist-Y"]['Value'], self.tags["jogspeed-Y"]['Value'])
            return
        if tag == 'jog-Y-neg':
            self.realtime_cmd = "$J=G91Y-{}F{}\n".format(self.tags["jogdist-Y"]['Value'], self.tags["jogspeed-Y"]['Value'])
            return
        if tag == 'jog-Z-pos':
            self.realtime_cmd = "$J=G91Z{}F{}".format(self.tags["jogdist-Z"]['Value'], self.tags["jogspeed-Z"]['Value'])
            return
        if tag == 'jog-Z-neg':
            self.realtime_cmd = "$J=G91Z-{}F{}\n".format(self.tags["jogdist-Z"]['Value'], self.tags["jogspeed-Z"]['Value'])
            return
        if tag == 'home-X':
            self.blocks_to_send.append("G10P0L20X{}".format(val))
            return
        if tag == 'home-Y':
            self.blocks_to_send.append("G10P0L20Y{}".format(val))
            return
        if tag == 'home-Z':
            self.blocks_to_send.append("G10P0L20Z{}".format(val))
            return
        if tag == 'gcode-line':
            if val.startswith("$"):
                self.realtime_cmd = "{}\n".format(val)
            else:
                self.blocks_to_send.append(val)
            return
        if tag == 'gcode-program':
            self.send_gcode(val)
            return
        if tag.startswith('override-'):
            cmds = {"feed-100" : b"\x90",
                            "feed-inc-10" : b"\x91",
                            "feed-dec-10" : b"\x92",
                            "feed-inc-1" : b"\x93",
                            "feed-dec-1" : b"\x94",
                            "rapids-100" : b"\x95",
                            "rapids-50" : b"\x96",
                            "rapids-25" : b"\x97",
                            "spindle-100" : b"\x99",
                            "spindle-inc-10" : b"\x9A",
                            "spindle-dec-10" : b"\x9B",
                            "spindle-inc-1" : b"\x9C",
                            "spindle-dec-1" : b"\x9D",
            }
            _cmd =    cmds.get(tag.replace('override-', ''))
            if _cmd:
                self.realtime_cmd =(_cmd)
            return
        if tag in ['manual-cmd-X', 'manual-cmd-Y', 'manual-cmd-Z']:
            self.manual_toggle(tag)
            return
        #if write command isn't identified that throw alarm
        event_msg = "Unhandled connection write in CNC: {}".format(tag)
        self.connection_manager.emit("new_event", event_msg)
        
    def send_gcode(self, gcode):
        while(self.block_lock):
            pass
        self.block_lock = True
        for line in gcode.split('\n'):
            line = line.strip('\r')
            self.blocks_to_send.append(line)
        self.block_lock = False

    def manual_toggle(self, cmd):
        #print(self.tags['manual-X'])
        if self.tags['state']["Value"] != 1:
            return
        axis = cmd.replace('manual-cmd-',"")
        state = self.tags['manual-{}'.format(axis)]["Value"]
        for a in ["X","Y","Z"]:
            self.tags['manual-{}'.format(a)]["Value"] = False 
        if not state: #was off, turn on
            self.tags['manual-{}'.format(axis)]["Value"] = True
            self.tags['manual-ticks-init']["Value"] = self.tags['pendant-ticks']["Value"]
            self.tags['manual-sp-init']["Value"] = self.tags['WPos-{}'.format(axis)]["Value"]
        #print(self.tags['manual-X'],type(self.tags['manual-X']['Value']))
        self.update_manual_vals()

    def update_manual_vals(self):
        for axis in ["X","Y","Z"]:
            if self.tags['manual-{}'.format(axis)]["Value"]:
                sp = self.tags['manual-sp-init']["Value"] - (self.tags['manual-ticks-init']["Value"]-self.tags['pendant-ticks']["Value"]) / (self.tags['pendant-mm-rev']["Value"])
                speed = self.tags['jogspeed-{}'.format(axis)]["Value"]
                self.realtime_cmd = '$J=G90{}{}F{}\n'.format(axis, sp, speed)
                self.tags['manual-{}-sp'.format(axis)]["Value"] = sp
            else:
                self.tags['manual-{}-sp'.format(axis)]["Value"] = self.tags['WPos-{}'.format(axis)]["Value"]
        
    def connectDevice(self,*args):
        self.connect_cmd = True
        if not self.poll_thread.is_alive():
            self.poll_thread = threading.Thread(target=self.poll, args=(self,))
            self.poll_thread.daemon=True
            self.poll_thread.start()

    def disconnectDevice(self,*args):
        self.connect_cmd = False
        while self.poll_thread.is_alive():
                time.sleep(0.01)
        if self.connection_handle:
            self.connection_handle.close()
        self.connection_handle = None
        self.tags['state']["Value"] = 0
    
    def update_conn_settings(self,db,setting,val,*args):
        if setting == 'PORT':
            self.port = val
        self.db_manager.set_db_val_by_id(db,setting,self.id,val)    #update memory db
        self.db_manager.copy_table(db)                                                        #update main db

    def poll(self, *args):
        self.connection_handle = None
        tx_id = 0
        while(self.connect_cmd): #while polling
            t=time.time()
            while(self.block_lock):
                pass
            self.block_lock = True
            self.blocks_to_send_private += self.blocks_to_send
            self.blocks_to_send = []
            self.block_lock = False
            
            if not self.connection_handle:
                try:
                    self.connection_handle = serial.Serial(self.port, 115200, timeout=0.1)
                except Exception as e:
                    if not self.connection_err:
                        event_msg = "CNC Controller comm err: {}".format(e)
                        self.connection_manager.emit("new_event", event_msg)

                        self.connection_err = True
                    self.tags['state'].update({"Value": 0, 'Timestamp': t})
                    self.connection_handle = None
            if self.connection_handle:
                self.connection_err = False
                if 1: #try:
                    if self.realtime_cmd:
                        if type(self.realtime_cmd) == bytes:
                            self.connection_handle.write(self.realtime_cmd + "\n".format().encode("ascii"))                            
                        else:
                            self.connection_handle.write("{}\n".format(self.realtime_cmd).encode("ascii"))
                        self.realtime_cmd = None
                    if self.settings_read_req:
                        self.connection_handle.write("$$\n".encode("ascii")) # triggers a read of all settings
                    chars_sent = 0
                    for block in self.blocks_sent:
                        chars_sent += len(block)
                    buff_avail = CNC_BUFFER_SZ - chars_sent
                    while len(self.blocks_to_send_private) and len(self.blocks_to_send_private[0]) <= buff_avail:
                        block = self.blocks_to_send_private.pop(0)
                        buff_avail -= len(block)
                        self.connection_handle.write("{}\n".format(block).encode("ascii"))
                        self.blocks_sent = [block] + self.blocks_sent
                    self.connection_handle.write("?\n".encode("ascii"))
                    data = ''
                    tag_update = {}
                    self.update_manual_vals()
                    tag_update.update(self.tags)
                    keep_going = 1
                    while keep_going:
                        b = self.connection_handle.read()
                        keep_going = len(b)
                        data+=b.decode('ascii')
                    lines = data.split('\r\n')
                    for line in lines:
                        if line.startswith("<"):
                            update = re.split(r'\|', re.sub("\r", "", re.sub("\n", "", re.sub("\<", "", re.sub("\>", "", line)))))
                            if "WCO:" in line:
                                self.update_tag('spindle-run', 0, t)
                                self.update_tag('coolant', 0, t)
                            for pin in 'XYZPDHRS':
                                self.update_tag(f'pin-{pin}', 0, t)#init pins, if on it will get updated
                            for idx, field in enumerate(update):
                                if (idx==0):
                                    self.update_tag('state', self.state_enum[field], t)
                                elif (field.startswith('MPos:')):
                                    _x,_y,_z = field.replace('MPos:', "").split(',')
                                    self.update_tag('MPos-X', _x, t)
                                    self.update_tag('MPos-Y', _y, t)
                                    self.update_tag('MPos-Z', _z, t)
                                    _x,_y,_z = [float(self.tags['MPos-X']["Value"])-self.WCO[0], float(self.tags['MPos-Y']["Value"])-self.WCO[1], float(self.tags['MPos-Z']["Value"])-self.WCO[2]]
                                    self.update_tag('WPos-X', _x, t)
                                    self.update_tag('WPos-Y', _y, t)
                                    self.update_tag('WPos-Z', _z, t)
                                elif (field.startswith('Bf:')):
                                    _b,_c = field.replace('Bf:', "").split(',')
                                    self.update_tag('block-in-avail', _b, t)
                                    self.update_tag('chars-avail', _c, t)
                                elif (field.startswith('F:')):
                                    self.update_tag('spindle-speed', field.replace('F:', ""), t)
                                elif (field.startswith('FS:')):
                                    _f, _s = field.replace('FS:', "").split(',')
                                    self.update_tag('feedrate', _f, t)
                                    self.update_tag('spindle-speed', _s, t)
                                elif (field.startswith('WCO:')):
                                    self.WCO = list(map(lambda s: float(s), field.replace('WCO:', "").split(',')))
                                    for idx, axis in enumerate('xyz'):
                                        self.update_tag(f'WCO-{axis.upper()}', self.WCO[idx], t)
                                elif (field.startswith('Pn:')):
                                    for pin in field.replace('Pn:', ""):
                                        self.update_tag(f'pin-{pin}', 1, t)
                                elif (field.startswith('Ov:')):
                                    _orf, _orr, _ors = field.replace('Ov:', "").split(',')
                                    self.update_tag('override-feed', _orf, t)
                                    self.update_tag('override-rapids', _orr, t)
                                    self.update_tag('override-spindle', _ors, t)
                                elif (field.startswith('A:')):
                                    for acc in field.replace('A:', "").split(','):
                                        if acc == "S": self.update_tag('spindle-run', 1, t) #FWD
                                        if acc == "C": self.update_tag('spindle-run', -1, t) #REV
                                        if acc == "F": self.update_tag('coolant', 1, t) #FLOOD
                                        if acc == "M": self.update_tag('coolant', 2, t) #MIST
                                else:
                                    event_msg = "CNC Controller field unhandled: {}".format(field)
                                    self.connection_manager.emit("new_event", event_msg)
                        if line == 'ok':
                            block_in = len(self.blocks_sent)
                            if block_in:
                                self.blocks_sent = self.blocks_sent[1:]
                        if line.startswith('Grbl'):
                            pass #connected
                        if line.startswith("$"):
                            self.settings_read_req = False
                            setting, setting_val = line.split("=")
                            self.update_tag(setting, setting_val, t)
                else: #except Exception as e:
                    self.disconnectDevice()
            dt = time.time()-t
            to = max(0.1, (self.pollrate - dt)) if self.connection_handle else 1.0
            time.sleep(to)


class Pendant(object):
    
    def __init__(self, cnc_connection, port,manager):
        self.connection_manager = manager
        self.port = port
        self.cnc = cnc_connection
        self.connection_err = False
        self.poll_thread = threading.Thread(target=self.poll, args=(self,))
        self.poll_thread.daemon=True
        self.poll_thread.start()


    def poll(self, *args):
        ser = None
        while(1): #while polling
            if not ser:
                try:
                    ser = serial.Serial(self.port, 115200, timeout=0.1)
                except Exception as e:
                    if not self.connection_err:
                        event_msg = "CNC Pendant comm err: {}".format(e)
                        self.connection_manager.emit("new_event", event_msg)
                        self.connection_err = True
                    ser = None
            if ser:
                self.connection_err = False
                try:
                    ser.write("?".encode("ascii"))
                    data = b''
                    keep_going = 1
                    while keep_going:
                        b = ser.read() 
                        keep_going = len(b)
                        data+=b
                    self.cnc.tags["pendant-ticks"] = struct.unpack('l', data)[0]
                except Exception as e:
                    self.cnc.tags["pendant-ticks"] = None
                    event_msg = 'Pendant read error'
                    self.connection_manager.emit("new_event", event_msg)
            
            to = 0.2 if ser else 1.0
            time.sleep(to)
    """ Pendant program
#define TICKS_INIT 2147483648UL
#define A_pin 2
#define B_pin 3

volatile uint32_t ticks_abs = TICKS_INIT;
volatile int32_t ticks = ticks_abs - TICKS_INIT;
String readString;

void setup() {
    Serial.begin(115200);
    pinMode(A_pin, INPUT_PULLUP);
    pinMode(B_pin, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(A_pin), tick, CHANGE);
}

void loop() {
    
     while (Serial.available()) {
     delay(2);    //delay to allow byte to arrive in input buffer
     char c = Serial.read();
     readString += c;
 }
    if (readString.equals(String("?"))) {
        
     Serial.write((uint8_t *)&ticks, 4);
 }
 readString="";
}

void tick() {
    bool a = digitalRead(A_pin);
    bool b = digitalRead(B_pin);
    if(a == b){
        ticks_abs--;
    } else {
        ticks_abs++;
    }
    ticks = ticks_abs - TICKS_INIT;
    ticks = ticks/2;
}
"""



