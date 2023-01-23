
DROP TABLE IF EXISTS [Airport];
CREATE TABLE [Airport]
(      [AirportCode] TEXT,
       [AirportName] TEXT,
       [City] TEXT,
       [Country] TEXT,       
       [WorldAreaCode] INTEGER,
       [Zone] INTEGER,
       PRIMARY KEY (`AirportCode`)
);

DROP TABLE IF EXISTS [Flight];
CREATE TABLE [Flight]
(   [Id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [Src] TEXT,
    [Dst] TEXT,
    [Departure] TIME,
    [Arrival] TIME,
    [Airline] TEXT,
    [FlightNum] INTEGER,
    [Fare] FLOAT    
);