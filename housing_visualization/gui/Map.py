import matplotlib
import geopandas

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from housing_visualization.database.database_repository import DataRepository
from matplotlib.pyplot import Axes
from PyQt5 import Qt
from PyQt5 import QtCore

import timeit


class Map(FigureCanvasQTAgg):
    scale_min = 0.001
    scale_max = 0.1
    scale_change_per_wheel_deg = 0.833E-6 * 5

    min_update_interval = 0.1

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
        self.update_plot()

    def update_plot(self):
        # print("plot")
        start = timeit.default_timer()
        self.axes.remove()
        self.fig.clear()
        self.axes = self.fig.gca()
        width_deg = self.fig.get_figwidth() * self.scale
        height_deg = self.fig.get_figheight() * self.scale
        bbox = ((self.center[0] - width_deg / 2, self.center[0] + width_deg / 2),
                (self.center[1] - height_deg / 2, self.center[1] + height_deg / 2))
        # print(bbox)
        self.axes.clear()
        self.axes.set(xlim=bbox[0], ylim=bbox[1])

        zipcodes_visible = self.repo.get_zipcodes_within_bbox(bbox[0], bbox[1])
        zipcodes_data_visible = self.zipcode_data[self.zipcode_data.ZCTA5CE10.isin(zipcodes_visible)].copy()
        zipcodes_data_visible["value"] = zipcodes_data_visible["ZCTA5CE10"].apply(
            lambda zipcode: self.repo.get_house_value_by_date_and_zipcode(zipcode, "2021-02-28"))
        graph_min = zipcodes_data_visible["value"].quantile(0.1)
        graph_max = zipcodes_data_visible["value"].quantile(0.9)
        zipcodes_data_visible.plot(ax=self.axes, column="value", legend=True, vmin=graph_min, vmax=graph_max,
                                   linewidth=10)
        zipcodes_data_visible.boundary.plot(ax=self.axes, edgecolor="white")
        self.fig.canvas.draw()

        end = timeit.default_timer()
        print(end - start)

    def wheelEvent(self, event: Qt.QWheelEvent):
        self.scale = self.scale + (event.angleDelta().y() * -self.scale_change_per_wheel_deg)
        if self.scale < self.scale_min:
            self.scale = self.scale_min
        elif self.scale > self.scale_max:
            self.scale = self.scale_max

        # print(self.scale)

        self.update_plot()

    def mousePressEvent(self, event:Qt.QMouseEvent):
        if event.buttons() & QtCore.Qt.MiddleButton:
            self.dragging = True
            self.drag_start = (event.x(), event.y())
        print(self.dragging)

    def mouseMoveEvent(self, event:Qt.QMouseEvent):
        if self.dragging:
            scale_factor = self.scale / self.fig.get_dpi()
            self.center[0] -= (event.x() - self.drag_start[0]) * scale_factor
            self.center[1] += (event.y() - self.drag_start[1]) * scale_factor
            self.drag_start = (event.x(), event.y())

            self.update_plot()


    def mouseReleaseEvent(self, event:Qt.QMouseEvent):
        if not event.buttons() & QtCore.Qt.MiddleButton:
            self.dragging = False
        print(self.dragging)
