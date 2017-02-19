import json
import os

from flask import Flask, render_template, request, Response
from functions import utils

app = Flask(__name__)


@app.route('/')
def landing_page():
    return render_template('landing_page.html')


@app.route('/added_booking', methods=['POST', 'GET'])
def added_booking():
    # {"first_name": "Keaton", "last_name": "Armentrout", "end_time": "2/19/17 4:00 PM", "duration": "1 hour", "start_time": "2/19/17 3:00 PM", "email": "keaton.armentrout@techstarsassociates.com"}

    if request.method == 'POST':
        try:
            with open('static/webhook_json.txt', 'a') as file:
                file.write(request.data)
                file.write('\n')
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
    return


@app.route('/changed_booking', methods=['POST'])
def changed_booking():
    return


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
