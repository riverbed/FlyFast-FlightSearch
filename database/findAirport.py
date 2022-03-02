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
   
def find_airports_containing(text, limit):
    connection = make_airports_db()   
    cursor = connection.cursor()
    query = """SELECT 
        AirportCode AS value,
        AirportName AS name,
        Address AS address,
        City AS city,
        Region AS region,
        Country AS country      
        FROM Airports
        WHERE AirportName LIKE '%{}%'   OR 
            Address LIKE '%{}%' OR
            AirportCode LIKE '%{}%' OR
            City LIKE '%{}%' OR
            Region LIKE '%{}%' OR
            Country LIKE '%{}%' OR
            Region LIKE '%{}%' --case-insensitive
        LIMIT {}
        """.format(text, text, text, text, text, text, text, limit)  
    cursor.execute(query)
    rows = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    rowsAsJson = json.dumps(rows)  
    # print(rowsAsJson)
    return rowsAsJson
    


