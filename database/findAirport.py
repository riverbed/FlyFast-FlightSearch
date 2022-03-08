from collections import namedtuple
from itertools import count, product
import json
from multiprocessing.connection import Connection
import sqlite3
from datetime import datetime

from zipkin import tornado 
from opentelemetry import trace
from  opentelemetry.sdk.trace import Resource

app_name = "FlyFast-FlightSearch"

def make_airports_db():
    connection = sqlite3.connect(":memory:") 
    cursor = connection.cursor()
    sql_file = open("database//airport.sql")
    sql_as_string = sql_file.read()
    cursor.executescript(sql_as_string)
    return connection
   
def find_airports_containing(text, limit):
    connection = make_airports_db() 
    
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
        """.format(text, text, text, text, text, text, text)  
     
    otlp_span = tornado.tracer.start_span("find_airports_containing",
                            kind=trace.SpanKind.SERVER,
                            # attributes={
                            #     "sql.query": query,                                
                            #     "service.name": app_name
                            # },
                            )
        
    otlp_span.set_attribute("service.name", app_name)
    otlp_span.set_attribute("sql.query", query)    
    otlp_span.set_attribute("host.name", tornado.get_hostname())
    otlp_span.set_attribute("service.instance.id", "123")

    cursor = connection.cursor()
    cursor.execute(query)
    rows = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    rowsAsJson = json.dumps(rows)  

    otlp_span.set_attribute("sql.rows", len(rows))
        
    otlp_span.end()
    # print(rowsAsJson)
    return rowsAsJson
    


