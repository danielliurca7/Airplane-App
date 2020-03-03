CREATE TABLE IF NOT EXISTS Flights (
    FlightID INT NOT NULL,
    Source VARCHAR(30) NOT NULL,
    Destination VARCHAR(30) NOT NULL,
    TakeOffHour INT CHECK (TakeOffHour BETWEEN 0 AND 23) NOT NULL,
    TakeOffDay INT CHECK (TakeOffDay BETWEEN 1 AND 365) NOT NULL,
    Duration INT CHECK (Duration > 0) NOT NULL,
    AvailableSeats INT CHECK (AvailableSeats > 0) NOT NULL,
    PRIMARY KEY (FlightID)
);

CREATE TABLE IF NOT EXISTS Reservations (
    ReservationID INT NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (ReservationID)
);

CREATE TABLE IF NOT EXISTS Tickets (
    ReservationID INT NOT NULL,
    CreditCardInformation CHAR(16) CHECK (LENGTH(CreditCardInformation) = 16) NOT NULL,
    PRIMARY KEY (ReservationID),
    FOREIGN KEY (ReservationID) REFERENCES Reservations (ReservationID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS FlightsToReservations (
    FlightID INT NOT NULL,
    ReservationID INT NOT NULL,
    PRIMARY KEY (FlightID, ReservationID),
    FOREIGN KEY (FlightID) REFERENCES Flights (FlightID) ON DELETE CASCADE,
    FOREIGN KEY (ReservationID) REFERENCES Reservations (ReservationID) ON DELETE CASCADE
);