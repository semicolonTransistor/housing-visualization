import sqlite3

def main():
    connection = sqlite3.connect("../housing_visualization_test/data/housing.sqlite")
    cursor = connection.cursor()

    with open("states.txt") as f:
        data = map(lambda line: tuple(map(lambda s: s.strip(), line.split("-"))), f)
        cursor.executemany("INSERT INTO states (name, abbreviation) VALUES (?, ?)", data)

    connection.commit()
    connection.close()

main()