import sqlite3
import json


def convert_to_binary(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blob_data = file.read()
    return blob_data


def insert_blob(rid, image):
    sql = None
    try:
        sql = sqlite3.connect('kkonni.db')
        print("Connected to SQLite")

        with sql:
            cur = sql.cursor()

            blob = sqlite3.Binary(convert_to_binary(image))
            sqlite_insert_blob_query = f"UPDATE cookbook SET image = ? WHERE rid = ?"

            # Convert data into tuple format
            cur.execute(sqlite_insert_blob_query, (blob, rid))
        print("Image and file inserted successfully as a BLOB into a table")

    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table >", error)
    finally:
        if sql:
            sql.close()
            print("The sqlite connection is closed")


def insert_json(rid):
    d = [
        {'amount': 3, 'unit': 'Stück', 'name': 'Banane'},
        {'amount': 200, 'unit': 'g', 'name': 'Vollkornmehl'},
        {'amount': 1, 'unit': 'Teelöffel', 'name': 'Zimt'},
        {'amount': 100, 'unit': 'g', 'name': 'Apfel'},
        {'amount': 50, 'unit': 'Packung', 'name': 'Backpulver'},
        {'amount': 1, 'unit': 'Stück', 'name': 'Eier'},
        {'amount': 2, 'unit': 'g', 'name': 'Walnüsse oder Haselnüsse'},
    ]
    s = json.dumps(d)

    sql = None
    try:
        sql = sqlite3.connect('kkonni.db')
        print("Connected to SQLite")

        with sql:
            cur = sql.cursor()
            sqlite_insert_blob_query = f"UPDATE cookbook SET ingredients = ? WHERE rid = ?"

            # Convert data into tuple format
            cur.execute(sqlite_insert_blob_query, (s, rid))
        print("Image and file inserted successfully as a BLOB into a table")

    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table >", error)
    finally:
        if sql:
            sql.close()
            print("The sqlite connection is closed")
