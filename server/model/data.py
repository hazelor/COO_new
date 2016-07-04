#!/usr/bin/env python
# -*- coding: utf-8 -*-
from transwarp.db import next_id, transaction
from transwarp.orm import Model, StringField, BooleanField, FloatField, TextField, IntegerField
import time,os
import json
import redis
from util.marcos import DATA_INFOS_FILE_PATH, MAX_TABLE_LINES
from util import *
from transwarp import db
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class DataParser():
    
    __instance = None
    
    @staticmethod
    def get_instance():
        if DataParser.__instance == None:
            DataParser.__instance  = DataParser()
        return DataParser.__instance
    def __init__(self):
        self._data_infos = {}
        data_info_path = os.path.join(get_pwd_dir(), DATA_INFOS_FILE_PATH)
        with open(data_info_path,'r+') as dis:
            contents = dis.readlines()
            contents = [x.strip() for x in contents]
            json_str = ''.join(contents)
            #print "the json string:",json_str
            self._data_infos = eval(json_str)
            print self._data_infos

        self.chart_infos = {}
        for proj_type in PROJECT_TYPES:
            chart_conf_filename = 'chart_%s.conf'%(proj_type)
            file_path = os.path.join(CONF_DIR,chart_conf_filename)
            with open(file_path,'r+') as f:
                lines = f.readlines()
                lines = [line.strip() for line in lines]
                self.chart_infos[proj_type] = eval(''.join(lines))

    def has_proj_type(self, proj_type):
        return self.chart_infos.has_key(proj_type)

    def get_chart_info(self, proj_type):
        if self.has_proj_type(proj_type):
            return self.chart_infos[proj_type]
        else:
            return {}

    def get_owners(self, dev_type):
        owners_list = []
        print dev_type
        for dev_info in self._data_infos:
            if dev_info['dev_type'] == dev_type.strip():
                for data_info in dev_info['data_content']:
                    if not data_info['owner'] in owners_list:
                        owners_list.append(data_info['owner'])
        print owners_list
        return owners_list

    def get_data_types(self, dev_type, owner):
        data_type_list = []
        for dev_info in self._data_infos:
            if dev_info['dev_type'] == dev_type:
                for data_info in dev_info['data_content']:
                    if data_info['owner'] == owner:
                        data_type_list.append(data_info)
        return data_type_list
    def has_type(self, dev_type):
        for dev_info in self._data_infos:
            if dev_info['dev_type'] == dev_type.strip():
                return True
        return False
    #def get_data_types(self, dev_type):
    #    for dev_info in self._data_infos:
    #        if dev_info['dev_type'] == dev_type.strip():
    #            return dev_info['data_content']
    #    return []

    def get_data_type(self, dev_type, type_id, owner):
        for dev_info in self._data_infos:
            if dev_info['dev_type'] == dev_type:
                for data_info in dev_info['data_content']:
                    if data_info['owner'] == owner and data_info['type_id']==type_id:
                        return data_info
        return []

    def get_data_info(self, dev_type, type_id, owner):
        for dev_info in self._data_infos:
            if dev_info['dev_type'] == dev_type.strip():
                for data_info in dev_info['data_content']:
                    if data_info['type_id'] == type_id.strip() and data_info['owner'] == owner:
                        return data_info
        return {}
    def parse_dev(self,  table_index, dev_id, dev_type, data_content):
        table_index = int(table_index)
        if Data.count_all(sub_name = str(table_index)) > MAX_TABLE_LINES:
            table_index+=1
            cdtm = Data_Table_Map.find_first("where `index` = ?", table_index)
            if cdtm == None:
                Data_Table_Map.add_table(table_index)
        with transaction() as tr:
            for dev_info in self._data_infos:
                if dev_info['dev_type'] == dev_type.strip():
                    for index in range(len(dev_info['data_content'])):
                        pos = (dev_info['data_content'][index]['start_pos']-1)/2
                        d = Data(device_id = dev_id,
                                 type_id = dev_info['data_content'][index]['type_id'],
                                 owner=dev_info['data_content'][index]['owner'],
                                 value = data_content[pos])
                        d.insert(sub_name=str(table_index))

        cdtm = Data_Table_Map.find_first("where `index` = ?", table_index)
        cdtm.end_time = time.time()
        cdtm.update()

    def parse_to_json(self, dev_type, data_content, date):
        res = []
        for dev_info in self._data_infos:
            if dev_info['dev_type'] == dev_type.strip():
                for index in range(len(dev_info['data_content'])):
                    pos = (dev_info['data_content'][index]['start_pos']-1)/2
                    res.append({'name':dev_info['data_content'][index]['name'],
                                'type_id':dev_info['data_content'][index]['type_id'],
                                'unit':dev_info['data_content'][index]['unit'],
                                'owner':dev_info['data_content'][index]['owner'],
                                'value': data_content[pos]})
        return {"date":date, 'content':res}



class Data(Model):
    __table__ = 'col_data'

    id = StringField(primary_key=True, ddl='varchar(32)', default=next_id)
    device_id = StringField(ddl='varchar(50)')
    type_id = StringField(ddl='varchar(50)')
    value = FloatField(ddl='double')
    owner = StringField(ddl='varchar(50)')
    created_at = FloatField(ddl='double', updatable=False, default=time.time)


class Data_Table_Map(Model):
    id = StringField(primary_key=True, ddl='varchar(32)', default=next_id)
    start_time = FloatField(ddl='double',  default=time.time)
    end_time = FloatField(ddl='double')
    index = IntegerField()

    @classmethod
    def get_last_table_index(cls):
        if cls.count_all() == 0:
            return 0
        else:
            data_table = cls.find_first('order by start_time desc')
            if data_table:
                return data_table.index
            else:
                return 0
    @classmethod
    def add_table(cls,index):
        r = redis.Redis()
        dt = Data()
        dt.create_table(sub_name = str(index))
        r.set("last_data_table_index",index)
        new_table = Data_Table_Map()
        new_table.end_time = time.time()
        new_table.index = index
        new_table.insert()
    
    

    @classmethod
    def get_tables(cls, start_time, end_time):
        return cls.find_by('where start_time<? and end_time>?', end_time, start_time)

     



if __name__=="__main__":
    db.create_engine('sonic513', 'sonic513', 'tobacco_monitor', host='127.0.0.1',port='3306')
    dtm = Data_Table_Map()
    print dtm.find_first("where 'index'=?",index)

