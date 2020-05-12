import configparser
import pika

config = configparser.ConfigParser()
config.read("client.conf")

broker_settings = config['rabbit_mq']['broker_settings']
queue_name = config['rabbit_mq']['queue_name']

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=broker_settings
))
channel = connection.channel()

channel.queue_declare(queue=queue_name)


def callback(ch, method, properties, body):
    print(" Received message: %r" % (body,))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(queue_name,
                      callback)

print(' Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
