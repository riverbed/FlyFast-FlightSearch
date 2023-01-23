from datetime import timedelta
import datetime
import json
import logging
from multiprocessing import connection
import random
import sqlite3
import os
import time
from os.path import exists

TIME_FORMAT = "%H:%M"
MAX_AREA_CODE = 1000
ZONES = 20
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
        index = (worldAreaCode - 1) // (MAX_AREA_CODE // ZONES)

        if index >= ZONES:
            print("**ERROR: Unexpected worldAreaCode " + str(worldAreaCode))
            return None
        return index

    # No longer in use
    def make_zones(self):
        zoneSize = MAX_AREA_CODE // ZONES
        self.zones = []
        for x in range(ZONES):
            start = (x * zoneSize) + 1
            end = ((x + 1) * zoneSize) + 1
            self.zones.append(range(start, end))

    def load_airports(self):

        parent_dir = os.path.dirname(Local_Path)
        json_file= open(os.path.join(parent_dir, EXTERNAL_DATA_FOLDER, "AirportsData.json"), "r")

        jsonAirports = json.load(json_file)
        
        logging.info("Data Source Items: " + str(len(jsonAirports)))
        
        query = "INSERT INTO Airport (AirportCode, AirportName, City, Country, WorldAreaCode, Zone) VALUES"
       
        for airport in jsonAirports:
            if airport['code'] <= MAX_AREA_CODE:
                zone = self.get_zone(airport['code'])
                if zone != None:
                    query += " ('{}', '{}', '{}', '{}', {}, {}),".format(
                        airport['value'],
                        airport['name'].replace("'","''",-1),
                        airport['city'].replace("'","''",-1),
                        airport['country'].replace("'","''",-1),
                        airport['code'],
                        zone
                    )
        
        logging.info("Successfully Added Airport Data!")
        query = query.rstrip(',') + ';'
        cursor = self.connection.cursor()
        cursor.execute(query)

    def create_flights(self, airports):
        airlines = [
            "Software Airlines",
            "Developer Airlines",
            "Coder Airlines",
            "Designer Airlines",
            "Engineer Airlines",
            "Programmer Airlines",
            "Analyzer Airlines",
            "Deployment Airlines",
            "IT Airlines"
        ]

        query = "INSERT INTO Flight (Src, Dst, Departure, Arrival, Airline, FlightNum, Fare) VALUES"

        dt = datetime.datetime.now()
        delta = timedelta(hours=FLIGHT_FREQUENCY)
        start = datetime.datetime.now()   

        for src in airports:
            dt = dt.replace(year=2022, month= 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            for dst in airports:
                if src[0] == dst[0] or abs(src[5] - dst[5]) > (ZONES // 2):
                    continue
                
                for flt_time in range(0, 24, FLIGHT_FREQUENCY):
                    dt = dt + delta
                    departure = dt.strftime(TIME_FORMAT)
                        
                    arrivalSpan = abs(dst[5] - src[5])  + 1
                    
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
                    
        query = query.rstrip(',') + ';'
        logging.info("Saving Flight Data...")
        cursor = self.connection.cursor()
        cursor.execute(query)
    
    def createFlightSearch(self):
        logging.info("Creating Database")
        
        # self.make_zones()
        self.create()

        logging.info("Loading Airports")
        self.load_airports()
    
        logging.info("Finding Airports of Interest (Airport Area Code <= {})".format(MAX_AREA_CODE))
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Airport where WorldAreaCode <= {} ORDER BY WorldAreaCode".format(MAX_AREA_CODE))
        airports = cursor.fetchall()
        
        logging.info("Number of Airports Used: " + str(len(airports)))

        logging.info("Creating Flights")
        self.create_flights(airports)

        self.connection.commit()
        self.connection.close()
        logging.info("Database Creation is Complete!")
    

# obj = CreateDB()
# obj.makeFlights()

obj = CreateDB()
obj.createFlightSearch()