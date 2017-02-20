import json
import os

from flask import Flask, render_template, request, Response
from functions import utils
from functions import sheets_scheduler

app = Flask(__name__)


@app.route('/')
def landing_page():
    return render_template('landing_page.html')


@app.route('/added_booking', methods=['POST', 'GET'])
def added_booking():
    if request.method == 'POST':
        try:
            with open('static/webhook_json.txt', 'a') as file:
                webhook_dict = json.dumps(request.get_json())
                file.write(webhook_dict)

            # wh_dict = json.dumps(request.get_json())
            wh_dict = json.loads(webhook_dict)
            sheets_scheduler.add_booking(wh_dict)

            js = json.dumps({'success': True, 'ContentType': 'application/json'})
            response = Response(js, status=201, mimetype='application/json')
            return response
        except Exception:
            js = json.dumps({'success': False}), 500, {'ContentType': 'application/json'}
            response = Response(js, status=500, mimetype='application/json')
            return response
    else:
        try:
            with open('static/webhook_json.txt') as file:
                webhook_json = file.read()
            return render_template('webhook_display.html', webhook_json=webhook_json)
        except Exception as exc:
            return str(exc)


@app.route('/cancelled_booking', methods=['POST'])
def cancelled_booking():
    try:
        webhook_dict = request.get_json()
        sheets_scheduler.remove_booking(webhook_dict)

        js = json.dumps({'success': True, 'ContentType': 'application/json'})
        response = Response(js, status=201, mimetype='application/json')
        return response
    except Exception:
        js = json.dumps({'success': False}), 500, {'ContentType': 'application/json'}
        response = Response(js, status=500, mimetype='application/json')
        return response


@app.route('/changed_booking', methods=['POST'])
def changed_booking():
    try:
        webhook_dict = request.get_json()
        sheets_scheduler.change_booking(webhook_dict)

        js = json.dumps({'success': True, 'ContentType': 'application/json'})
        response = Response(js, status=201, mimetype='application/json')
        return response
    except Exception:
        js = json.dumps({'success': False}), 500, {'ContentType': 'application/json'}
        response = Response(js, status=500, mimetype='application/json')
        return response


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
