__author__ = 'guoxiao'

import serial
import ctypes, binascii
from macros import SERIAL_PORT_NAME, SERIAL_PORT_BAUD, SERIAL_PORT_TIMEOUT
from queueUtils import DataPool
from commUtils import *
from confUtils import *
import time
import random


class serialController(CountDownTimer):
    def __init__(self, seconds, start_pos, data_num):
        #self.ser = self.init_serial_port()
        #self.ser = self.open_serial_port(self.ser)
        self.ser = ""
        self.duration = seconds
        self.start_pos = start_pos
        self.data_num = data_num
        CountDownTimer.__init__(self, seconds)

    instance = None

    @staticmethod
    def get_instance():
        if serialController.instance == None:
            duration = get_update_duration()
            start_pos = get_serial_start_pos()
            data_num = get_serial_data_num()
            serialController.instance = serialController(duration,start_pos,data_num)
        return serialController.instance



    def init_serial_port(self):
        ser = serial.Serial(SERIAL_PORT_NAME, SERIAL_PORT_BAUD, timeout=SERIAL_PORT_TIMEOUT)
        return ser


    def open_serial_port(self, ser):
        if not ser.isOpen():
            ser.open()
        return ser


    def close_serial_port(self, ser):
        if ser.isOpen():
            ser.close()
        return ser

    def set_update_duration(self, duration):
        self.seconds = duration
        self.set_duration(self.seconds)

    def set_start_pos(self, start_pos):
        self.start_pos = start_pos

    def set_data_num(self, data_num):
        self.data_num = data_num

    def run(self):
        while True:
            CountDownTimer.run(self)
            self.exe_read_datas(self.ser, self.start_pos, self.data_num)
        



    @classmethod
    def int_to_hex_string(cls, data):
        s= hex(data)
        if len(s[2::])%2==1:
            s ="0" +s[2::]
            return s
        return s[2::]

    @classmethod
    def int_array_to_string(cls, array):
        if len(array) == 0:
            return ""
        s=""
        if not isinstance(array[0], int):
            return
        for item in array:
            s+=cls.int_to_hex_string(item)
        return s

    @classmethod
    def CRC16(cls, data):
        CRC16Lo = 0xff
        CRC16Hi = 0xFF
        CL = 0x01
        CH = 0xA0
        for i in range(len(data)):
            CRC16Lo ^= data[i]
            for Flag in range(8):
                SaveHi = CRC16Hi
                SaveLo = CRC16Lo
                CRC16Hi >>= 1
                CRC16Lo >>= 1
                if (SaveHi & 0x01) == 0x01:
                    CRC16Lo  |=0x80
                if (SaveLo & 0x01) == 0x01:
                    CRC16Hi  ^= CH
                    CRC16Lo  ^= CL
        return (CRC16Hi<<8)|CRC16Lo

    @classmethod
    def form_read_command(cls, addr, code, start_pos, end_pos):
        data=[]
        data.append(addr)
        data.append(code)
        data.append(start_pos/256)
        data.append(start_pos%256)
        data.append(end_pos/256)
        data.append(end_pos%256)
        crc =cls.CRC16(data)
        data.append(crc%256)
        data.append(crc/256)
        return data

    @classmethod
    def form_write_float_command(cls, addr, code, value, start_pos):
        data = []
        f_data = float_to_bytes(value)
        data.append(addr)
        data.append(code)
        data.append(start_pos/256)
        data.append(start_pos%256)
        data.append(0)
        data.append(2)
        data.extend(f_data)
        crc = cls.CRC16(data)
        data.append(crc%256)
        data.append(crc/256)
        return data
    

    def write_float(self, value, start_pos):
        command = serialController.form_write_float_command(1,6,value, start_pos)
        hexer = serialController.int_array_to_string(command).decode("hex")
        ser.write(hexer)
        ans = ser.readall()
        
    

    def exe_read_datas(self, ser, start_pos, num_data):

        command = serialController.form_read_command(1, 3, start_pos, num_data*2)
        hexer = serialController.int_array_to_string(command).decode("hex")
        #ser.write(hexer)
        #ans = ser.readall()
        ans = []
        serialController.construct_datas(ans, num_data)

    @classmethod
    def construct_datas(cls, ans, num_data):
        start_pos = 3
    
        c_res = {}
        c_res['mac'] = get_mac_address()
        c_res['data_content']={}
        c_res['data_content']['date'] = time.time()
        c_res['data_content']['content'] = []
        try:
            for i in range(num_data):
                c_res['data_content']['content'].append(random.random())
            #    c_res['content'].append(bytes_to_float(ans, i*4+start_pos))
            print c_res
            DataPool.get_instance().push_data(c_res)
        except:
            pass


if __name__ == '__main__':
    sc = serialController.get_instance()
    sc.start()
    for i in range(5):
        time.sleep(1.0)
    print "change the duration"

    sc.set_update_duration(20)
