import urllib.request
import requests
import os.path
import zipfile
import datetime
import sqlite3
from typing import Union
from housing_visualization.database.database_repository import DataRepository

import geopandas
import pandas as pd
import tqdm

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
        "data/housing/house_value_zip.csv"
    )
    urllib.request.urlretrieve(
        "https://files.zillowstatic.com/research/public_v2/zhvi/County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_mon.csv",
        "data/housing/house_value_county.csv"
    )
    urllib.request.urlretrieve(
        "https://files.zillowstatic.com/research/public_v2/zhvi/State_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_mon.csv",
        "data/housing/house_value_states.csv"
    )
    print("Downloading geography data...")
    urllib.request.urlretrieve(
        "https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_zcta510_500k.zip",
        "data/download/zipcode.zip"
    )

    urllib.request.urlretrieve(
        "https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_county_20m.zip",
        "data/download/county.zip"
    )

    urllib.request.urlretrieve(
        "https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_state_20m.zip",
        "data/download/state.zip"
    )

    print("Extracting geography data...")

    with zipfile.ZipFile("data/download/zipcode.zip") as z:
        ensure_directory("data/geography/zipcode")
        z.extractall("data/geography/zipcode")

    with zipfile.ZipFile("data/download/county.zip") as z:
        ensure_directory("data/geography/county")
        z.extractall("data/geography/county")

    with zipfile.ZipFile("data/download/state.zip") as z:
        ensure_directory("data/geography/state")
        z.extractall("data/geography/state")

    # if os.path.exists("data/housing.sqlite"):
    #     print("Dropping Database...")
    #     os.remove("data/housing.sqlite")
    #
    # # setting up the database
    # print("Creating Database")
    repo = DataRepository("data/housing.sqlite")
    # print("Constructing Database...")
    # with open("database_init.sql") as f:
    #     repo.conn.executescript(f.read())
    #
    # with open("states_table_init.sql") as f:
    #     repo.conn.executescript(f.read())

    # print("Parsing Housing Data...")
    #
    # with open("data/housing/house_value_states.csv") as f:
    #     # init date array:
    #     header = f.readline()
    #     date_strings = header.split(",")[9:]
    #
    #     date_strings = tuple(map(lambda s: s.strip(" \n\""), date_strings))
    #
    #     lines = f.readlines()
    #     for i in tqdm.trange(len(lines)):
    #         line = lines[i]
    #         entry_strings = line.split(",")
    #
    #         # size_rank = int(entry_strings[1].strip(" \n\""))
    #         state_name = entry_strings[4].strip(" \n\"")
    #         state_id = repo.get_state_id(state_name)
    #
    #         data_strings = entry_strings[9:]
    #         data = list()
    #         for j in range(len(data_strings)):
    #             data_string = data_strings[j]
    #             data_string = data_string.strip(" \n\"")
    #             if data_string:
    #                 data.append((state_id, date_strings[j], float(data_string)))
    #
    #         repo.conn.executemany("INSERT INTO house_values_by_state (state, date, value) VALUES (?, ?, ?)", data)
    #         repo.conn.commit()
    #
    # with open("data/housing/house_value_county.csv") as f:
    #     # init date array:
    #     header = f.readline()
    #     date_strings = header.split(",")[9:]
    #
    #     date_strings = tuple(map(lambda s: s.strip(" \n\""), date_strings))
    #
    #     lines = f.readlines()
    #     for i in tqdm.trange(len(lines)):
    #         line = lines[i]
    #         entry_strings = line.split(",")
    #         # RegionID,SizeRank,RegionName,RegionType,StateName,State,City,Metro,CountyName
    #         size_rank = int(entry_strings[1].strip(" \n\""))
    #         state_id = int(entry_strings[7].strip(" \n\""))
    #         county_id = state_id * 1000 + int(entry_strings[8].strip(" \n\""))
    #         name = entry_strings[2].strip(" \n\"")
    #         metro_area_id = repo.get_metro_area_id(entry_strings[6].strip(" \n\""))
    #         repo.conn.execute("INSERT INTO counties (id, state, name, metro_area, size_rank) VALUES (?, ?, ?, ?, ?)",
    #                           (county_id, state_id, name, metro_area_id, size_rank))
    #
    #         data_strings = entry_strings[9:]
    #         data = list()
    #         for j in range(len(data_strings)):
    #             data_string = data_strings[j]
    #             data_string = data_string.strip(" \n\"")
    #             if data_string:
    #                 data.append((county_id, date_strings[j], float(data_string)))
    #
    #         repo.conn.executemany("INSERT INTO house_values_by_county (county, date, value) VALUES (?, ?, ?)", data)
    #         repo.conn.commit()
    #
    # with open("data/housing/house_value_zip.csv") as f:
    #     # init date array:
    #     header = f.readline()
    #     date_strings = header.split(",")[9:]
    #
    #     date_strings = tuple(map(lambda s: s.strip(" \n\""), date_strings))
    #
    #     lines = f.readlines()
    #     for i in tqdm.trange(len(lines)):
    #         line = lines[i]
    #         entry_strings = line.split(",")
    #         # RegionID,SizeRank,RegionName,RegionType,StateName,State,City,Metro,CountyName
    #         size_rank = int(entry_strings[1].strip(" \n\""))
    #         zipcode = int(entry_strings[2].strip(" \n\""))
    #         metro_area_id = repo.get_metro_area_id(entry_strings[7].strip(" \n\""))
    #         city_id = repo.get_city_id(entry_strings[5].strip(" \n\""),
    #                                    entry_strings[8].strip(" \n\""),
    #                                    entry_strings[6].strip(" \n\""))
    #         repo.conn.execute("INSERT INTO zipcodes (zipcode, city, metro_area, size_rank) VALUES (?, ?, ?, ?)",
    #                           (zipcode, city_id, metro_area_id, size_rank))
    #
    #         data_strings = entry_strings[9:]
    #         data = list()
    #         for j in range(len(data_strings)):
    #             data_string = data_strings[j]
    #             data_string = data_string.strip(" \n\"")
    #             if data_string:
    #                 data.append((zipcode, date_strings[j], float(data_string)))
    #
    #         repo.conn.executemany("INSERT INTO house_values (zipcode, date, value) VALUES (?, ?, ?)", data)
    #         repo.conn.commit()

    print("Parsing Zipcode Geographic Data...")
    zip_gdf = geopandas.read_file("data/geography/zipcode")
    print("Calculating Bounding Boxes")
    d = pd.concat([zip_gdf["GEOID10"], zip_gdf.bounds], axis=1)

    print("Inserting Bounding Box Data into Database...")
    for index, row in tqdm.tqdm(d.iterrows(), total=d.shape[0]):
        if repo.conn.execute("SELECT count(zipcode) FROM zipcodes WHERE zipcode = ?", (row["GEOID10"],)).fetchone()[0]:
            repo.conn.execute(
                "UPDATE zipcodes SET longitude_min = ?, longitude_max = ?, latitude_min = ?, latitude_max = ? "
                "WHERE zipcode = ?",
                (row["minx"], row["maxx"], row["miny"], row["maxy"], int(row["GEOID10"])))
            repo.conn.commit()
        else:
            repo.conn.execute(
                "INSERT INTO zipcodes (zipcode, longitude_min, longitude_max, latitude_min, latitude_max)"
                "VALUES (?, ?, ?, ?, ?)",
                (int(row["GEOID10"]), row["minx"], row["maxx"], row["miny"], row["maxy"]))
            repo.conn.commit()

    print("Parsing County Geographic Data...")
    county = geopandas.read_file("data/geography/county")
    print("Calculating Bounding Boxes")
    d = pd.concat([county["STATEFP"], county["COUNTYFP"], county.bounds], axis=1)

    print("Inserting Bounding Box Data into Database...")
    for index, row in tqdm.tqdm(d.iterrows(), total=d.shape[0]):
        if repo.conn.execute("SELECT count(id) FROM counties WHERE id = ?",
                             (int(row["STATEFP"] +row["COUNTYFP"]),)).fetchone()[0]:
            repo.conn.execute(
                "UPDATE counties SET longitude_min = ?, longitude_max = ?, latitude_min = ?, latitude_max = ? "
                "WHERE id = ?",
                (row["minx"], row["maxx"], row["miny"], row["maxy"], int(row["STATEFP"] + row["COUNTYFP"])))
            repo.conn.commit()

    print("Parsing State Geographic Data...")
    county = geopandas.read_file("data/geography/state")
    print("Calculating Bounding Boxes")
    d = pd.concat([county["STATEFP"], county.bounds], axis=1)

    print("Inserting Bounding Box Data into Database...")
    for index, row in tqdm.tqdm(d.iterrows(), total=d.shape[0]):
        if repo.conn.execute("SELECT count(id) FROM states WHERE id = ?",
                             (int(row["STATEFP"]),)).fetchone()[0]:
            repo.conn.execute(
                "UPDATE states SET longitude_min = ?, longitude_max = ?, latitude_min = ?, latitude_max = ? "
                "WHERE id = ?",
                (row["minx"], row["maxx"], row["miny"], row["maxy"], int(row["STATEFP"])))
            repo.conn.commit()
    repo.close()
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
