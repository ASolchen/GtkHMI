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
import gi
gi.require_version('Gtk', '3.0')
import time
from gi.repository import GObject
from backend.widget_classes.widget import Widget # for static methods
import sqlite3
from io import StringIO
from sqlite3 import Error






class AlarmEventViewHandler(object):
    def __init__(self, app):
        self.app = app
        self.connection_manager = app.connection_manager
        self.file_db = sqlite3.connect("event_log.db")
        c = self.file_db.cursor()
        try:
            table = c.execute("SELECT * FROM [alarms] LIMIT 1",[])
        except sqlite3.OperationalError:
            c.execute(
"""
CREATE TABLE "Alarms" (
	"ID"	INTEGER,
	"Timestamp"	INTEGER,
	"EventID"	INTEGER,
	"EventType"	TEXT,
	"State"	INTEGER,
	PRIMARY KEY("ID" AUTOINCREMENT)
)
"""
            )
        self.file_db.commit()
        #self.factory = app.widget_factory
        self.subscriber = "__ALARM_AND_EVENT_HANDLER__"
        GObject.timeout_add(1000, self.update)

    def update(self, *args):
        ts = time.time()
        if not self.app.db_manager.table_exists("AlarmsEvents"):
            self.create_viewer_alarm_table()
        alarm_rows = self.app.db_manager.run_query(
            'SELECT [ID], [Indication] FROM [AlarmEventConfig] WHERE [Enable] = 1;'
        )
        for alm in alarm_rows:
            state = self.connection_manager.evaluate_expression(self, alm["Indication"], self.subscriber)
            last_state_row = self.app.db_manager.get_rows("AlarmsEvents",["ID","State"], match_col="ID", match=alm["ID"])
            if not len(last_state_row):
                alarm_cfg_rows = self.app.db_manager.run_query('SELECT [Message],[Severity] FROM [AlarmEventConfig] WHERE [ID] = ?;',[alm["ID"]])
                msg = alarm_cfg_rows[0]["Message"]
                severity = alarm_cfg_rows[0]["Severity"]
                if state:
                    on_ts = ts
                    off_ts = None
                else:
                    off_ts = ts
                    on_ts = None
                self.app.db_manager.run_query("""INSERT INTO [AlarmsEvents] ([ID],[Message],[Severity],[State], [EventOnTimestamp], 
                        [EventOffTimestamp], [AckState], [AckTimestamp])    VALUES (?,?,?,?,?,?,?,?)""",[alm["ID"],msg, severity, state, 
                        on_ts, off_ts, 0,None])
                last_state = -1 #bad quality, first read
            else:
                last_state = last_state_row[0]["State"]
            if last_state != state:
                self.file_db.cursor().execute("""INSERT INTO [Alarms] ([Timestamp],[EventID],[EventType],[State])
                VALUES (?,?,?,?)""", [ts, alm["ID"], "STATE", state])
                self.file_db.commit()
                update_col = "EventOnTimestamp" if state else "EventOffTimestamp"
                self.app.db_manager.run_query("""UPDATE [AlarmsEvents] SET [State]=?, [{}]=? WHERE [ID]=?""".format(update_col),
                [state, ts, alm["ID"]])
                self.connection_manager.emit("tag_update", self.subscriber) #just let widgets know to update
        return True

    def evaluate_expression(self, expression):
        #reads the expression, parses out the tags required, then replaces thier values and runs it
        #returns value if successful or None if tag read or script error
        expression_val = None
        if expression:
            tags = Widget.get_tags_required(expression)
            if len(tags):
                update = self.app.db_manager.get_sub_vals(self.subscriber, tags)
                if len(update):
                    for tag in tags:
                        if not tag in update or type(update[tag]["Value"]) == type(None):
                            #log error? expression cannot be evaluated with all tags
                            return expression_val #None
                        expression = expression.replace("{{{}}}".format(tag),str(update[tag]["Value"]))
            try:
                locs = locals()
                exec("expression_val = {}".format(expression), globals(), locs)
                expression_val = locs["expression_val"]
            except Exception as e:
                print(e)
                expression_val = None
        return expression_val

    def create_viewer_alarm_table(self):
        self.app.db_manager.run_query("""
CREATE TABLE "AlarmsEvents" (
	"ID"	INTEGER NOT NULL,
	"Enable"	INTEGER DEFAULT 1,
	"Message"	REAL DEFAULT ALARM,
	"Indication"	TEXT,
	"Severity"	INTEGER DEFAULT 500,
	"State"	INTEGER DEFAULT -1,
	"EventOnTimestamp"	NUMERIC,
	"EventOffTimestamp"	NUMERIC,
	"AckState"	INTEGER DEFAULT 0,
	"AckTimestamp"	REAL,
	PRIMARY KEY("ID" AUTOINCREMENT)
)""", [])


#temp table
"""
CREATE TABLE "AlarmsEvents" (
                    "ID"	INTEGER NOT NULL,
                    "Message"	TEXT DEFAULT "ALARM",
                    "Severity"	INTEGER DEFAULT 500,
                    "State"	INTEGER,
                    "EventOnTimestamp"	NUMERIC,
                    "EventOffTimestamp"	NUMERIC,
                    "AckState"	INTEGER,
                    "AckTimestamp"	NUMERIC,
                    PRIMARY KEY("ID" AUTOINCREMENT)
                )
"""


#historic log
"""
CREATE TABLE "Alarms" (
	"ID"	INTEGER,
	"Timestamp"	INTEGER,
	"EventID"	INTEGER,
	"EventType"	TEXT,
	"State"	INTEGER,
	PRIMARY KEY("ID" AUTOINCREMENT)
)
"""
#alarm config in project db
"""
CREATE TABLE "AlarmEventConfig" (
	"ID"	INTEGER,
	"Message"	TEXT,
	"Severity"	INTEGER,
	"Enable"	INTEGER,
	"Indication"	TEXT,
	PRIMARY KEY("ID" AUTOINCREMENT)
)
"""