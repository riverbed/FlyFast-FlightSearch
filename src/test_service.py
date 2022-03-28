import os
from tornado_inst import BaseRequestHandler

LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DATA_FOLDER = "app_data"

class TestServiceHandler(BaseRequestHandler):
    def get(self):
        with open(os.path.join(os.path.dirname(LOCAL_DIR), APP_DATA_FOLDER, "index.html"), "r") as infile:
            response = infile.read()        
        self.write(response)     