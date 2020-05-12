import configparser
import pika

config = configparser.ConfigParser()
config.read("server.conf")

broker_settings = config['rabbit_mq']['broker_settings']
queue_name = config['rabbit_mq']['queue_name']


def send_message(text):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=broker_settings
    ))

    channel = connection.channel()

    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=text)

    print(" Sent message: '{}'".format(text))
    connection.close()