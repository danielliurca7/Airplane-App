from flask import *
from mysql.connector import connect, Error

app = Flask(__name__)

@app.route('/add', methods=['POST'])
def add_flight():
    sql = 'INSERT INTO Flights Values (%s, %s, %s, %s, %s, %s, %s);'
    data = request.json

    val = (
        data['flight_id'],
        data['source'],
        data['destination'],
        data['departure_hour'],
        data['departure_day'],
        data['duration'],
        data['available_seats']
    )

    try:
        # Connect to database
        connection = connect(
            host='mysql',
            port=3306,
            database='flights',
            user='root',
            password='root'
        )

        cursor = connection.cursor()

        # Insert the new value into Flights and commit changes
        cursor.execute(sql, val)
        connection.commit()

        # Close the connection
        if connection.is_connected():
            cursor.close()
            connection.close()
    except Error as e:
        return Response('MySQL error: ' + e.msg, status=500)

    return Response(f'Flight {data["flight_id"]} added', status=200)


@app.route('/cancel', methods=['DELETE'])
def cancel_flight():
    flight_id = request.args.get('flight_id')

    try:
        # Connect to database
        connection = connect(
            host='mysql',
            port=3306,
            database='flights',
            user='root',
            password='root'
        )

        cursor = connection.cursor()

        # Check if flight is not in the database
        cursor.execute('SELECT * FROM Flights WHERE FlightID = %s;', (flight_id,))
        result = cursor.fetchone()
        if result is None:
            return Response(f'Flight {flight_id} does not exist', status=404)

        # Delete from the Flights table and commit changes
        cursor.execute('DELETE FROM Flights WHERE FlightID = %s;', (flight_id,))
        connection.commit()

        # Close the connection
        if connection.is_connected():
            cursor.close()
            connection.close()
    except Error as e:
        return Response('MySQL error: ' + e.msg, status=500)

    return Response(f'Flight {flight_id} deleted', status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='6000')
