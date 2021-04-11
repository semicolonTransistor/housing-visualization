import sqlite3
from typing import Union, Tuple

class DataRepository:
    def __init__(self, data_base: str):
        self.conn = sqlite3.connect(data_base)

    def get_state_id(self, state: Union[int, str]) -> int:
        if isinstance(state, int):
            return state
        else:
            cursor = self.conn.cursor()
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


    def get_county_id(self, state: Union[str, int], county: Union[str, int]):
        if isinstance(county, int):
            return county

        state_id = self.get_state_id(state)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM counties WHERE state = ? AND name = ?", (state_id, county,))
        row = cursor.fetchone()
        if row is None:
            cursor.execute("INSERT INTO counties (state, name) VALUES (?, ?)", (state_id, county,))
            self.conn.commit()
            return self.get_county_id(state_id, county)
        else:
            return row[0]

    def get_city_id(self, state: Union[str, int], county: Union[str, int], city: Union[str, int]):
        if isinstance(city, int):
            return city

        state_id = self.get_state_id(state)
        county_id = self.get_county_id(state_id, county)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM cities WHERE county = ? AND name = ?", (county_id, city,))
        row = cursor.fetchone()
        if row is None:
            cursor.execute("INSERT INTO cities (county, name) VALUES (?, ?)", (county_id, city,))
            self.conn.commit()
            return self.get_city_id(state_id, county_id, city)
        else:
            return row[0]

    def get_metro_area_id(self, metro_area_name: str) -> Union[int, None]:
        if metro_area_name:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM metro_areas WHERE name = ?", (metro_area_name,))
            row = cursor.fetchone()
            if row is None:
                cursor.execute("INSERT INTO metro_areas (name) VALUES (?)", (metro_area_name,))
                self.conn.commit()
                return self.get_metro_area_id(metro_area_name)
            else:
                return row[0]
        else:
            return None

    def get_zipcodes_within_bbox(self,
                                 longitude_limits: Tuple[float, float],
                                 latitude_limits: Tuple[float, float]) -> Tuple[int]:
        result = self.conn.execute("SELECT zipcode FROM zipcodes WHERE longitude_max > ? AND longitude_min < ? "
                                   "AND latitude_max > ? AND latitude_min < ?",
                                   longitude_limits + latitude_limits).fetchall()
        return tuple(map(lambda x: int(x[0]), result))

    def get_house_value_by_date_and_zipcode(self,
                                            zipcode: int,
                                            date: str):
        result = self.conn.execute("SELECT value FROM house_values WHERE zipcode = ? AND date = ?",
                                   (zipcode, date)).fetchone()

        if result is not None:
            return result[0]
        else:
            return None

    def close(self):
        self.conn.close()

