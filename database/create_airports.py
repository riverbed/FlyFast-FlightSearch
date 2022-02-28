import sqlite3



connection = sqlite3.connect(":memory:")
cursor = connection.cursor()
sql_file = open("airport.sql")
sql_as_string = sql_file.read()
cursor.executescript(sql_as_string)

for row in cursor.execute("SELECT * FROM Customers"):
   print(row)



# for row in cursor.execute("SELECT COUNT(*) FROM Orders"):
#     print(row)