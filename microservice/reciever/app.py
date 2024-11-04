import connexion
from connexion import NoContent
import json
import datetime
from datetime import datetime
import os
import requests
import yaml
import logging.config, logging
import uuid
from pykafka import KafkaClient

""" MAX_EVENTS = 5
EVENT_FILE = "events.json" """
DATA_STORAGE_URL="http://localhost:8090/readings"

""" def update_event(event_type, msg_data):
    if not os.path.exists(EVENT_FILE):
        events_data = {
            "num_aircraft_location":0,
            "recent_aircraft_location":[],
            "num_arrival_time":0,
            "recent_arrival_time":[]
        }
    else:
        with open(EVENT_FILE, "r") as file:
            events_data = json.load(file)

    new_event = {
        "message": msg_data,
        "received_timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    }

    if event_type == "aircraft_location":
        events_data["num_aircraft_location"] += 1
        events_data["recent_aircraft_location"].insert(0, new_event)
        if len(events_data["recent_aircraft_location"]) > MAX_EVENTS:
            events_data["recent_aircraft_location"].pop()

    if event_type == "arrival_time":
        events_data["num_arrival_time"] += 1
        events_data["recent_arrival_time"].insert(0, new_event)
        if len(events_data["recent_arrival_time"]) > MAX_EVENTS:
            events_data["recent_arrival_time"].pop()

    with open(EVENT_FILE, 'w') as f:
        json.dump(events_data, f, indent=4)
 """

def generate_trace_id():
    return str(uuid.uuid4())

def report_aircraft_location(body):
    #print("Received aircraft location")
    #print(body) 
    #msg_data = "Aircraft location for " + body["flight_id"] + " has latitude: " + str(body["latitude"]) + " and longitude: " + str(body["longitude"])
    #response = requests.post(DATA_STORAGE_URL + "/location", json=body, headers={"Content-Type": "application/json"})
    
    event_name = "location"
    trace_id = generate_trace_id()
    body["trace_id"] = trace_id

    #logger.info(f'Received event {event_name} request with a trace id of {trace_id}')
    ###response = requests.post(app_config['eventstore1']['url'], json=body, headers={"Content-Type": "application/json"})
    #logger.info(f"Returned event {event_name} response (Id: {trace_id}) with status {response.status_code}")
    #update_event("aircraft_location", msg_data) 
    reading = body
    client = KafkaClient(hosts=f'{app_config['events']['hostname']}:{app_config['events']['port']}')
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = { "type": "location_reading",
        "datetime" :
            datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": reading }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    ###return NoContent, response.status_code
    return NoContent, 201

def report_time_until_arrival(body):
    #print("Received time until arrival")
    #print(body)
    #msg_data = "Time until arrival for " + body["flight_id"] + " is " + body["actual_arrival_time"]
    #response = requests.post(DATA_STORAGE_URL + "/time-until-arrival", json=body, headers={"Content-Type": "application/json"})
    
    event_name = "time_until_arrival"
    trace_id = generate_trace_id()
    body["trace_id"] = trace_id
    
    #logger.info(f'Received event {event_name} request with a trace id of {trace_id}')
    ###response = requests.post(app_config['eventstore2']['url'], json=body, headers={"Content-Type": "application/json"})
    #logger.info(f"Returned event {event_name} response (Id: {trace_id}) with status {response.status_code}")
    #update_event("arrival_time", msg_data)
    reading = body
    client = KafkaClient(hosts=f'{app_config['events']['hostname']}:{app_config['events']['port']}')
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = { "type": "time_until_arrival_reading",
        "datetime" :
            datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": reading }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    
    #return NoContent, response.status_code
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("lli249-Aircraft-Readings-1.0.0-resolved.yaml",
            strict_validation=True,
            validate_responses=True)

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')

if __name__ == "__main__":
    app.run(port=8080)