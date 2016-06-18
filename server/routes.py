__author__ = 'sonic-server'

from handler import *
handlers = [
    (r'/', home_handler),
    (r'/data/preview',data_preview_handler),
    (r'/data/preview/realtime', data_preview_realtime_handler),
    (r'/data/conf',data_conf_handler),
    (r'/data/history',data_history_handler),
    (r'/data/history/query', data_history_query_handler),
    (r'/data/history/device', data_history_device_handler),
    (r'/data/history/owner', data_history_owner_handler),
    (r'/api/data', api_data_handler),
    (r'/login', login_handler),
    (r'/logout', logout_handler),
    #(r'/register',register_handler),
    #(r'/setting', setting_handler),
    #(r"/setting/(\w+)",setting_handler),
    #(r"/manager", manager_handler),
    #(r"/manager/user",manager_user_handler),
    #(r"/manager/device",manager_device_handler),

]

modules = {}
