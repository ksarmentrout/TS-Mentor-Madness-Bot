import json
import os

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/added_booking', methods=['POST'])
def added_booking():
    # {"first_name": "Keaton", "last_name": "Armentrout", "end_time": "2/19/17 4:00 PM", "duration": "1 hour", "start_time": "2/19/17 3:00 PM", "email": "keaton.armentrout@techstarsassociates.com"}
    return


@app.route('/cancelled_booking', methods=['POST'])
def cancelled_booking():
    return


@app.route('/changed_booking', methods=['POST'])
def changed_booking():
    return


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
