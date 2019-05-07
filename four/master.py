import sys
sys.path.append("..")

from crawlServer import CrawlServer
import protocol_constants as pc
import json
import time
import threading
# mongo db

import signal

constants = {
    "reorder_period": 1200, # 20 mins
    "connection_lost_period": 30, # 30s
}

class CrawlMaster:
    clients = dict()
    server_status = pc.STATUS_RUNNING
    last_reorder_time = time.time()

    def __init__(self):
        self.server = CrawlServer(self.on_message)
        self.server.start()

    def on_message(self, msg):
        request = json.loads(msg)
        ty = request[pc.MSG_TYPE]

        client_state = dict()

        response = dict()
        response[pc.SERVER_STATUS] = self.server_status

        # 注册 / 反注册流程
        if pc.REGISTER == ty:
            client_id = self.get_free_id()
            client_state["status"] = pc.STATUS_RUNNING
            client_state["time"] = time.time()
            self.clients[client_id] = client_state
            return client_id
        elif pc.UNREGISTER == ty:
            client_id = request.get(pc.CLIENT_ID)
            del self.clients[client_id]
            return json.dumps(response)

        client_id = request.get(pc.CLIENT_ID)
        if not client_id:
            response[pc.ERROR] = pc.ERR_NOT_FOUND
            return json.dumps(response)
        # 心跳
        if pc.HEARTBEAT == ty:
            if self.server_status is not self.clients[client_id]["status"]:
                if pc.STATUS_RUNNING == self.server_status:
                    response[pc.ACTION_REQUIRED] = pc.RESUME_REQUIRED
                elif pc.STATUS_PAUSED == self.server_status:
                    response[pc.ACTION_REQUIRED] = pc.PAUSE_REQUIRED
                elif pc.STATUS_SHUTDOWN == self.server_status:
                    response[pc.ACTION_REQUIRED] = pc.SHUTDOWN_REQUIRED
                return json.dumps(response)
        else:
            client_state["status"] = ty
            client_state["time"] = time.time()
            self.clients[client_id] = client_state

        return json.dumps(response)

    def get_free_id(self):
        idx = 0
        for key in self.clients.keys():
            if idx < int(key):
                break
            idx += 1
        return str(idx)


