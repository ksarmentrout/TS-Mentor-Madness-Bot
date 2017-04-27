import json
import os
import sys
import datetime

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'functions/'))
import logging
from logging import FileHandler

from flask import Flask, render_template, request, Response, flash, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy

from functions.utilities import utils
from functions.utilities import variables as vrs
from functions.utilities import directories as dr
from functions import (
    csv_saving_script, daily_notice, email_sender, exceptions,
    gcal_scheduler, generate_mentor_schedules, meeting,
    sheets_scheduler, update_script, weekly_notice, meeting_stats
)
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


@application.route('/view_schedule', methods=['POST'])
def view_schedule():
    form_data = request.form.to_dict()
    page_dict = {
        'daily_or_weekly': form_data.get('daily_or_weekly'),
        'name': form_data.get('names')
    }

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
        page_dict['date'] = [formatted_date]

    elif form_data.get('daily_or_weekly') == 'weekly':
        if not form_data.get('week-picker'):
            flash('Please choose a week to view the schedule. ' + str(form_data))
            return redirect(url_for('dashboard'))
        elif not form_data.get('names'):
            flash('Please choose a person or team to view their schedule.')
            return redirect(url_for('dashboard'))

        # Format the data
        page_dict['date'] = utils.format_week_picked(form_data['week-picker'])
    else:
        return False

    meeting_dict = db.get_meeting_views(page_dict)
    page_dict['meetings'] = meeting_dict

    return render_template(
        'view_schedule.html',
        **page_dict
    )


@application.route('/email_schedule', methods=['POST'])
def email_schedule():
    # flash('schedule emailing is not yet implemented')
    # return redirect(url_for('dashboard'))
    form_data = request.form.to_dict()
    page_dict = {
        'daily_or_weekly': form_data.get('daily_or_weekly'),
        'name': form_data.get('names')
    }

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
        page_dict['date'] = [formatted_date]

    elif form_data.get('daily_or_weekly') == 'weekly':
        if not form_data.get('week-picker'):
            flash('Please choose a week to view the schedule. ' + str(form_data))
            return redirect(url_for('dashboard'))
        elif not form_data.get('names'):
            flash('Please choose a person or team to view their schedule.')
            return redirect(url_for('dashboard'))

        # Format the data
        page_dict['date'] = utils.format_week_picked(form_data['week-picker'])
    else:
        return False

    meeting_dict = db.get_meeting_views(page_dict)
    page_dict['meetings'] = meeting_dict

    return render_template(
        'view_schedule.html',
        **page_dict
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
