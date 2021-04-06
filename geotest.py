import geopandas
import timeit
import time
import tqdm
import pandas as pd
import sqlite3

zip_gdf = geopandas.read_file("data/geography/zipcode")
start = time.perf_counter()
for i in tqdm.trange(100):
    zoned_zip_gdf = zip_gdf.loc[zip_gdf["GEOID10"].isin(("02120", "02119", "02115"))]
end = time.perf_counter()
print(f"{(end - start) / 100} sec/iter")
print(zoned_zip_gdf)
# # t = zip_gdf.bounds
# print(t)
# print(t.index)
# print(zip_gdf.index)
# print(zip_gdf.keys())

# for index, row in zip_gdf.iterrows():
#     if int(row["GEOID10"]) == 501:
#         print(row)

# d = pd.concat([zip_gdf["GEOID10"], t], axis=1)
# print(d)
# print(type(d["GEOID10"]))
#
# conn: sqlite3.Connection = sqlite3.connect("data/housing.sqlite")
#
# for index, row in d.iterrows():
#     if conn.execute("SELECT count(zipcode) FROM zipcodes WHERE zipcode = ?", (row["GEOID10"],)).fetchone()[0]:
#         conn.execute("UPDATE zipcodes SET longitude_min = ?, longitude_max = ?, latitude_min = ?, latitude_max = ? "
#                      "WHERE zipcode = ?",
#                      (row["minx"], row["maxx"], row["miny"], row["maxy"], int(row["GEOID10"])))
#         conn.commit()
#
# conn.close()
