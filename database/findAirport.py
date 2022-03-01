from collections import namedtuple
from itertools import count, product
import json
from multiprocessing.connection import Connection
import sqlite3
from datetime import datetime 

def make_airports_db():
    connection = sqlite3.connect(":memory:") 
    cursor = connection.cursor()
    sql_file = open("database//airport.sql")
    sql_as_string = sql_file.read()
    cursor.executescript(sql_as_string)
    return connection
   
def find_airports_containing(text):
    connection = make_airports_db()   
    cursor = connection.cursor()
    query = """SELECT 
        AirportCode,
        AirportName,
        Address,
        City,
        Region,
        Country      
        FROM Airports
        WHERE AirportName LIKE '%{}%'   OR 
            Address LIKE '%{}%' OR
            AirportCode LIKE '%{}%' OR
            City LIKE '%{}%' OR
            Region LIKE '%{}%' OR
            Country LIKE '%{}%' OR
            Region LIKE '%{}%' --case-insensitive
        """.format(text, text, text, text, text, text, text)  
    cursor.execute(query)
    
    airport = {}
    airports = []
    for row in cursor.fetchall():
        airport["value"] = row[0]
        airport["name"] = row[1]
        airport["address"] = row[2]
        airport["city"] = row[3]
        airport["region"] = row[4]
        airport["country"] = row[5]
        airports.append(airport)

    rowsAsJson = json.dumps(airports)
    # print(rowsAsJson)
    return rowsAsJson
    


