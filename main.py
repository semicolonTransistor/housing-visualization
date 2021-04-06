import urllib.request
import os.path
import zipfile
import datetime
import sqlite3
from typing import Union

import geopandas
import pandas as pd
import tqdm


def get_state_id(conn: sqlite3.Connection, state: Union[int, str]) -> int:
    if isinstance(state, int):
        return state
    else:
        cursor = conn.cursor()
        if len(state) == 2:
            cursor.execute("SELECT id FROM states WHERE abbreviation = ?", (state,))
            row = cursor.fetchone()
            if row is None:
                raise RuntimeError(f"Expected 1 Rows, Got {cursor.arraysize} instead.")
            else:
                return row[0]
        else:
            cursor.execute("SELECT id FROM states WHERE name = ?", (state,))
            row = cursor.fetchone()
            if row is None:
                raise RuntimeError(f"Expected 1 Rows, Got {cursor.arraysize} instead.")
            else:
                return row[0]


def get_county_id(conn: sqlite3.Connection, state: Union[str, int], county: Union[str, int]):
    if isinstance(county, int):
        return county

    state_id = get_state_id(conn, state)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM counties WHERE state = ? AND name = ?", (state_id, county,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute("INSERT INTO counties (state, name) VALUES (?, ?)", (state_id, county,))
        conn.commit()
        return get_county_id(conn, state_id, county)
    else:
        return row[0]


def get_city_id(conn: sqlite3.Connection, state: Union[str, int], county: Union[str, int], city: Union[str, int]):
    if isinstance(city, int):
        return city

    state_id = get_state_id(conn, state)
    county_id = get_county_id(conn, state_id, county)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM cities WHERE county = ? AND name = ?", (county_id, city,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute("INSERT INTO cities (county, name) VALUES (?, ?)", (county_id, city,))
        conn.commit()
        return get_city_id(conn, state_id, county_id, city)
    else:
        return row[0]


def get_metro_area_id(conn: sqlite3.Connection, metro_area_name: str) -> Union[int, None]:
    if metro_area_name:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM metro_areas WHERE name = ?", (metro_area_name,))
        row = cursor.fetchone()
        if row is None:
            cursor.execute("INSERT INTO metro_areas (name) VALUES (?)", (metro_area_name,))
            conn.commit()
            return get_metro_area_id(conn, metro_area_name)
        else:
            return row[0]
    else:
        return None


def main():
    update_database()
    # print("Checking directories...")
    # ensure_directory("../housing_visualization_test/data/housing")
    # ensure_directory("../housing_visualization_test/data/download")
    # ensure_directory("../housing_visualization_test/data/geography")
    # # print("Downloading housing data...")
    # # urllib.request.urlretrieve(
    # #     "https://files.zillowstatic.com/research/public_v2/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_mon.csv",
    # #     "data/housing/house_value.csv"
    # # )
    # # print("Downloading geography data...")
    # # urllib.request.urlretrieve(
    # #     "https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_zcta510_500k.zip",
    # #     "data/download/zipcode.zip"
    # # )
    # # print("Extracting geography data...")
    # # file = zipfile.ZipFile("data/download/zipcode.zip")
    # # ensure_directory("data/geography/zipcode")
    # # file.extractall("data/geography/zipcode")
    #
    # print("Parsing Housing Data...")
    # connection = sqlite3.connect("../housing_visualization_test/data/housing.sqlite")
    # with open("../housing_visualization_test/data/housing/house_value.csv") as f:
    #     # init date array:
    #     header = f.readline()
    #     date_strings = header.split(",")[9:]
    #     dates = list()
    #     entries_by_zip_code = dict()
    #
    #     date_strings = tuple(map(lambda s: s.strip(" \n\""), date_strings))
    #
    #     for date_string in date_strings:
    #         date = datetime.date.fromisoformat(date_string)
    #         dates.append(date)
    #     lines = f.readlines()
    #     for i in tqdm.trange(len(lines)):
    #         line = lines[i]
    #         entry_strings = line.split(",")
    #         # RegionID,SizeRank,RegionName,RegionType,StateName,State,City,Metro,CountyName
    #         size_rank = int(entry_strings[1].strip(" \n\""))
    #         zipcode = int(entry_strings[2].strip(" \n\""))
    #         metro_area_id = get_metro_area_id(connection, entry_strings[7].strip(" \n\""))
    #         city_id = get_city_id(connection,
    #                               entry_strings[5].strip(" \n\""),
    #                               entry_strings[8].strip(" \n\""),
    #                               entry_strings[6].strip(" \n\""))
    #
    #         connection.execute("INSERT INTO zipcodes (zipcode, city, metro_area, size_rank) VALUES (?, ?, ?, ?)",
    #                            (zipcode, city_id, metro_area_id, size_rank))
    #
    #         data_strings = entry_strings[9:]
    #         data = list()
    #         for j in range(len(data_strings)):
    #             data_string = data_strings[j]
    #             data_string = data_string.strip(" \n\"")
    #             if data_string:
    #                 data.append((zipcode, date_strings[j], float(data_string)))
    #
    #         connection.executemany("INSERT INTO house_values (zipcode, date, value) VALUES (?, ?, ?)", data)
    #         connection.commit()
    # connection.close()


