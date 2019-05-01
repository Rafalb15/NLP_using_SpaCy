from flask import Flask, render_template, request, jsonify
import socket
import sys
import datetime
from mainNLP import NLP
from flask_socketio import SocketIO, emit
from random import random
from time import sleep
from threading import Thread, Event


app = Flask(__name__)
socketio = SocketIO(app)



def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def get_port_number():
    try:
        port_number = int(sys.argv[1])
    except:
        print("Incorrect port number specified")
        exit(1)
    finally:
        return port_number

################################################################################
@socketio.on('connect', namespace='/forward_doc_result')
def start_connect():
    print("Starting socket connection")

@app.route("/")
def hello():
    return render_template("index.html")

@app.route('/query', methods=['POST'])
def form_post():
    response = request.get_json()
    currentDT = datetime.datetime.now()
    print("Query: {}".format(response["message"]))
    return_result = nlp_eng.get_query_from_phrase(response["message"])
    return jsonify("Response: {} | Received: {} | Time elapsed: {} seconds".format(return_result, currentDT.strftime("%Y-%m-%d %H:%M:%S"), nlp_eng.time_elapsed))

@app.route('/document_listener', methods=['POST'])
def get_index_result():
    response = request.get_json(force=True)
    #print(response)
    socketio.emit('newdata', {'document': response["document_list"], 'time': response["time_elapsed"]}, namespace='/forward_doc_result')
    return jsonify("Thanks!, received")



if __name__ == "__main__":
    port_number = get_port_number()
    ip_addr = get_ip_address()
    print("*******************************************************************")
    print ("Connect to http://{}:{} to view the service".format(ip_addr, port_number))
    print("*******************************************************************")
    nlp_eng = NLP()
    socketio.run(app, host='0.0.0.0', port=port_number, debug=True)
