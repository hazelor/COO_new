#!/usr/bin/env python
# coding=utf-8
import os
from macros import *
import json

def start_mqtt_server():
    command = "sudo mosquitto -d"
    os.system(command)


def publish_info(subject, info):
    j_info = json.dumps(info)
    command = "sudo mosquitto_pub -h %s -p %s -t %s -m %s" % (MQTT_HOST, MQTT_PORT, subject, j_info)
    os.system(command)

