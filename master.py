import json
import os

from flask import Flask, render_template, request, url_for
from functions import utils

app = Flask(__name__)


@app.route('/')
def landing_page():
    return render_template('landing_page.html')


@app.route('/added_booking', methods=['POST', 'GET'])
def added_booking():
    # {"first_name": "Keaton", "last_name": "Armentrout", "end_time": "2/19/17 4:00 PM", "duration": "1 hour", "start_time": "2/19/17 3:00 PM", "email": "keaton.armentrout@techstarsassociates.com"}

    if request.method == 'POST':
        with open(url_for('static', filename='webhook_json.txt'), 'w') as file:
            file.write(request.form)
        return
    else:
        try:
            with open(url_for('static', filename='webhook_json.txt')) as file:
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
