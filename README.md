# Airplane Ticket Booking
Application for booking and buying airplane tickets.

A flight will contain the following information:
* ID (as a String)
* source and destination (as Strings)
* leaving hour (an Int between 0 and 23)
* leaving day (an Int between 0 and 365) - we consider all the flights to be in the same year
* duration (as an Int)
* number of available tickets

# Services

## Airplane service
This service is used for booking and buying tickets and has the following API:
* finding the shortest route between two cities, that returns a list of flights
* booking a ticket between two cities that returns a reservation id
* buying a ticket using it's reservation id, that returns a boarding pass

## Admin service
This service is meant for administering the flights in the database and has the following API:
* add flight, that adds a new entry in the Flights table
* cancel flight, that removes an entry in the Flights table

## Client service
To run use this service use docker attach to the container in order to get to the interactive shell. You can use the command help to see all available commands with parameters and q to exit the terminal.

## MySQL service
The database has 4 tables:
* Flights - contains details about flights.
* Reservations - contains the IDs of the reservation.
* FlightsToReservations - many-to-many relation between flights and reservations.
* Tickets - contains bought reservations and card number.

# Testing
There is a the test file example.txt that covers all possible cases.
