__author__ = 'guoxiao'
import paho.mqtt.client as mqtt
from commUtils import get_mac_address,CountDownTimer
from confUtils import *
from macros import *
from serialUtils import serialController
from updateUtils import updateController
import json

def on_connect(client, userdata, flags, rc):
    print "connected with result code:"+str(rc)
    client.subscribe(get_mac_address()+"_duration_param")
    client.subscribe(get_mac_address()+"_PID_param")
    client.subscribe(get_mac_address()+"_serial_param")

def on_message(client, userdata, msg):
    print msg.topic+" "+str(msg.payload)
    if msg.topic == get_mac_address()+"_duration_param":
        on_duration_set(str(msg.payload))
        return
    if msg.topic == get_mac_address()+"_PID_param":
        on_PID_set(str(msg.payload))
        return
    if msg.topic == get_mac_address()+"_serial_param":
        on_serial_set(str(msg.payload))
        return

def on_duration_set(payload):
    j_data = json.loads(payload)
    duration = j_data['duration']
    set_update_duration(duration)
    serialController.get_instance().set_update_duration(duration)
    updateController.get_instance().set_update_duration(duration)
    


def on_PID_set(payload):
    j_data = json.loads(payload)
    param_P = float(j_data['P']['value'])
    param_P_start_pos = int(j_data['P']['start_pos'])


    param_I = float(j_data['I']['value'])
    param_I_start_pos = int(j_data['I']['start_pos'])

    param_D = float(j_data['D']['value'])
    param_D_start_pos = int(j_data['D']['start_pos'])
    serialController.get_instance().write_float(param_P, param_P_start_pos)
    serialController.get_instance().write_float(param_I, param_I_start_pos)
    serialController.get_instance().write_float(param_D, param_D_start_pos)


def on_serial_set(payload):
    j_data = json.loads(payload)
    start_pos = j_data['start_pos']
    data_num = j_data['data_num']
    set_serial_start_pos(start_pos)
    set_serial_data_num(data_num)
    serialController.get_instance().set_start_pos(start_pos)
    serialController.get_instance().set_data_num(data_num)


class mqttController(CountDownTimer):
    def __init__(self):
        self.duration = 10
        self.client = mqtt.Client()
        self.client.on_message = on_message
        self.client.on_connect = on_connect
        CountDownTimer.__init__(self, self.duration)

    instance = None
    @staticmethod
    def get_instance():
        if mqttController.instance == None:
            mqttController.instance = mqttController()
        return mqttController.instance

    def run(self):
        while True:
            try:
                self.client.connect(HOST_ADDRESS, HOST_MQTT_PORT, MQTT_TIMEOUT)
                self,client.loop_forever()
            except:
                print "connect disable! and try after 10 seconds"
                pass
            CountDownTimer.run(self)
        


        
    
if __name__=="__main__":
    pass
