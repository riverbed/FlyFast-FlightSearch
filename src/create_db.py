from datetime import timedelta
import datetime
import json
import logging
from multiprocessing import connection
import random
import sqlite3
import os
import time
from pyparsing import Word 
from os.path import exists

TIME_FORMAT = "%H:%M"
MAX_AREA_CODE = 50
ZONES = 3
FLIGHT_FREQUENCY = 8


DATABASE_FILENAME = "flight_search.db"
EXTERNAL_DATA_FOLDER = "external_data"

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

       
Local_Path = os.path.dirname(os.path.realpath(__file__))

class CreateDB():

    def create(self):   
              
        parent_dir = os.path.dirname(Local_Path)
        database_file = os.path.join(parent_dir, "database", DATABASE_FILENAME )       

        if exists(database_file):
            os.remove(database_file)

        self.connection = sqlite3.connect(database_file)

        cursor = self.connection.cursor()
        sql_file = open(os.path.join(Local_Path,"create_db.sql"))
        sql_as_string = sql_file.read()
        cursor.executescript(sql_as_string)
        
    def get_zone(self, worldAreaCode):

        for ndx, zone in enumerate(self.zones):        
            if worldAreaCode in zone:
                return ndx

        print("**ERROR: Unexpected worldAreaCode " + str(worldAreaCode))
        return 0

    def make_zones(self):
        zoneSize = MAX_AREA_CODE//ZONES
        self.zones = []
        start = 0
        
        for x in range(ZONES):
            stop = start + zoneSize + 1
            if x == ZONES -1:
                stop = MAX_AREA_CODE + 1

            self.zones.append(range(start, stop ))
            start = stop - 1

    def load_airports_new(self):

        parent_dir = os.path.dirname(Local_Path)
        json_file= open(os.path.join(parent_dir, EXTERNAL_DATA_FOLDER, "AirportsData.json"), "r")

        jsonAirports = json.load(json_file)
        start = datetime.datetime.now()
        
        logging.info("Data source items: " + str(len(jsonAirports)))

        
        query = "INSERT INTO Airport (AirportCode, AirportName, City, Region, Country, WorldAreaCode, Zone) VALUES"
       
        for item in jsonAirports:
            if item['code'] <= MAX_AREA_CODE:
                query += " ('{}', '{}', '{}', '{}', '{}', {}, {}),".format(item['value'], 
                item['name'].replace("'","''",-1), item['city'].replace("'","''",-1), item['city'].replace("'","''",-1) + " " + item['country'].replace("'","''",-1),
                item['country'].replace("'","''",-1), item['code'], self.get_zone(item['code']))
        
        query = query.rstrip(',')   + ';'      
        cursor = self.connection.cursor()
        cursor.execute(query)

    def makeFlightsNew(self):
    
        flights = []
        logging.info("creating database")
        self.make_zones()
        self.create()

        self.load_airports_new()
    
        logging.info("finding airports of interest(airport area code <= {})".format(MAX_AREA_CODE))
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Airport where WorldAreaCode < {} ORDER BY WorldAreaCode".format(MAX_AREA_CODE))           
        airports = cursor.fetchall()
        
        logging.info("Number of airports used: " + str(len(airports)))
        airlines = ["ABC Airways", "YBZ Airlines", "MNL Airways", "FGH Airlines", "KLN Airways", "LPS Airways"]

        query = "INSERT INTO Flight (Src, Dst, Departure, Arrival, Airline, FlightNum, Fare) VALUES"

        dt = datetime.datetime.now()
        delta = timedelta(hours=FLIGHT_FREQUENCY)
        start = datetime.datetime.now()   

        logging.info("Building Flight  data...")    
        for src in airports:
        
            dt = dt.replace(year=2022, month= 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            for dst in airports:   
                if dst[0] is not src[0] and abs(dst[6] - src[6]) <= 1:
                    for flt_time in range(0,24, FLIGHT_FREQUENCY):
                    
                        dt = dt + delta
                        departure = dt.strftime(TIME_FORMAT)
                            
                        arrivalSpan = abs(dst[6] - src[6])  + 1
                       
                        dt = dt + timedelta(hours=arrivalSpan)
                        arrival = dt.strftime(TIME_FORMAT)

                        random.seed(arrival)
                        airline = airlines[random.randint(0, len(airlines) -1)]

                        random.seed(src[0] + dst[0] + departure + arrival + airline)
                        flightNum = random.randint(100, 1000)
                        
                        random.seed(src[0] + dst[0] + departure + arrival + airline + str(flightNum))
                        fare = random.randint(100, 900)
                        
                        query += "('{}', '{}', '{}', '{}', '{}', {}, {}),".format(src[0],
                            dst[0], departure, arrival, airline, flightNum, fare)
                    
        query = query.rstrip(',')   + ';'      
        print (datetime.datetime.now() - start)
        logging.info("Inserting Flight  data...")   
        cursor.execute(query)      

        query = "DROP TABLE IF EXISTS [AirportWithCode];"
        cursor.execute(query)
        query = "DROP TABLE IF EXISTS [AirportWithName];"
        cursor.execute(query)

        self.connection.commit()
        self.connection.close()
        logging.info("Database creation is complete")
    

# obj = CreateDB()
# obj.makeFlights()

obj = CreateDB()
obj.makeFlightsNew()