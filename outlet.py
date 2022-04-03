import wiringpi as wp
from flask import Blueprint, jsonify, abort, request, render_template
from relaydefinitions import relays, relayIdToPin

outlet = Blueprint("outlet", __name__, static_folder="static", template_folder="template")

PIN_OFFSET = 65

I2C_ADDR_01 = 0x20
I2C_ADDR_02 = 0x22

wp.wiringPiSetup()
wp.mcp23017Setup(PIN_OFFSET, I2C_ADDR_01)

relayStateToWiringPiState = {
    'off'   : 0,
    'on'    : 1
    }

for relay in relays:
    wp.pinMode(relayIdToPin[relay['id']], 1)
    wp.digitalWrite(relayIdToPin[relay['id']], relayStateToWiringPiState[relay['state']])


def UpdatePinFromRelayObject(relay):
    wp.digitalWrite(relayIdToPin[relay['id']], relayStateToWiringPiState[relay['state']])


@outlet.route('/WebRelay/api/relays', methods=['GET'])
def get_relays():
    return jsonify({'relays' : relays})


@outlet.route('/WebRelay/api/relays/<int:relay_id>', methods=['PUT'])
def update_relay(relay_id):
    matchingRelays = [relay for relay in relays in relay['id'] == relay_id]

    if len(matchingRelays) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if not 'state' in request.json:
        abort(400)

    relay = matchingRelays[0]
    relay['state'] = request.json.get('state')
    return jsonify({'relay': relay})