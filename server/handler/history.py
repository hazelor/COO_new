from base import base_handler
import time
import json
from model.data import Data_Table_Map, Data, DataParser
from model.device_observed import Device_Observed
from model.device import Device

import tornado
import tornado.web



class data_history_handler(base_handler):
    @tornado.web.authenticated
    def get(self):
        usr = self.get_current_user()
        device_observed = Device_Observed()
        devices = device_observed.observed_devices(usr.id)
        if not devices or len(devices) < 1:
            return self.render('no_devices.html', user_name=usr.name, page_name="browser")

        sel_device_id = self.get_argument('sel_device_id','')
        sel_device = Device.get(sel_device_id)
        if sel_device_id == '':
            sel_device = devices[0]

        owners = DataParser.get_instance().get_owners(sel_device.dev_type)
        sel_owner = self.get_argument('owner','')
        if sel_owner == '':
            sel_owner = owners[0]


        data_infos = DataParser.get_instance().get_data_types(sel_device.dev_type, sel_owner)
        if data_infos and len(data_infos)>1:
            sel_data_info = data_infos[0]
        else:
            sel_data_info = None
        return self.render('history.html',
                           page_name = 'history',
                           devices = devices,
                           sel_device = sel_device,
                           sel_owner = sel_owner,
                           owners = owners,
                           data_infos =data_infos,
                           sel_data = sel_data_info,
                           user_name=usr.name)

    def post(self):
        usr = self.get_current_user()
        device_observed = Device_Observed()
        devices = device_observed.observed_devices(usr.id)
        if not devices or len(devices) < 1:
            return self.render('no_devices.html', user_name=usr.name, page_name="browser")

        sel_device_id = self.get_argument('sel_device_id','')
        sel_device = Device.get(sel_device_id)
        if sel_device_id == '':
            sel_device = devices[0]

        data_infos = DataParser.get_instance().get_data_types(sel_device.dev_type)
        return self.write(json.dumps(data_infos))


class data_history_device_handler(base_handler):
    def post(self):
        dev_id = self.get_argument('dev_id','')
        dev = Device.get(dev_id)
        if dev:
            dev_type = dev.dev_type
            res = DataParser.get_instance().get_owners(dev_type)
            res = json.dumps(res)
            self.write(res)

class data_history_owner_handler(base_handler):
    def post(self):
        dev_id = self.get_argument('dev_id','')
        owner = self.get_argument('owner','')
        dev = Device.get(dev_id)
        if dev:
            dev_type = dev.dev_type
            res = DataParser.get_instance().get_data_types(dev_type, owner)
            res = json.dumps(res)
            self.write(res)


class data_history_query_handler(base_handler):
    def get_data_info(self, tables, type_id, dev_id, owner, start_time, end_time):
        data_list = []
        for table in tables:
            data_list.extend(Data.find_by('where device_id = ? and type_id = ? and owner= ? and created_at between ? and ?', dev_id, type_id, owner, start_time, end_time, sub_name = str(table.index)))
        res = {}
        dev  = Device.get(dev_id)
        data_info = DataParser.get_instance().get_data_type(dev.dev_type, type_id, owner)
        res['name'] = data_info['name']
        res['type_id'] = data_info['type_id']
        res['unit'] = data_info['unit']
        res['values'] = []
        for data_item in data_list:
            res['values'].append([data_item.created_at*1000, data_item.value])
        return res

    def get(self):
        dev_id = self.get_argument('dev_id','')
        type_id = self.get_argument('type_id','')
        owner = self.get_argument('owner','')
        start_time=self.get_argument('start_time')+':00'
        start_time = time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
        end_time=self.get_argument('end_time')+':00'
        end_time = time.mktime(time.strptime(end_time, '%Y-%m-%d %H:%M:%S'))
        tables = Data_Table_Map.get_tables(start_time, end_time)

        if type_id != "":
            res = self.get_data_info(tables, type_id, dev_id, owner, start_time, end_time)
            self.write(json.dumps(res))
        else:
            dev = Device.get(dev_id)
            datas_info = DataParser.get_instance().get_data_types(dev.dev_type, owner)
            print "tables:---------",datas_info
            reses = []
            for di in datas_info:
                print di['type_id']
                reses.append(self.get_data_info(tables, di['type_id'], dev_id, di['owner'], start_time, end_time))
            self.write(json.dumps(reses))
