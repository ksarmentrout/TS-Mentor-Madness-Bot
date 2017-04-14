import json
import os
import sys
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'functions/'))
import logging
from logging import FileHandler

from flask import Flask, render_template, request, Response, flash, redirect, url_for

from functions.utilities import utils
from functions.utilities import variables as vrs
from functions.utilities import directories as dr
from functions import (
    csv_saving_script, daily_notice, email_sender, exceptions,
    gcal_scheduler, generate_mentor_schedules, meeting,
    sheets_scheduler, update_script, weekly_notice
)

application = Flask(__name__)
application.secret_key = 'super secret key'

print(os.path.abspath(__file__))

# Add logging
file_handler = FileHandler("debug.log","a")
file_handler.setLevel(logging.WARNING)
application.logger.addHandler(file_handler)


@application.route('/')
def landing_page():
    return render_template('landing_page.html')


@application.route('/dashboard', methods=['GET'])
def dashboard():
    name_list = [
        'Everyone',
        'Companies Only',
        'Associates Only'
    ]
    proper_name_list = name_list.copy()
    proper_name_list.extend(dr.all_proper_names)

    name_list.extend(dr.all_names)

    return render_template(
        'dashboard.html',
        days=vrs.sheet_options,
        weeks=vrs.weeks,
        all_names=name_list,
        all_proper_names=proper_name_list
    )


@application.route('/view_schedule', methods=['POST'])
def view_schedule():
    # flash(request.form)
    # return redirect(url_for('dashboard'))
    form_data = request.form


    if form_data.get('daily_or_weekly') == 'daily':
        if not form_data.get('day-picker'):
            flash('Please choose a day to view the schedule. ' + str(form_data))
            return redirect(url_for('dashboard'))
        elif not form_data.get('names'):
            flash('Please choose a person or team to view their schedule.')
            return redirect(url_for('dashboard'))

    elif form_data.get('daily_or_weekly') == 'weekly':
        if not form_data.get('week-picker'):
            flash('Please choose a week to view the schedule. ' + str(form_data))
            return redirect(url_for('dashboard'))
        # elif not form_data.get('names'):
        #     flash('Please choose a person or team to view their schedule.')
        #     return redirect(url_for('dashboard'))
    else:
        return False

    # TODO: Implement call to database

    return render_template(
        'variable_display.html',
        variable=form_data
    )


@application.route('/email_schedule', methods=['POST'])
def email_schedule():
    flash('schedule was emailed')
    return redirect(url_for('dashboard'))


@application.route('/update_db', methods=['POST'])
def update_db():
    try:
        update_script.main()
        return True
    except:
        return False








@application.route('/added_booking', methods=['POST', 'GET'])
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
            flash('hello, Keaton')
            return redirect(url_for('landing_page'))
            # return render_template('webhook_display.html', webhook_json=webhook_json)
        except Exception as exc:
            return str(exc)


@application.route('/cancelled_booking', methods=['POST'])
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


@application.route('/changed_booking', methods=['POST'])
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
    # port = int(os.environ.get('PORT', 5000))
    application.run()
