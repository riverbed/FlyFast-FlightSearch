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
    query = """SELECT *
        FROM Airports
        WHERE AirportName LIKE '%{}%'   OR 
            Address LIKE '%{}%' OR
              Region LIKE '%{}%' --case-insensitive
        """.format(text, text, text)  
    cursor.execute(query)
    rows = cursor.fetchall()
    print("count {}".format(len(rows)))
    rowsAsJson= json.dumps(rows)   
    print(rowsAsJson)
    return rowsAsJson
    
# find_airports_containing("ing")

