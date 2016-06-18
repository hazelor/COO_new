__author__ = 'guoxiao'

from macros import *
import copy, ConfigParser


def get_update_duration():
    cr = ConfigParser.RawConfigParser()
    cr.read("./config.conf")
    return cr.getint("main", "duration")


def set_update_duration(duration):
    cr = ConfigParser.RawConfigParser()
    cr.read("./config.conf")
    cr.set("main", "duration", str(duration))
    cr.write(open("./config.conf","w"))

def get_serial_start_pos():
    cr = ConfigParser.RawConfigParser()
    cr.read("./config.conf")
    return cr.getint("serial","start_pos") 

def get_serial_data_num():
    cr = ConfigParser.RawConfigParser()
    cr.read("./config.conf")
    return cr.getint("serial","data_num")

def set_serial_start_pos(param):
    cr = ConfigParser.RawConfigParser()
    cr.read("./config.conf")
    cr.set("serial", "start_pos", str(param))
    cr.write(open("./config.conf","w"))

def set_serial_start_pos(param):
    cr = ConfigParser.RawConfigParser()
    cr.read("./config.conf")
    cr.set("serial", "data_num", str(param))
    cr.write(open("./config.conf","w"))

