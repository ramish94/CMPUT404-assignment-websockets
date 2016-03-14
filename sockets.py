#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2013-2014 Abram Hindle
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import flask
from flask import Flask
from flask import redirect
from flask import request
from flask import url_for
from flask import jsonify
from flask import send_from_directory
from flask_sockets import Sockets
import gevent
from gevent import queue
import time
import json
import os

app = Flask(__name__)
sockets = Sockets(app)
app.debug = True


# Sourced from Dr. Hindles in class Sockets example: https://github.com/abramhindle/WebSocketsExamples/blob/master/broadcaster.py
class Client:
    def __init__(self):
        self.queue = queue.Queue()

    def put(self, v):
        self.queue.put_nowait(v)

    def get(self):
        return self.queue.get()

class World:
    def __init__(self):
        self.clear()
        self.listeners = list()
        
    def add_set_listener(self, listener):
        self.listeners.append( listener )

    def update(self, entity, key, value):
        entry = self.space.get(entity,dict())
        entry[key] = value
        self.space[entity] = entry
        self.update_listeners( entity )

    def set(self, entity, data):
        self.space[entity] = data
        self.update_listeners( entity )

    def update_listeners(self, entity):
        '''update the set listeners'''
        for listener in self.listeners:
            listener(entity, self.get(entity))

    def clear(self):
        self.space = dict()

    def get(self, entity):
        return self.space.get(entity,dict())
    
    def world(self):
        return self.space

myWorld = World()

# Sourced from Dr. Hindles in class Sockets example: https://github.com/abramhindle/WebSocketsExamples/blob/master/broadcaster.py
clientsList = list()

# Sourced from Dr. Hindles in class Sockets example: https://github.com/abramhindle/WebSocketsExamples/blob/master/broadcaster.py
def send_all(msg):
    for c in clientsList:
        c.put(msg)

# Sourced from Dr. Hindles in class Sockets example: https://github.com/abramhindle/WebSocketsExamples/blob/master/broadcaster.py
def send_all_json(obj):
    send_all(json.dumps(obj))        

def set_listener( entity, data ):
    ''' do something with the update ! '''
    m = json.dumps({entity:data})
    for c in clientsList:
        c.put(m)     

myWorld.add_set_listener( set_listener )
      
@app.route('/')
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''
    return send_from_directory('static', 'index.html')

# Sourced from Dr. Hindles in class Sockets example: https://github.com/abramhindle/WebSocketsExamples/blob/master/broadcaster.py
# Changed to set key and value to world
def read_ws(ws, client):
    '''A greenlet function that reads from the websocket and updates the world'''
    try:
        while True:
            m = ws.receive()
            print "Web Socket recv: %s" % m
            if (m is not None):
                m = json.loads(m)
                for key in m:
                    val = m[key]
                    myWorld.set(key, val)
            else:
                break
    except:
        '''Done'''

# Sourced from Dr. Hindles in class Sockets example: https://github.com/abramhindle/WebSocketsExamples/blob/master/broadcaster.py
@sockets.route('/subscribe')
def subscribe_socket(ws):
    '''Fufill the websocket URL of /subscribe, every update notify the
       websocket and read updates from the websocket '''
    c = Client()
    clientsList.append(c)
    json.dumps(myWorld.world())
    g = gevent.spawn(read_ws, ws, c)
    print "Subscribing"   
    try:
        while True:
            m = c.get()
            ws.send(m)

    except Exception as e: # WebSocketError as e:
        print "Web Socket Error %s" % e
    finally:
        clientsList.remove(c)
        gevent.kill(g)

def flask_post_json(request):
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data != ''):
        return json.loads(request.data)
    else:
        return json.loads(request.form.keys()[0])

@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    '''update the entities via this interface'''
    d = flask_post_json(request)

    if request.method == "PUT":
        for key, val in d.iteritems():
            myWorld.update(entity, key, val)

    elif request.method == "POST":
        myWorld.set(entity, d)

    return jsonify(myWorld.get(entity))

@app.route("/world", methods=['POST','GET'])    
def world():
    '''you should probably return the world here'''
    return jsonify(myWorld.world())

@app.route("/entity/<entity>")    
def get_entity(entity):
    '''This is the GET version of the entity interface, 
       return a representation of the entity'''
    return jsonify(**myWorld.get(entity))

@app.route("/clear", methods=['POST','GET'])
def clear():
    '''Clear the world out!'''
    myWorld.clear()
    return jsonify(myWorld.world())

if __name__ == "__main__":
    ''' This doesn't work well anymore:
        pip install gunicorn
        and run
        gunicorn -k flask_sockets.worker sockets:app
    '''
    app.run()
