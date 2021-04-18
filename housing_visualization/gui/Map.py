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
import shapely.geometry
import numpy as np
import copy
import numpy as np

import timeit

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 240)

class Map(FigureCanvasQTAgg):
    scale_min = 0.001
    scale_max = 1
    scale_change_per_wheel_deg = 0.833E-6 * 5

    min_update_interval = 0.1

    center_changed = QtCore.pyqtSignal(object)

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes: Axes = self.fig.gca()
        super(Map, self).__init__(self.fig)
        self.zipcode_data = geopandas.read_file("data/geography/zipcode")
        self.zipcode_data["ZCTA5CE10"] = self.zipcode_data["ZCTA5CE10"].apply(lambda x: int(x))
        self.center = [-71.0900052, 42.3367387]
        self.scale = 0.01  # degrees per inch
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
        self.timer.start(40)

        self.update_plot()

    def update_plot(self):
        # print("plot")
        start = timeit.default_timer()
        width_deg = self.fig.get_figwidth() * self.scale
        height_deg = self.fig.get_figheight() * self.scale
        bbox = ((self.center[0] - width_deg / 2, self.center[0] + width_deg / 2),
                (self.center[1] - height_deg / 2, self.center[1] + height_deg / 2))
        # print(bbox)
        zipcodes_visible = self.repo.get_zipcodes_within_bbox(bbox[0], bbox[1])
        zipcodes_data_visible = self.zipcode_data[self.zipcode_data.ZCTA5CE10.isin(zipcodes_visible)].copy()
        zipcodes_data_visible["value"] = zipcodes_data_visible["ZCTA5CE10"].apply(
            lambda zipcode: self.repo.get_house_value_by_date_and_zipcode(zipcode, self.cur_date))
        graph_min = zipcodes_data_visible["value"].quantile(0.25)
        graph_max = zipcodes_data_visible["value"].quantile(0.75)
        polygons = zipcodes_data_visible["geometry"]

        t1 = timeit.default_timer()
        self.axes.remove()
        self.fig.clear()
        self.axes = self.fig.gca()

        t2 = timeit.default_timer()
        self.axes.clear()
        self.axes.set(xlim=bbox[0], ylim=bbox[1])

        patches = []
        values = []

        for index, row in zipcodes_data_visible.iterrows():
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
            patches.set_clim(vmin=graph_min, vmax=graph_max)
            patches.set_cmap(self.cmap)

        label = patches.get_label()

        self.axes.add_collection(patches, autolim=True)
        # zipcodes_data_visible.boundary.plot(ax=self.axes, edgecolor="white")

        if self.show_zip_codes:
            for idx, row in zipcodes_data_visible.iterrows():
                self.axes.annotate(text=f"{row['ZCTA5CE10']:0>5}",
                                   xy=row["geometry"].centroid.coords[:][0],
                                   horizontalalignment='center',
                                   color="darkgrey",
                                   fontsize=10,
                                   )

        t3 = timeit.default_timer()

        self.fig.canvas.draw()

        end = timeit.default_timer()
        print(f"{end - start}, {t1 - start}, {end - t1}")
        print(f"clear: {t2-t1}, plot: {t3-t2}, render: {end - t3}")

    def wheelEvent(self, event: Qt.QWheelEvent):
        self.scale = self.scale + (event.angleDelta().y() * -self.scale_change_per_wheel_deg)
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

    def on_timer(self):
        if self.do_update:
            self.do_update = False
            self.update_plot()

    def update_date_by_idx(self, idx):
        self.cur_date = self.dates[idx]