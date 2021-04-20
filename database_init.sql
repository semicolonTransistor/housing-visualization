BEGIN TRANSACTION;
DROP TABLE IF EXISTS "house_values";
CREATE TABLE IF NOT EXISTS "house_values" (
	"zipcode"	INTEGER,
	"date"	TEXT,
	"value"	REAL NOT NULL,
	PRIMARY KEY("zipcode","date"),
	FOREIGN KEY("zipcode") REFERENCES "zipcodes"("zipcode")
);
DROP TABLE IF EXISTS "states";
CREATE TABLE IF NOT EXISTS "states" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL UNIQUE,
	"abbreviation"	TEXT UNIQUE,
	"longitude_min"	REAL,
	"longitude_max"	REAL,
	"latitude_min"	REAL,
	"latitude_max"	REAL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "metro_areas";
CREATE TABLE IF NOT EXISTS "metro_areas" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "cities";
CREATE TABLE IF NOT EXISTS "cities" (
	"id"	INTEGER,
	"county"	INTEGER NOT NULL,
	"name"	INTEGER NOT NULL,
	UNIQUE("county","name"),
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("county") REFERENCES "counties"("id")
);
DROP TABLE IF EXISTS "zipcodes";
CREATE TABLE IF NOT EXISTS "zipcodes" (
	"zipcode"	INTEGER,
	"city"	INTEGER,
	"metro_area"	INTEGER,
	"size_rank"	INTEGER,
	"longitude_min"	REAL,
	"longitude_max"	REAL,
	"latitude_min"	REAL,
	"latitude_max"	REAL,
	PRIMARY KEY("zipcode"),
	FOREIGN KEY("city") REFERENCES "cities"("id"),
	FOREIGN KEY("metro_area") REFERENCES "metro_areas"("id")
);
DROP TABLE IF EXISTS "counties";
CREATE TABLE IF NOT EXISTS "counties" (
	"id"	INTEGER,
	"state"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL,
	"metro_area"	INTEGER,
	"size_rank"	INTEGER,
	"longitude_min"	REAL,
	"longitude_max"	REAL,
	"latitude_min"	REAL,
	"latitude_max"	REAL,
	UNIQUE("state","name"),
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("state") REFERENCES "states"("id")
);
DROP TABLE IF EXISTS "house_values_by_state";
CREATE TABLE IF NOT EXISTS "house_values_by_state" (
	"state"	INTEGER,
	"date"	TEXT,
	"value"	REAL NOT NULL,
	PRIMARY KEY("state","date"),
	FOREIGN KEY("state") REFERENCES "states"("id")
);
DROP TABLE IF EXISTS "house_values_by_county";
CREATE TABLE IF NOT EXISTS "house_values_by_county" (
	"county"	INTEGER,
	"date"	TEXT,
	"value"	REAL NOT NULL,
	PRIMARY KEY("county","date"),
	FOREIGN KEY("county") REFERENCES "counties"("id")
);
DROP VIEW IF EXISTS "cities_human_readable";
CREATE VIEW cities_human_readable as
SELECT states.name as state, counties.name as county, cities.name as city
FROM states, counties, cities
WHERE counties.state = states.id AND cities.county = counties.id;
COMMIT;
