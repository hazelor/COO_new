#!/usr/bin/env python
#--coding:utf-8--

__author__ = 'guoxiao'

import json
import os
import urllib2
from commUtils import *
from confUtils import *
from queueUtils import DataPool
from macros import *

class updateController(CountDownTimer):
    def __init__(self, seconds):
        self.duration = seconds
        CountDownTimer.__init__(self, seconds)

    instance = None

    @staticmethod
    def get_instance():
        if updateController.instance == None:
            duration = get_update_duration()
            updateController.instance = updateController(duration)
        return updateController.instance

    def update_data(self, c_data):
        url = "http://{0}:{1}{2}".format(SERVER_URL, UPDATE_PORT, API_DATACHANNEL_URL)
        j_data = json.dumps(c_data)
        req = urllib2.Request(url, j_data)
        try:
            res = urllib2.urlopen(req, timeout = 30)
            if res.read().strip() == RES_SUCCESS:
                return True
            else:
                return False
        except Exception as e:
            print "error!",e
            return False

    def set_update_duratioon(self, duration):
        self.duration = duration
        self.set_duration(self.duration)

    def run(self):
        while True:
            CountDownTimer.run(self)
            self.exe_update()

    def exe_update(self):
        dp = DataPool.get_instance()
        length = dp.get_len() if dp.get_len()<10 else 10
        print 'len:',dp.get_len()

        c_datas = []
        for i in range(length):
            res = dp.pull_data()
            if res:
                c_datas.append(res)
        if c_datas:
            res = self.update_data(c_datas)
            print 'res:',res
            if not res:
                dp.g_counts_reboot+=1
                if dp.g_counts_reboot>10:
                    os.system("sudo reboot")
                for cd in c_datas:
                    dp.push_data(cd)


