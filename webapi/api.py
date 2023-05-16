import json
import logging

from flask import Flask, jsonify, request
from flask_sock import Sock

from labot.data import Msg, Buffer

app = Flask(__name__)
sock = Sock(app)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@sock.route('/ws')
def ws_decoder(ws):
    while True:
        try:
            body = json.loads(ws.receive())
            if body['action'] == 'encode':
                result = Msg.from_json(body['message']).data.hex()
            else:
                result = Msg.fromRaw(Buffer(bytearray.fromhex(body['hex'])), 'client' in body).json()
            ws.send(json.dumps(result))
        except Exception as e:
            print(e)
            ws.send(json.dumps({'error': True}))


@app.route('/encode', methods=['GET', 'POST'])
def rest_encoder():
    body = request.json if request.method == 'POST' else request.args.to_dict()
    return jsonify(Msg.from_json(body['message']).data.hex())


@app.route('/decode', methods=['GET', 'POST'])
def rest_decoder():
    body = request.json if request.method == 'POST' else request.args.to_dict()
    return jsonify(Msg.fromRaw(Buffer(bytearray.fromhex(body['hex'])), 'client' in body).json())


@app.errorhandler(Exception)
def exception_handler(error):
    print('error', error)
    return jsonify({'error': True})


if __name__ == '__main__':
    app.run()
