import configparser
import urllib.request
import ntpath
import requests
import time


from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from server.send import send_message

config = configparser.ConfigParser()
config.read("server.conf")

path_source = config['server']['server_path']

client_url_path = config['server']['url_path']


class Handler(FileSystemEventHandler):

    def on_created(self, event):
        file_name = ntpath.basename(event.src_path)
        file = {'file': (file_name, open(event.src_path, 'rb'))}
        try:
            request = requests.post(client_url_path, files=file)
            if request.status_code == requests.codes.ok:
                send_message('File {} created on source: {}'.format(
                    file_name, client_url_path))
            else:
                print("Something was wrong with adding file {} on "
                      "source {}").format(
                    file_name, client_url_path
                )
        except requests.exceptions.ConnectionError:
            self.failed_to_connect()

    def on_modified(self, event):
        file_name = ntpath.basename(event.src_path)
        file = {'file': (file_name, open(event.src_path, 'rb'))}
        try:
            request = requests.put(client_url_path, files=file)
            if request.status_code == requests.codes.ok:
                send_message('File {} modified on source: {}'.format(
                    file_name, client_url_path))
            else:
                print("Something was wrong with modifying file {} on "
                      "source {}").format(
                    file_name, client_url_path
                )
        except requests.exceptions.ConnectionError:
            self.failed_to_connect()

    def on_moved(self, event):
        file_name = ntpath.basename(event.dest_path)
        delete_url_path = client_url_path + '/{}'.format(event.src_path)
        file = {'file': (file_name, open(event.dest_path, 'rb'))}
        try:
            move_request = requests.post(client_url_path, files=file)
            if move_request.status_code == requests.codes.ok:
                delete_request = requests.delete(delete_url_path)
                if delete_request.status_code == requests.codes.ok:
                    send_message(
                        'File {} was moved from {} to {} on source {}'.format(
                            file_name, event.src_path, event.dest_path,
                            client_url_path
                        )
                    )
                else:
                    print("Something was wrong with deleting file {} on "
                          "source {}").format(
                        file_name, client_url_path
                    )
            else:
                print("Something was wrong with moving file {} on "
                      "source {}").format(
                    file_name, client_url_path
                )

        except requests.exceptions.ConnectionError:
            self.failed_to_connect()

    def on_deleted(self, event):
        file_name = ntpath.basename(event.src_path)
        delete_url_path = client_url_path + '/{}'.format(event.src_path)
        try:
            request = requests.delete(delete_url_path)
            if request.status_code == requests.codes.ok:
                send_message('File {} deleted on source: {}'.format(
                    file_name, client_url_path))
            else:
                print("Something was wrong with deleting file {} on "
                      "source {}").format(
                    file_name, client_url_path
                )
        except requests.exceptions.ConnectionError:
            self.failed_to_connect()

    @staticmethod
    def failed_to_connect():
        print("Connection with server {} has been lost").format(
            client_url_path
        )


observer = Observer()
observer.schedule(Handler(), path=path_source, recursive=True)
observer.start()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    observer.stop()
observer.join()

