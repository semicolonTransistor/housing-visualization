BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "house_values" (
	"zipcode"	INTEGER,
	"date"	TEXT,
	"value"	REAL NOT NULL,
	FOREIGN KEY("zipcode") REFERENCES "zipcodes"("zipcode"),
	PRIMARY KEY("zipcode","date")
);
CREATE TABLE IF NOT EXISTS "states" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL UNIQUE,
	"abbreviation"	TEXT UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "metro_areas" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "counties" (
	"id"	INTEGER,
	"state"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL,
	FOREIGN KEY("state") REFERENCES "states"("id"),
	PRIMARY KEY("id" AUTOINCREMENT),
	UNIQUE("state","name")
);
CREATE TABLE IF NOT EXISTS "cities" (
	"id"	INTEGER,
	"county"	INTEGER NOT NULL,
	"name"	INTEGER NOT NULL,
	FOREIGN KEY("county") REFERENCES "counties"("id"),
	PRIMARY KEY("id" AUTOINCREMENT),
	UNIQUE("county","name")
);
CREATE TABLE IF NOT EXISTS "zipcodes" (
	"zipcode"	INTEGER,
	"city"	INTEGER,
	"metro_area"	INTEGER,
	"size_rank"	INTEGER,
	"longitude_min"	REAL,
	"longitude_max"	REAL,
	"latitude_min"	REAL,
	"latitude_max"	REAL,
	FOREIGN KEY("metro_area") REFERENCES "metro_areas"("id"),
	FOREIGN KEY("city") REFERENCES "cities"("id"),
	PRIMARY KEY("zipcode")
);
CREATE VIEW cities_human_readable as
SELECT states.name as state, counties.name as county, cities.name as city
FROM states, counties, cities
WHERE counties.state = states.id AND cities.county = counties.id;
COMMIT;
