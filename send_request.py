import json
import requests

class POST_request():
    def __init__(self, url, port_number, dir):
        self.url = url
        self.port_number = port_number
        self.dir = dir

    def get_url(self):
        return self.url

    def get_port(self):
        return self.port_number

    def get_dir(self):
        return self.dir

    def set_url(self, new_url):
        self.url = new_url
        return "New url {}".format(self.url)

    def set_port(self, new_port):
        self.port_number = new_port
        return "New port {}".format(self.port_number)

    def set_dir(self, new_dir):
        self.dir = new_dir
        return "New dir {}".format(self.dir)

    def send_message(self, document_id, time):
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'document_list': document_id,
            'time_elapsed': time
        }
        url = "http://{}:{}/{}".format(self.url, self.port_number, self.dir)
        return_str = ""
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=0.5)
            #response.raise_for_status()
            return_str = response.json()
        except Exception as e:
            return_str = "{}\nTimeout set to 0.5 second".format(e)
        finally:
            return return_str