def update_database():
    print("Checking directories...")
    ensure_directory("data/housing")
    ensure_directory("data/download")
    ensure_directory("data/geography")

    # fetch data from the internet
    print("Downloading housing data...")
    urllib.request.urlretrieve(
        "https://files.zillowstatic.com/research/public_v2/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_mon.csv",
        "data/housing/house_value.csv"
    )
    print("Downloading geography data...")
    urllib.request.urlretrieve(
        "https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_zcta510_500k.zip",
        "data/download/zipcode.zip"
    )
    print("Extracting geography data...")

    with zipfile.ZipFile("data/download/zipcode.zip") as z:
        ensure_directory("data/geography/zipcode")
        z.extractall("data/geography/zipcode")

    if os.path.exists("data/housing.sqlite"):
        print("Dropping Database...")
        os.remove("data/housing.sqlite")

    # setting up the database
    print("Creating Database")
    with sqlite3.connect("data/housing.sqlite") as connection:
        print("Constructing Database...")
        with open("database_init.sql") as f:
            connection.executescript(f.read())

        with open("states_table_init.sql") as f:
            connection.executescript(f.read())

        print("Parsing Housing Data...")
        with open("data/housing/house_value.csv") as f:
            # init date array:
            header = f.readline()
            date_strings = header.split(",")[9:]

            date_strings = tuple(map(lambda s: s.strip(" \n\""), date_strings))

            lines = f.readlines()
            for i in tqdm.trange(len(lines)):
                line = lines[i]
                entry_strings = line.split(",")
                # RegionID,SizeRank,RegionName,RegionType,StateName,State,City,Metro,CountyName
                size_rank = int(entry_strings[1].strip(" \n\""))
                zipcode = int(entry_strings[2].strip(" \n\""))
                metro_area_id = get_metro_area_id(connection, entry_strings[7].strip(" \n\""))
                city_id = get_city_id(connection,
                                      entry_strings[5].strip(" \n\""),
                                      entry_strings[8].strip(" \n\""),
                                      entry_strings[6].strip(" \n\""))

                connection.execute("INSERT INTO zipcodes (zipcode, city, metro_area, size_rank) VALUES (?, ?, ?, ?)",
                                   (zipcode, city_id, metro_area_id, size_rank))

                data_strings = entry_strings[9:]
                data = list()
                for j in range(len(data_strings)):
                    data_string = data_strings[j]
                    data_string = data_string.strip(" \n\"")
                    if data_string:
                        data.append((zipcode, date_strings[j], float(data_string)))

                connection.executemany("INSERT INTO house_values (zipcode, date, value) VALUES (?, ?, ?)", data)
                connection.commit()
        print("Parsing Zipcode Geographic Data...")
        zip_gdf = geopandas.read_file("data/geography/zipcode")
        print("Calculating Bounding Boxes")
        d = pd.concat([zip_gdf["GEOID10"], zip_gdf.bounds], axis=1)

        print("Inserting Bounding Box Data into Database...")
        for index, row in tqdm.tqdm(d.iterrows(), total=d.shape[0]):
            if connection.execute("SELECT count(zipcode) FROM zipcodes WHERE zipcode = ?", (row["GEOID10"],)).fetchone()[0]:
                connection.execute(
                    "UPDATE zipcodes SET longitude_min = ?, longitude_max = ?, latitude_min = ?, latitude_max = ? "
                    "WHERE zipcode = ?",
                    (row["minx"], row["maxx"], row["miny"], row["maxy"], int(row["GEOID10"])))
                connection.commit()
    print("Done!")


def ensure_directory(path: str):
    if path:
        head, tail = os.path.split(path)
        ensure_directory(head)
        if tail:
            if not os.path.exists(path):
                os.mkdir(path)


if __name__ == "__main__":
    main()
