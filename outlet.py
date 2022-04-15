import time
import serial
import wiringpi as wp
from flask import Blueprint, jsonify, abort, request, url_for, render_template
from relaydefinitions import relays, relayIdToPin

outlet = Blueprint("outlet", __name__, static_folder="static", template_folder="templates")

PIN_OFFSET = 65

I2C_ADDR_01 = 0x20
I2C_ADDR_02 = 0x22

wp.wiringPiSetup()
wp.mcp23017Setup(PIN_OFFSET, I2C_ADDR_01)

relayStateToWiringPiState = {
    'off'   : 1,
    'on'    : 0
    }

for relay in relays:
    wp.pinMode(relayIdToPin[relay['id']], 1)
    wp.digitalWrite(relayIdToPin[relay['id']], relayStateToWiringPiState[relay['state']])


def UpdatePinFromRelayObject(relay):
    wp.digitalWrite(relayIdToPin[relay['id']], relayStateToWiringPiState[relay['state']])

@outlet.route('/', methods=['GET'])
def index():
    ip_address = request.environ['REMOTE_ADDR']
    clock = time.strftime("%a, %B %d %l:%M%p")

    return render_template('index.html', ipa=ip_address, clock=clock);


@outlet.route('/api/relays', methods=['GET'])
def get_relays():
    return jsonify({'relays' : relays})


@outlet.route('/api/relays/<int:relay_id>', methods=['GET'])
def get_relay(relay_id):
    matchingRelays = [relay for relay in relays if relay['id'] == relay_id]
    if len(matchingRelays) == 0:
        abort(404)
    return jsonify({'relay': matchingRelays[0]})


@outlet.route('/api/relays/<int:relay_id>', methods=['PUT'])
def update_relay(relay_id):
    matchingRelays = [relay for relay in relays if relay['id'] == relay_id]

    if len(matchingRelays) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if not 'state' in request.json:
        abort(400)

    relay = matchingRelays[0]
    relay['state'] = request.json.get('state')
    UpdatePinFromRelayObject(relay)
    return jsonify({'relay': relay})