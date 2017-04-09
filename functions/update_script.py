import csv

import gcal_scheduler
import utils
import email_sender
import variables as vrs


def main():
    # Make Google API object
    sheets_api = utils.google_sheets_login()

    # Set variables
    spreadsheet_id = vrs.spreadsheet_id
    room_mapping = vrs.room_mapping
    sheet_options = vrs.sheet_options
    full_range = vrs.full_range
    lookahead = vrs.lookahead_days

    # Determine which days to check for.
    # Find index of today's date
    today_date = utils.get_today(skip_weekends=True)
    day_index = -1
    for idx, date in enumerate(sheet_options):
        if today_date in date:
            day_index = idx
            break

    if day_index == -1:
        raise IndexError("Today's date not found within sheet_options."
                         "If Mentor Madness has ended, please shut off this"
                         "update script.")

    # Set the days to check, without worrying about going past the program end
    sheet_names = [sheet_options[day_index]]
    idx = 1
    while lookahead > 0:
        try:
            sheet_names.append(sheet_options[day_index + idx])
            idx += 1
            lookahead -= 1
        except IndexError:
            break

    # Create holding variables for adding and deleting messages
    adding_msgs = []
    deleting_msgs = []

    for day in sheet_names:
        # String formatting for API query and file saving
        sheet_query = day + '!' + full_range
        csv_name = utils.day_to_filename(day)

        # Make request for sheet
        sheet = sheets_api.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_query).execute()
        new_sheet = sheet['values']
        for idx, new_sheet_row in enumerate(new_sheet):
            if len(new_sheet_row) < vrs.row_length:
                new_sheet[idx].extend([''] * (vrs.row_length - len(new_sheet_row)))

        # Load old sheet
        old_sheet = open(csv_name, 'r')
        reader = csv.reader(old_sheet)

        row_counter = 0
        for old_row in reader:
            new_row = new_sheet[row_counter]
            timeslot = new_row[0]

            # Make rows the same length if they are not
            if len(old_row) < len(new_row):
                old_row.extend([''] * (len(new_row) - len(old_row)))
            elif len(old_row) > len(new_row):
                new_row.extend([''] * (len(old_row) - len(new_row)))

            # Iterate over rooms
            for room_num in range(1, len(room_mapping) + 1):
                # Get descriptive variables of room
                room_dict = room_mapping[room_num]
                room_name = room_dict['name']
                mentor_name = new_row[room_dict['mentor_col']]

                for col_num in room_dict['check_range']:
                    old_name = old_row[col_num]
                    new_name = new_row[col_num]
                    if new_name != old_name:
                        new_event_dict = {'time': timeslot, 'name': new_name, 'mentor': mentor_name,
                                          'room_num': str(room_num), 'room_name': room_name, 'day': day}
                        old_event_dict = {'time': timeslot, 'name': old_name, 'mentor': mentor_name,
                                          'room_num': str(room_num), 'room_name': room_name, 'day': day}

                        if new_name and old_name:
                            # Someone was changed, assuming the names are different
                            if utils.process_name(new_name) != utils.process_name(old_name):
                                deleting_msgs.append(old_event_dict)
                                adding_msgs.append(new_event_dict)
                            else:
                                continue
                        elif old_name:
                            # Someone was deleted
                            deleting_msgs.append(old_event_dict)
                        elif new_name:
                            # Someone was added
                            adding_msgs.append(new_event_dict)

            row_counter += 1

        # Save the sheet
        old_sheet.close()
        old_sheet = open(csv_name, 'w')
        writer = csv.writer(old_sheet)
        writer.writerows(new_sheet)

    email_sender.send_update_mail(adding_msgs, deleting_msgs)
    gcal_scheduler.add_cal_events(adding_msgs)
    gcal_scheduler.delete_cal_events(deleting_msgs)


if __name__ == '__main__':
    main()
    print('Ran successfully')
