import requests
import json
import shlex

if __name__ == '__main__':
    while True:
        # Read a line and split it into words
        line = shlex.split(input('\n'))

        if len(line) == 0:
            continue

        operation = line[0]

        # If first word is q then quit
        if operation == 'quit':
            break

        # We can have comments
        if operation[0] == '#':
            print(' '.join(line))
            continue

        # Identify the service and make a request to the proper operation
        # Throw an exception if then number of parameters is incorrect or parameters that are supposed to be integers are strings
        try:
            # Help tells you all the parameters for all the commands
            if operation == 'help':
                print('add flight_id source destination departure_hour departure_day duration available_seats')
                print('cancel flight_id')
                print('route source destination max_flights departure_day')
                print('book flight_id1 flight_id2 flight_id3 etc.')
                print('book source destination max_flights departure_day')
                print('buy reservation_id credit_card_inforamation')
                print('quit')           
            elif operation == 'add':
                headers = { 'content-type': 'application/json' }

                data = {
                    'flight_id'       : int(line[1]),
                    'source'          : line[2],
                    'destination'     : line[3],
                    'departure_hour'  : int(line[4]),
                    'departure_day'   : int(line[5]),
                    'duration'        : int(line[6]),
                    'available_seats' : int(line[7])
                }

                r = requests.post('http://admin:6000/' + operation, data=json.dumps(data), headers=headers)

                print(r.text)
            elif operation == 'cancel':
                params = {
                    'flight_id': int(line[1])
                }

                r = requests.delete('http://admin:6000/' + operation, params=params)

                print(r.text)
            elif operation == 'route':
                params = {
                    'source'        : line[1],
                    'destination'   : line[2],
                    'max_flights'   : int(line[3]),
                    'departure_day' : int(line[4])
                }

                r = requests.get('http://airplane:9000/' + operation, params=params)

                print(r.text)
            elif operation == 'book':
                headers = { 'content-type': 'application/json' }

                if False in [s.isdigit() for s in line[1:]]:
                    data = {
                        'source'        : line[1],
                        'destination'   : line[2],
                        'max_flights'   : int(line[3]),
                        'departure_day' : int(line[4])
                    }

                    r = requests.post('http://airplane:9000/findand' + operation, data=json.dumps(data), headers=headers)
                else:
                    data = { 'flight_ids' : [int(flight) for flight in line[1:]] }

                    r = requests.post('http://airplane:9000/' + operation, data=json.dumps(data), headers=headers)

                print(r.text)
            elif operation == 'buy':
                headers = { 'content-type': 'application/json' }

                data = {
                    'reservation_id'          : int(line[1]),
                    'credit_card_information' : line[2]
                }

                r = requests.post('http://airplane:9000/' + operation, data=json.dumps(data), headers=headers)

                print(r.text)
            else:
                print('Unknown operation')
        except Exception as e:
            print(e)
