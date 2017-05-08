import json
import os
import sys
import datetime
import traceback

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'functions/'))
import logging
from logging import FileHandler

from flask import Flask, render_template, request, Response, flash, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy

from functions.utilities import utils
from functions.utilities import variables as vrs
from functions.utilities import directories as dr

from functions import (
    csv_saving_script, schedule_handler, email_sender,
    gcal_scheduler, generate_mentor_schedules, meeting,
    sheets_scheduler, update_script, meeting_stats
)
from functions.exceptions import *
from functions.database import db_interface as db

application = Flask(__name__)
application.secret_key = 'super secret key'
# db = SQLAlchemy(application)

print(os.path.abspath(__file__))

# Add logging
file_handler = FileHandler("debug.log", "a")
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

    associate_proper_names = dr.associate_proper_names
    company_proper_names = dr.company_proper_names
    mentor_names = meeting_stats.get_mentor_list()

    # Need to sort week names
    week_names = list(vrs.weeks.keys())
    week_names.sort()

    # Get today's date
    today = datetime.datetime.today()
    today = '{dy:%A}, {dy.month}/{dy.day}/{dy.year}'.format(dy=today)

    return render_template(
        'dashboard.html',
        days=vrs.sheet_options,
        week_dict=vrs.weeks,
        week_names=week_names,
        all_names=name_list,
        all_proper_names=proper_name_list,
        associate_names=associate_proper_names,
        company_names=company_proper_names,
        mentor_names=mentor_names,
        todays_date=today
    )


@application.route('/view_tomorrow_schedule', methods=['GET', 'POST'])
def view_tomorrow_schedule():
    name = 'everyone'
    daily_or_weekly = 'daily'

    # Get a dict of meetings
    try:
        meetings = schedule_handler.get_meeting_views(
            name=name,
            daily_or_weekly=daily_or_weekly
        )
        # Break into associate and company lists
        associate_company_meeting_dict = utils.associate_and_company_meetings_dict(meetings)
    except IndexError:
        tomorrow = utils.get_next_day()
        flash('No meetings were found for the date ' + tomorrow + '.')
        return redirect(url_for('dashboard'))

    return render_template(
        'view_schedule.html',
        **associate_company_meeting_dict
    )


@application.route('/view_next_week_schedule', methods=['GET', 'POST'])
def view_next_week_schedule():
    name = 'everyone'
    daily_or_weekly = 'weekly'

    # Get a dict of meetings
    try:
        meetings = schedule_handler.get_meeting_views(
            name=name,
            daily_or_weekly=daily_or_weekly
        )
    except IndexError:
        next_week = utils.get_next_week()

        flash('No meetings were found for the date ' + next_week + '.')
        return redirect(url_for('dashboard'))

    # Break into associate and company lists
    associate_company_meeting_dict = utils.associate_and_company_meetings_dict(meetings)

    return render_template(
        'view_schedule.html',
        **associate_company_meeting_dict
    )


@application.route('/email_tomorrow_schedule', methods=['POST'])
def email_tomorrow_schedule():
    name = 'everyone'
    daily_or_weekly = 'daily'

    # Get schedules and send emails
    try:
        schedule_handler.email_meetings(name, daily_or_weekly)
        flash('Emails were sent successfully.')
        return redirect(url_for('dashboard'))

    except Exception:
        tb = sys.exc_traceback
        variable = ''.join(traceback.format_tb(tb))
        return render_template(
            'variable_display.html',
            variable=variable
        )


@application.route('/email_next_week_schedule', methods=['POST'])
def email_next_week_schedule():
    name = 'everyone'
    daily_or_weekly = 'weekly'

    # Get schedules and send emails
    try:
        schedule_handler.email_meetings(name, daily_or_weekly)
        flash('Emails were sent successfully.')
        return redirect(url_for('dashboard'))

    except Exception:
        tb = sys.exc_traceback
        variable = ''.join(traceback.format_tb(tb))
        return render_template(
            'variable_display.html',
            variable=variable
        )


@application.route('/view_schedule', methods=['POST'])
def view_schedule():
    form_data = request.form.to_dict()
    daily_or_weekly = form_data.get('daily_or_weekly')
    name = form_data.get('names')

    # Check if it's weekly or daily
    if form_data.get('daily_or_weekly') == 'daily':
        # Ensure that the data is available
        if not form_data.get('day-picker'):
            flash('Please choose a day to view the schedule. ' + str(form_data))
            return redirect(url_for('dashboard'))
        elif not form_data.get('names'):
            flash('Please choose a person or team to view their schedule.')
            return redirect(url_for('dashboard'))

        # Format the data
        formatted_date = utils.format_day_picked(form_data['day-picker'])
        date = [formatted_date]

    elif form_data.get('daily_or_weekly') == 'weekly':
        if not form_data.get('week-picker'):
            flash('Please choose a week to view the schedule. ' + str(form_data))
            return redirect(url_for('dashboard'))
        elif not form_data.get('names'):
            flash('Please choose a person or team to view their schedule.')
            return redirect(url_for('dashboard'))

        # Format the data
        date = utils.format_week_picked(form_data['week-picker'])
    else:
        return False

    # Get a dict of meetings
    meetings = schedule_handler.get_meeting_views(
        name=name,
        specific_date=date,
        daily_or_weekly=daily_or_weekly
    )

    # Break into associate and company lists
    associate_company_meeting_dict = utils.associate_and_company_meetings_dict(meetings)

    return render_template(
        'view_schedule.html',
        **associate_company_meeting_dict
    )


@application.route('/email_schedule', methods=['POST'])
def email_schedule():
    form_data = request.form.to_dict()
    daily_or_weekly = form_data.get('daily_or_weekly'),
    name = form_data.get('names')

    # Check if it's weekly or daily
    if form_data.get('daily_or_weekly') == 'daily':
        # Ensure that the data is available
        if not form_data.get('day-picker'):
            flash('Please choose a day to view the schedule. ' + str(form_data))
            return redirect(url_for('dashboard'))
        elif not form_data.get('names'):
            flash('Please choose a person or team to view their schedule.')
            return redirect(url_for('dashboard'))

        specific_date = form_data['day-picker']

    elif form_data.get('daily_or_weekly') == 'weekly':
        if not form_data.get('week-picker'):
            flash('Please choose a week to view the schedule. ' + str(form_data))
            return redirect(url_for('dashboard'))
        elif not form_data.get('names'):
            flash('Please choose a person or team to view their schedule.')
            return redirect(url_for('dashboard'))

        specific_date = form_data['week_picker']
    else:
        return False

    # Get schedules and send emails
    try:
        schedule_handler.email_meetings(name, specific_date, daily_or_weekly)
        flash('Emails were sent successfully.')
        return redirect(url_for('dashboard'))

    except Exception:
        tb = sys.exc_traceback
        variable = ''.join(traceback.format_tb(tb))
        return render_template(
            'variable_display.html',
            variable=variable
        )


@application.route('/update_db', methods=['POST'])
def update_db():
    try:
        update_script.main()
        return True
    except:
        return False


@application.route('/stats', methods=['POST'])
def stats():
    stats_table = meeting_stats.get_stats()

    return render_template(
        'stats.html',
    )


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
