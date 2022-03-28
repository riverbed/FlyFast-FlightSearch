from datetime import datetime
import os
import random
from select import select
import sqlite3
from xmlrpc.client import DateTime
import tornado.ioloop
import tornado.options
from tornado.web import Application, StaticFileHandler
from tornado.template import Template
from tornado_inst import BaseRequestHandler
import logging
logging.basicConfig()
import time
import simplejson as json
from datetime import timedelta



LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_FILENAME = "flight_search.db"


 # 1 hour in Julian day
MIN_CONNECTION_TIME = 0.0416666667 

# 3 hour in Julian day
MAX_CONNECTION_TIME = 0.125

PORT = 8080

class TemplateHandler(BaseRequestHandler):
    def get(self):
        with open(os.path.join(os.path.dirname(LOCAL_DIR), "templates", "index.html.template"), "r") as infile:
            response = infile.read()
        
        self.write(response)     

class SearchFlightHandler(BaseRequestHandler):
    def ConnectToDB(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(dir_path)
        database_file = os.path.join(parent_dir, "database", DATABASE_FILENAME )
        return sqlite3.connect(database_file)

    def find_flights(self, departureDate, src, dst, seatType ):
      
        flightSearchResponse = []       

        query = "SELECT * FROM Flight WHERE src='{}' AND dst='{}'".format(src, dst)
        connection = self.ConnectToDB()
        cursor = connection.cursor()
        cursor.execute(query)
        # available_flights = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        direct_flights = cursor.fetchall()

        if len(direct_flights) > 0:
            for direct_flight in direct_flights:
                flight_detail = self.set_flight_attributes( departureDate, direct_flight, seatType)

                flight =  {
                "from": src, 
                "to": dst, 
                "flights": [],
                "departureTime": flight_detail['departureTime'], 
                "arrivalTime": flight_detail['arrivalTime'],
                "fare": flight_detail['fare'],
                }
                flight['flights'].append( flight_detail)
                flightSearchResponse.append(flight)
            
        else:           

            query = """SELECT *
            FROM Flight AS StartFlight
            INNER JOIN Flight AS EndFlight
            ON StartFlight.Dst = EndFlight.Src 
            WHERE StartFlight.Src = '{}' AND  EndFlight.Dst = '{}' 
            AND StartFlight.Arrival < EndFlight.Departure 
            AND abs( julianday(StartFlight.Arrival)- julianday(EndFlight.Departure) )
            BETWEEN {} AND {};""".format(src, dst, MIN_CONNECTION_TIME, MAX_CONNECTION_TIME)
           
            cursor = connection.cursor()
            cursor.execute(query)
            connected_flights = cursor.fetchall()
                
            for itinerary in connected_flights:
                start_flight = self.set_flight_attributes( departureDate, itinerary[0:8], seatType)
                end_flight = self.set_flight_attributes( departureDate, itinerary[8:16], seatType)

                flight =  {
                "from": src, 
                "to": dst, 
                "flights": [],
                "departureTime": start_flight['departureTime'], 
                "arrivalTime": end_flight['arrivalTime'],
                "fare": start_flight['fare'] + end_flight['fare'],
                }
                flight['flights'].append(start_flight)
                flight['flights'].append(end_flight)
                flightSearchResponse.append(flight)
           
                   
        # print(flightSearchResponse)
        connection.close()
        return flightSearchResponse
    
    def set_flight_attributes(self, departureDate, row, seatType = 'Economy'):
              
        departure_str = departureDate + " " + row[3]
        tm_struct = time.strptime(departure_str, "%m-%d-%Y %H:%M")
        departure_dt = datetime(tm_struct.tm_year, tm_struct.tm_mon, tm_struct.tm_mday, tm_struct.tm_hour, tm_struct.tm_min)
        
        departureTimeStruct = time.strptime(row[3], "%H:%M")
        arrivalTimeStruct = time.strptime(row[4], "%H:%M")        
        dt_departure = datetime.fromtimestamp(time.mktime(departureTimeStruct))
        dt_arrival = datetime.fromtimestamp(time.mktime(arrivalTimeStruct))
        diff = dt_arrival - dt_departure
        arrival_dt =  departure_dt + timedelta(seconds=diff.seconds)        

        flight = {}
        flight["departureTime"] =  departure_dt.strftime("%m-%d-%Y %H:%M")
        flight["arrivalTime"] = arrival_dt.strftime("%m-%d-%Y %H:%M")
        flight["departureTime"] =  departure_dt.strftime("%m-%d-%Y %H:%M")
        flight["arrivalTime"] = arrival_dt.strftime("%m-%d-%Y %H:%M")
                    
        flight["from"] = row[1]
        flight["to"] = row[2]
        flight["seat"] = seatType
        flight["airline"] = row[5]
        flight["flightNumber"] = row[6]
        
        fare = row[7]
        if seatType == "Premium Enconomy":
            fare = fare  + fare * 0.25
        if seatType == "Buisiness":
            fare = fare  + fare * 0.5
        if seatType == "First":
            fare = fare  + fare * 0.75

        flight["fare"] = fare
        flight["id"] = row[0]
        return flight
        

    def handle_request(self):
      
        flights = []
        searchParams  = json.dumps({ k: self.get_argument(k) for k in self.request.arguments })
        print ("flight search parameters received: " + searchParams)

        departure = datetime.now().strftime("%m-%d-%Y")
        if 'departure' in searchParams:
             departure = self.get_argument('departure')

        seatype = 'Economy'
        if 'seat' in searchParams:
             seatype = self.get_argument('seat')

        departingFlights = self.find_flights(departure, self.get_argument('from'), self.get_argument('to'), seatype)
        flights.append(departingFlights)

        if 'return' in searchParams:
            print("round trip")           
            departure = self.get_argument('return')
            returnFlights = self.find_flights(departure, self.get_argument('to'), self.get_argument('from'), seatype)
            flights.append(returnFlights)
        
        result = json.dumps(flights)
        self.write(result)
        

    def get(self):       
       self.handle_request()
        
    def post(self):
        self.handle_request()







