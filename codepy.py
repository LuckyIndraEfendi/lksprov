import os
import json
import boto3
import paho.mqtt.client as mqtt
from datetime import datetime
from decimal import Decimal

mqtt_broker = os.environ.get('MQTT_BROKER')
mqtt_port = int(os.environ.get('MQTT_PORT'))
mqtt_topic = os.environ.get('MQTT_TOPIC')

aws_access_key = os.environ.get('AWS_ACCESS_KEY')
aws_secret_key = os.environ.get('AWS_SECRET_KEY')
s3_bucket = os.environ.get('S3_BUCKET')
s3_region = os.environ.get('S3_REGION')

dynamodb_table = os.environ.get('DYNAMODB_TABLE')
dynamodb_region = os.environ.get('DYNAMODB_REGION')

mqtt_username = os.environ.get('MQTT_USERNAME')
mqtt_password = os.environ.get('MQTT_PASSWORD')

def on_connect(client, userdata, flags, rc):
    print('Terhubung dengan broker MQTT')
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode('utf-8'))

    suhu = Decimal(str(payload.get('suhu')))
    kelembaban = Decimal(str(payload.get('kelembaban')))

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f'{topic}/{timestamp}.json'

    s3_client = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=s3_region)
    s3_client.put_object(Body=json.dumps(payload), Bucket=s3_bucket, Key=file_name)

    dynamodb = boto3.resource('dynamodb', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=dynamodb_region)
    table = dynamodb.Table(dynamodb_table)
    payload['timestamp'] = timestamp
    payload['suhu'] = suhu
    payload['kelembaban'] = kelembaban
    payload['sensor_id'] = topic.split('/')[1]
    table.put_item(Item=payload)

client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_password)
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)

client.loop_forever()
