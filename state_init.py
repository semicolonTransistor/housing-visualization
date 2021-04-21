import sqlite3

def main():
    connection = sqlite3.connect("data/housing.sqlite")
    cursor = connection.cursor()

    with open("states.txt") as f:
        data = map(lambda x: (x[0], x[1], int(x[2])),
                   map(lambda line: tuple(map(lambda s: s.strip(), line.split("\t"))), f))

        cursor.executemany("INSERT INTO state (name, abbreviation, id) VALUES (?, ?, ?)", data)

    connection.commit()
    connection.close()

main()