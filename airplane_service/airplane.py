import json
from flask import *
from mysql.connector import connect, Error
from queue import PriorityQueue

app = Flask(__name__)

inf = 9999


# Search algorithm
# Based on uniform cost search 
def search(nodes, edges, source, destination, max_flights, departure_hour):
    visited = set()
    visited.add(source)

    queue = PriorityQueue()
    queue.put((0, source))

    parent = {source : (None, None)}

    def reconstruct_path(city):
        flights = []

        while city:
            flight, city = parent[city]
            if flight:
                flights.append(flight)

        flights.reverse()

        return flights

    while not queue.empty():
        node = queue.get()

        cost = node[0]
        current = node[1]
    
        if current == destination:
            return reconstruct_path(current)

        if len(reconstruct_path(current)) == max_flights or current not in edges:
            continue

        for city, info in edges[current].items():
            if city not in visited:
                visited.add(city)

                minim = inf, inf, -1
                for year_hour, duration, flight_id in info:
                    takeoff_hour = year_hour - departure_hour
                    
                    if takeoff_hour > cost and takeoff_hour < minim[0]:
                        minim = takeoff_hour, duration, flight_id

                if minim[0] != inf:
                    parent[city] = minim[2], current
                    queue.put((minim[0] + minim[1], city))

    return None


def route(source, destination, max_flights, departure_day):
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

        # Get all the cities
        cursor.execute('SELECT Source FROM Flights UNION SELECT Destination FROM Flights;')
        nodes = [result[0] for result in cursor.fetchall()]

        # Get all the flights that start after departure day
        # We only consider flight from the source city that start on the departure day
        # It would be absurd to fly around just to return in the same city in order to catch a later flight
        cursor.execute(
            '''
                SELECT FlightID, Source, Destination, (TakeOffDay * 24 + TakeOffHour) HourInYear, Duration
                FROM Flights
                WHERE
                    TakeOffDay * 24 + TakeOffHour + Duration >= (
                        SELECT MIN(TakeOffDay * 24 + TakeOffHour + Duration)
                        FROM Flights
                        WHERE TakeOffDay = %s AND Source = %s
                    )
                    AND
                    (
                        TakeOffDay = %s
                        OR
                        NOT Source = %s
                    );
            ''',
            (departure_day, source, departure_day, source)
        )
        result = cursor.fetchall()

        # Close the connection
        if connection.is_connected():
            cursor.close()
            connection.close()

        # Get the edges as dictionary with key source and dictionary with key destination
        edges = {
            r[1] : {
                ro[2] : [
                    (row[3], row[4], row[0]) for row in result if row[1] == ro[1] and row[2] == ro[2]
                ] for ro in result if ro[1] == r[1]
            } for r in result
        }

        flight_ids = search(nodes, edges, source, destination, int(max_flights), 24 * int(departure_day))

        if flight_ids:
            return flight_ids, None
        else:
            return None, ''
    except Error as e:
        return None, e


def book(flight_ids):
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

        # Get the number of available seats and number of reserved seats for each flight
        for flight_id in flight_ids:
            cursor.execute(
                '''
                    SELECT AvailableSeats, (SELECT COUNT(*) FROM FlightsToReservations WHERE FlightID = %s)
                    FROM Flights
                    WHERE FlightID = %s;
                ''',
                (flight_id, flight_id)
            )
            
            result = cursor.fetchone()

            if result == None:
                return None, -1
            else:
                available_seats, booked_seats = result

                # We can overbook by 10%
                if booked_seats >= 1.1 * available_seats:
                    return None, -2

        # Create a new reservation
        cursor.execute('INSERT INTO Reservations Values ();')

        reservation_id = cursor.lastrowid

        # Create a mapping between reservation and flights
        for flight_id in flight_ids:
            cursor.execute('INSERT INTO FlightsToReservations Values (%s, %s);', (flight_id, reservation_id))

        # Commit the changes to the database
        connection.commit()

        # Close the connection
        if connection.is_connected():
            cursor.close()
            connection.close()
    except Error as e:
        return None, e

    return reservation_id, None


