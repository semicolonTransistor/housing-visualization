import enum
import math

import matplotlib
import geopandas

from matplotlib import cm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from housing_visualization.database.database_repository import DataRepository
from matplotlib.pyplot import Axes
from PyQt5 import Qt
from PyQt5 import QtCore
import pandas as pd
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from matplotlib.ticker import StrMethodFormatter
import shapely.geometry
import numpy as np
import copy
import numpy as np

import timeit

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 240)


class Map(FigureCanvasQTAgg):

    class DetailLevel(enum.Enum):
        ZIPCODE = 1
        COUNTY = 2
        STATE = 3

    lod_auto_switch_order = (None, DetailLevel.ZIPCODE, DetailLevel.COUNTY, DetailLevel.STATE)
    lod_auto_switch_threshold = (0.00, 0.1, 0.4, 10)

    scale_min = 0.001
    scale_max = 4
    scale_change_per_wheel_deg_ratio = 4.165E-4
    scale_change_per_wheel_deg = 0.833E-6 * 5

    min_update_interval = 0.1

    center_changed = QtCore.pyqtSignal(object)
    clim_changed = QtCore.pyqtSignal(object)

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes: Axes = self.fig.gca()
        super(Map, self).__init__(self.fig)
        self.zipcode_data = geopandas.read_file("data/geography/zipcode")
        self.zipcode_data["id"] = self.zipcode_data["ZCTA5CE10"].apply(lambda x: int(x))
        self.county_data = geopandas.read_file("data/geography/county")
        self.county_data["id"] = self.county_data.apply(lambda x: int(x["STATEFP"] + x["COUNTYFP"]), axis=1)
        self.state_data = geopandas.read_file("data/geography/state")
        print(self.state_data)
        self.state_data["id"] = self.state_data.apply(lambda x: int(x["STATEFP"]), axis=1)

        self.center = [-71.0900052, 42.3367387]
        self.scale = 0.01  # degrees per inch
        self.lod = Map.DetailLevel.ZIPCODE
        self.lod_auto_switch = True

        self.graph_min = 1000
        self.graph_max = 1000000
        self.color_bar_auto_range = True
        self.color_axis = (0, 1500000)
        self.cur_clim = None

        self.repo = DataRepository("data/housing.sqlite")
        self.last_update = timeit.default_timer()
        self.dragging = False
        self.drag_start = (0.0, 0.0)
        self.cur_date = "2021-02-28"
        self.show_zip_codes = False
        self.dates = self.repo.get_dates()

        self.cmap = copy.copy(cm.get_cmap("plasma"))
        self.cmap.set_bad(color="lightgrey")

        self.do_update = False
        self.timer = Qt.QTimer(self)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(100)

        self.update_plot()

    def update_plot(self):
        # print("plot")
        start = timeit.default_timer()

        # calculate lod auto switch
        if self.lod_auto_switch:
            if self.scale < self.lod_auto_switch_threshold[self.lod_auto_switch_order.index(self.lod) - 1]:
                self.lod = self.lod_auto_switch_order[self.lod_auto_switch_order.index(self.lod) - 1]
            elif self.scale > self.lod_auto_switch_threshold[self.lod_auto_switch_order.index(self.lod)]:
                self.lod = self.lod_auto_switch_order[self.lod_auto_switch_order.index(self.lod) + 1]
        print(self.lod)
        print(self.scale)

        width_deg = self.fig.get_figwidth() * self.scale
        height_deg = self.fig.get_figheight() * self.scale
        bbox = ((self.center[0] - width_deg / 2, self.center[0] + width_deg / 2),
                (self.center[1] - height_deg / 2, self.center[1] + height_deg / 2))
        # print(bbox)
        if self.lod == self.DetailLevel.ZIPCODE:
            zipcodes_visible = self.repo.get_zipcodes_within_bbox(bbox[0], bbox[1])
            geo_data_visible = self.zipcode_data[self.zipcode_data.id.isin(zipcodes_visible)].copy()
            geo_data_visible["value"] = geo_data_visible["id"].apply(
                lambda zipcode: self.repo.get_house_value_by_date_and_zipcode(zipcode, self.cur_date))
        elif self.lod == self.DetailLevel.COUNTY:
            counties_visible = self.repo.get_counties_within_bbox(bbox[0], bbox[1])
            geo_data_visible = self.county_data[self.county_data.id.isin(counties_visible)].copy()
            geo_data_visible["value"] = geo_data_visible["id"].apply(
                lambda county: self.repo.get_house_value_by_date_and_county(county, self.cur_date))
        else:
            states_visible = self.repo.get_states_within_bbox(bbox[0], bbox[1])
            geo_data_visible = self.state_data[self.state_data.id.isin(states_visible)].copy()
            geo_data_visible["value"] = geo_data_visible["id"].apply(
                lambda state: self.repo.get_house_value_by_date_and_state(state, self.cur_date))
        if self.color_bar_auto_range:
            self.graph_min = geo_data_visible["value"].quantile(0.25)
            self.graph_max = geo_data_visible["value"].quantile(0.75)

        t1 = timeit.default_timer()
        self.axes.clear()
        self.fig.clear()
        self.axes = self.fig.gca()

        t2 = timeit.default_timer()
        self.axes.clear()
        self.axes.set(xlim=bbox[0], ylim=bbox[1])

        patches = []
        values = []

        for index, row in geo_data_visible.iterrows():
            poly = row["geometry"]
            value = row["value"]

            if value is None:
                value = np.nan

            if isinstance(poly, shapely.geometry.MultiPolygon):
                for sub_poly in poly:
                    a = np.asarray(sub_poly.exterior)
                    patches.append(Polygon(a))
                    values.append(value)
            else:
                a = np.asarray(poly.exterior)
                patches.append(Polygon(a))
                values.append(value)
        patches = PatchCollection(patches, edgecolors="white")
        values = np.asarray(values)

        if values is not None:
            patches.set_array(values)
            if self.color_bar_auto_range:
                patches.set_clim(vmin=self.graph_min, vmax=self.graph_max)
            else:
                patches.set_clim(vmin=self.color_axis[0], vmax=self.color_axis[1])
            self.color_axis = patches.get_clim()
            self.clim_changed.emit(self.color_axis)
            patches.set_cmap(self.cmap)

        self.axes.add_collection(patches, autolim=True)

        if self.show_zip_codes:
            graph_mid = (self.graph_max + self.graph_min) / 2
            if self.lod == self.DetailLevel.ZIPCODE:
                for idx, row in geo_data_visible.iterrows():
                    color = "white" if row["value"] < graph_mid else "black"
                    self.axes.annotate(text=f"{row['id']:0>5}",
                                       xy=row["geometry"].centroid.coords[:][0],
                                       horizontalalignment='center',
                                       color=color,
                                       fontsize=10,
                                       )
            else:
                for idx, row in geo_data_visible.iterrows():
                    color = "white" if row["value"] < graph_mid else "black"
                    self.axes.annotate(text=row["NAME"],
                                       xy=row["geometry"].centroid.coords[:][0],
                                       horizontalalignment='center',
                                       color=color,
                                       fontsize=10,
                                       )

        t3 = timeit.default_timer()

        comma_fmt = StrMethodFormatter("${x:,.0f}")
        self.fig.colorbar(cm.ScalarMappable(norm=patches.norm, cmap=self.cmap), ax=self.axes, format=comma_fmt, pad=0.05)
        # self.fig.tight_layout()
        self.fig.canvas.draw()


        end = timeit.default_timer()
        print(f"{end - start}, {t1 - start}, {end - t1}")
        print(f"clear: {t2-t1}, plot: {t3-t2}, render: {end - t3}")

    def wheelEvent(self, event: Qt.QWheelEvent):
        self.scale = self.scale + (event.angleDelta().y() * -self.scale * self.scale_change_per_wheel_deg_ratio)
        if self.scale < self.scale_min:
            self.scale = self.scale_min
        elif self.scale > self.scale_max:
            self.scale = self.scale_max

        self.do_update = True

        # self.update_plot()

    def mousePressEvent(self, event: Qt.QMouseEvent):
        if event.buttons() & QtCore.Qt.MiddleButton:
            self.dragging = True
            self.drag_start = (event.x(), event.y())

    def mouseMoveEvent(self, event: Qt.QMouseEvent):
        if self.dragging:
            scale_factor = self.scale / self.fig.get_dpi()
            self.center[0] -= (event.x() - self.drag_start[0]) * scale_factor
            self.center[1] += (event.y() - self.drag_start[1]) * scale_factor
            self.drag_start = (event.x(), event.y())

            self.do_update = True
            # self.update_plot()
            self.center_changed.emit(self.center)


    def mouseReleaseEvent(self, event: Qt.QMouseEvent):
        if not event.buttons() & QtCore.Qt.MiddleButton:
            self.dragging = False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.do_update = True

    def on_timer(self):
        if self.do_update:
            self.do_update = False
            self.update_plot()

    def update_date_by_idx(self, idx):
        self.cur_date = self.dates[idx]
        self.do_update = True