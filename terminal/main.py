__author__ = 'guoxiao'

from serialUtils import *
from updateUtils import *
from commUtils import *
from mqttUtils import *
import os, time

if __name__ == "__main__":
    #sync time for devies
    print "start sync time"
    #os.system("ntpdate -u ntp.api.bz")
    print "end sync time"
    #mqttCtrler = mqttController.get_instance()
    serialCtrler = serialController.get_instance()
    updateCtrler = updateController.get_instance()
    #mqttCtrler.start()
    serialCtrler.start()
    updateCtrler.start()
    
