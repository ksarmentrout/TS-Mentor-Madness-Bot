from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/added_booking', methods=['POST'])
def added_booking():
    return


@app.route('/cancelled_booking', methods=['POST'])
def cancelled_booking():
    return


@app.route('/changed_booking', methods=['POST'])
def changed_booking():
    return


if __name__ == '__main__':
    app.run()
