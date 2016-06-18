# coding=utf-8
from base import base_handler
import tornado, tornado.web

class manager_handler(base_handler):
    @tornado.web.authenticated
    def get(self):
        pass

class manager_user_handler(base_handler):
    @tornado.web.authenticated
    def get(self):
        pass

class manager_device_handler(base_handler):
    @tornado.web.authenticated
    def get(self):
        pass

