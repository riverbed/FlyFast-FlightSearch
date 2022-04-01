from collections import namedtuple
from itertools import count, product
import json
from multiprocessing.connection import Connection
import os
import sqlite3
from datetime import datetime

import tornado_inst

from opentelemetry import trace
from  opentelemetry.sdk.trace import Resource

DATABASE_FILENAME = "flight_search.db"

def ConnectToDB():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.dirname(dir_path)
    database_file = os.path.join(parent_dir, "database", DATABASE_FILENAME )
    return sqlite3.connect(database_file)

def search_airports_containing(text, spanCntext):
    connection = ConnectToDB() 
    
    query = """SELECT 
        AirportCode AS value,
        AirportName AS name,       
        City AS city,
        Region AS region,
        Country AS country      
        FROM Airport
        WHERE AirportName LIKE '%{}%'   OR             
            AirportCode LIKE '%{}%' OR
            City LIKE '%{}%' OR           
            Country LIKE '%{}%' OR
            Region LIKE '%{}%' --case-insensitive
        """.format(text, text, text, text, text, text)  
    
    otlp_span = tornado_inst.tracer.start_span("find_airports_containing", context=spanCntext,
                            kind=trace.SpanKind.SERVER, )
    tornado_inst.set_otlp_span_attributes(otlp_span)
    otlp_span.set_attribute("sql.query", query)
    cursor = connection.cursor()
    cursor.execute(query)
    rows = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    rowsAsJson = json.dumps(rows)  
    
    otlp_span.set_attribute("sql.rows", len(rows))
    connection.close()
    otlp_span.end()

    # print(rowsAsJson)
    return rowsAsJson
