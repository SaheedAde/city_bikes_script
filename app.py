import requests
import logging
from time import sleep

CITYBIKE = 'https://wegfinder.at/api/v1/stations'
ADDRESS = 'https://api.i-mobility.at/routing/api/v1/nearby_address?latitude={}&longitude={}'

def make_request(endpoint):
    resp = requests.get(endpoint)
    if resp.status_code == requests.codes.ok:
        return resp.json()

    logging.error(f'Encountered an error with status code: {resp.status_code}')

def transform_data(stations):
    if not stations: return []

    transformed_stations = [{
        'id': station['id'],
        'name': station['name'],
        'active': station['status'] == "aktiv",
        'description': station['description'],
        'boxes': station['boxes'],
        'free_boxes': station['free_boxes'],
        'free_bikes': station['free_bikes'],
        'free_ratio': float(station['free_boxes'] / station['boxes']),
        'coordinates': [station['longitude'], station['latitude']]
    } for station in stations if station['free_bikes']]

    transformed_stations.sort(key=lambda k: (-k['free_bikes'], k['name'].lower()))

    return transformed_stations

RATE_LIMIT = 10
def add_address(stations):
    if not stations: return stations
    for idx, station in enumerate(stations):
        coord = station['coordinates']
        endpoint = ADDRESS.format(coord[1], coord[0])
        address = make_request(endpoint)
        station['address'] = '' if not address else address['data']['name']

        # handles 429: sleep after every 10 requests
        if idx >= RATE_LIMIT and (idx % RATE_LIMIT == 0):
            sleep(1)
    return stations


data = make_request(CITYBIKE)
stations = transform_data(data)
stations_with_address = add_address(stations)

print(stations_with_address)