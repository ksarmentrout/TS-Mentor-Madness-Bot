# Mentor Madness Scheduling Hub

Interfaces between youcanbook.me, Google Calendar, and Google Sheets.

This is for internal use for Techstars Boston to handle Mentor Madness
scheduling and notification.

A Google Sheets spreadsheet is the heart of the organizational
flow so that multiple people can edit the schedule independently and so 
that it can be easily displayed.


## Uses:
This set of tools does the following:
* Automatically populates the Google Sheets with mentor names as they sign
up on youcanbook.me. 
    * They are placed on all half-hour meetings within the 
timeslot they chose.
    * The mentors are placed in one room for their entire time slot,
    if possible. 
* Sends email alerts to companies/associates about their meetings.
    * The spreadsheet is monitored, so each person receives notifications when 
    their meetings were added, cancelled, or changed.
* Maintains separate Google Calendars for each company and associate,
with up-to-date information about time, location, and mentor. 
* Generates individualized schedules to be given to mentors, along with
email bodies that can be sent out as reminders.


## Web App
This set of tools was originally used by manually running scripts and
changing them on the fly. The web app version is a work in progress,
but is built in Flask and deployed on AWS Elastic Beanstalk.
