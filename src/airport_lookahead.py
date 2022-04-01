import json
from tornado_inst import BaseRequestHandler
import airport_search

class AirportLookAheadHandler(BaseRequestHandler):
    
    def handle_request(self):
        
        searchParams  = json.dumps({ k: self.get_argument(k) for k in self.request.arguments })
        searchTxt = self.get_argument('searchtxt')
        limit = 15
        if 'limit' in searchParams:
            limit = self.get_argument('limit')
        airports = airport_search.search_airports_containing(searchTxt, self.span_context)
        self.write(airports)

    def get(self):       
       self.handle_request()
        
    def post(self):
        self.handle_request()    