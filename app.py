import os
import psycopg2
from datetime import datetime, timezone
from flask import Flask, app, request
from dotenv import load_dotenv

load_dotenv()


CREATE_ROOM_TABLE = (
    "CREATE TABLE IF NOT EXISTS rooms (id SERIAL PRIMARY KEY, name TEXT);"
)

CREATE_TEMP_TABLE = """CREATE TABLE IF NOT EXISTS temperatures 
                    (room_id INTEGER, temperature REAL, date TIMESTAMP, FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE);"""
    
INSERT_ROOM_RETURN_ID = "INSERT INTO rooms (name) VALUES (%s) RETURNING id;"

INSERT_TEMP = "INSERT INTO temperatures (room_id, temperature, date) VALUES (%s, %s, %s);"

GLOBAL_NUMBER_OF_DAYS = """SELECT COUNT(DISTINCT DATE(date)) AS days FROM temperatures;"""

GLOBAL_AVG_TEMPERATURE = """SELECT AVG(temperature) as average FROM temperatures;"""

URL = os.getenv("DATABASE_URL")
app = Flask(__name__)
connection = psycopg2.connect(URL)

@app.post('/api/rooms')
def create_room():
    data = request.get_json()
    name = data.get('name')
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_ROOM_TABLE)
            cursor.execute(INSERT_ROOM_RETURN_ID, (name,))
            connection.commit()
            room_id = cursor.fetchone()[0]
    return {"room_id": room_id, "message": f"{name} created"}, 201

@app.post('/api/temperatures')
def create_temp():
    data = request.get_json()
    room_id = data.get('room_id')
    temperature = data.get('temperature')
    try:
        date = datetime.strptime(data["date"], '%Y-%m-%d %H:%M:%S')
    except KeyError:
        date = datetime.now(timezone.utc)

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_TEMP_TABLE)
            cursor.execute(INSERT_TEMP, (room_id, temperature, date))
            connection.commit()
    return {"message": "Temperature added"}, 201


@app.get('/api/average')
def get_average():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GLOBAL_AVG_TEMPERATURE)
            days = cursor.fetchone()[0]
            cursor.execute(GLOBAL_NUMBER_OF_DAYS) 
            average = cursor.fetchone()[0]
    return {"average": round(average, 2), "days": days}, 200