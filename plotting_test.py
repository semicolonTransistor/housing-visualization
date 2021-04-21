import geopandas
import pandas as pd
import matplotlib.pyplot as plt
from housing_visualization.database import database_repository

bbox = ((-71.195, -70.948), (42.293, 42.442))

fig: plt.Figure
ax: plt.Axes

fig, ax = plt.subplots(1, 1)


ax.set(xlim=bbox[0], ylim=bbox[1])

states = geopandas.read_file("data/geography/state")
zipcode_data = geopandas.read_file("data/geography/zipcode")
# shore_line_data = geopandas.read_file("data/geography/shoreline")
zipcode_data["ZCTA5CE10"] = zipcode_data["ZCTA5CE10"].apply(lambda x: int(x))
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 240)

repo = database_repository.DataRepository("data/housing.sqlite")
zipcodes_visible = repo.get_zipcodes_within_bbox(bbox[0], bbox[1])
zipcodes_data_visible = zipcode_data[zipcode_data.ZCTA5CE10.isin(zipcodes_visible)].copy()
zipcodes_data_visible["value"] = zipcodes_data_visible["ZCTA5CE10"].apply(
    lambda zipcode: repo.get_house_value_by_date_and_zipcode(zipcode, "2021-02-28"))
print(zipcodes_data_visible)
graph_min = zipcodes_data_visible["value"].quantile(0.1)
graph_max = zipcodes_data_visible["value"].quantile(0.9)
zipcodes_data_visible.plot(ax=ax, column="value", legend=True, vmin=graph_min, vmax=graph_max,
                           linewidth=10)
zipcodes_data_visible.boundary.plot(ax=ax, edgecolor="white")
plt.show()

