import connexion
from connexion import NoContent
import json
import datetime
from datetime import datetime
import yaml
import logging.config, logging
from pykafka import KafkaClient
from collections import defaultdict
from flask import jsonify

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("lli249-Aircraft_readings-1.0.0-resolved.yaml",
            strict_validation=True,
            validate_responses=True)

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')

def get_aircraft_location_reading(index):
    """ Get location Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,consumer_timeout_ms=1000)
    logger.info("Retrieving location at index %d" % index)
    current_index = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
                # Find the event at the index you want and
                # return code 200
                # i.e., return event,
            if msg.get("type")== "location_reading":
                if current_index == index:
                    event = msg.get("payload")
                    logger.info("Found location reading at index %d" % (index))
                    return event, 200
                current_index += 1
            
    except:
        logger.error("No more messages found")
    logger.error("Could not find BP at index %d" % index)
    return { "message": "Not Found"}, 404


def get_aircraft_time_until_arrival_reading(index):
    """ Get time-until-arrival Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,consumer_timeout_ms=1000)
    logger.info("Retrieving time-until-arrival at index %d" % index)
    current_index = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg.get("type")== "time_until_arrival_reading":
                if current_index == index:
                    event = msg.get("payload")
                    logger.info("Found time-until-arrival reading at index %d" % (index))
                    return event, 200
                current_index += 1
                # Find the event at the index you want and
                # return code 200
                # i.e., return event, 200
    except:
        logger.error("No more messages found")
    logger.error("Could not find time-until-arrival at index %d" % index)
    return { "message": "Not Found"}, 404

def get_event_stats():
    hostname = "%s:%d" % (app_config["events"]["hostname"],app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    event_counts = defaultdict(int)

    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            event_type = msg.get("type")
            if event_type:
                event_counts[event_type] += 1

    except Exception as e:
        logger.error(f"Error reading messages: {str(e)}")
        return jsonify({"message": "Error retrieving stats"}), 500

    logger.info("Successfully retrieved event type stats")
    return jsonify(event_counts), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8110)