@app.route('/route', methods=['GET'])
def get_optimal_route():
    source        = request.args.get('source')
    destination   = request.args.get('destination')
    max_flights   = request.args.get('max_flights')
    departure_day = request.args.get('departure_day')

    flight_ids, err = route(source, destination, max_flights, departure_day)

    if err == '':
        return Response('Route not found', status=404)
    elif err is not None:
        return Response('MySQL error: ' + err.msg, status=500)
    else:
        return Response(json.dumps(flight_ids), status=200, mimetype='application/json')


@app.route('/book', methods=['POST'])
def book_ticket():
    data = request.json

    flight_ids = data['flight_ids']

    reservation_id, err = book(flight_ids)
        
    if err == -1:
        return Response('One of the flights not found', status=404)
    elif err == -2:
        return Response('One of the flights is fully booked', status=403)
    elif err is not None:
        return Response('MySQL error: ' + err.msg, status=500)
    else:
        flight_ids = ', '.join(str(flight_id) for flight_id in flight_ids)
        return Response(f'Flight(s) {flight_ids} reserved and reservation id is {reservation_id}', status=200)


@app.route('/findandbook', methods=['POST'])
def find_and_book_ticket():
    data = request.json

    source        = data['source']
    destination   = data['destination']
    max_flights   = data['max_flights']
    departure_day = data['departure_day']

    flight_ids, err = route(source, destination, max_flights, departure_day)

    if err == '':
        return Response('Route not found', status=404)
    elif err is not None:
        return Response('MySQL error: ' + err.msg, status=500)
    else:
        reservation_id, err = book(flight_ids)
        
        if err == -1:
            return Response('One of the flights not found', status=404)
        elif err == -2:
            return Response('One of the flights is fully booked', status=403)
        elif err is not None:
            return Response('MySQL error: ' + err.msg, status=500)
        else:
            flight_ids = ', '.join(str(flight_id) for flight_id in flight_ids)
            return Response(f'Flights {flight_ids} reserved and reservation id is {reservation_id}', status=200)
    

@app.route('/buy', methods=['POST'])
def buy_ticket():
    data = request.json

    reservation_id = data['reservation_id']
    credit_card_information = data['credit_card_information']
    boarding_pass = ''

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

        # Check if ticket was already bought
        cursor.execute('SELECT * FROM Tickets WHERE ReservationID = %s;', (reservation_id,))
        result = cursor.fetchone()
        if result is not None:
            return Response('Ticket already bought', status=403)

        # Get the number of available seats and the number of bought seats
        cursor.execute(
            '''
                SELECT FlightID ID, Source, Destination, TakeOffHour, TakeOffHour, Duration, AvailableSeats, (
                    SELECT COUNT(*)
                    FROM FlightsToReservations NATURAL JOIN Tickets
                    WHERE FlightID = ID
                ) BoughtTickets
                FROM FlightsToReservations NATURAL JOIN Flights
                WHERE FlightID IN (
                    SELECT FlightID
                    FROM FlightsToReservations
                    WHERE ReservationID = %s
                )
                GROUP BY ID;
            ''',
            (reservation_id,)
        )

        result = cursor.fetchall()

        if result == []:
            return Response('Reservation does not exist or flights on it had been canceled', status=404)

        # Check if one of the flights if sold out
        for _, source, destination, take_off_hour, take_off_day, duration, available_seats, bought_seats in result:
            if bought_seats == available_seats:
                return Response('No more available seats on one of the flights', status=403)
            else:
                boarding_pass += f'{source} to {destination} leaves on {take_off_day} at {take_off_hour} and takes {duration} hour(s)' + '\n'

        # Create a new ticket
        cursor.execute('INSERT INTO Tickets Values (%s, %s);', (reservation_id, credit_card_information))

        # Commit the changes to the database
        connection.commit()

        # Close the connection
        if connection.is_connected():
            cursor.close()
            connection.close()
    except Error as e:
        return Response('MySQL error: ' + e.msg, status=500)

    return Response(f'Ticket bought\n\nBoarding Pass Information:\n{boarding_pass}', status=200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='9000')
