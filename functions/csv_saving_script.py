import csv

from functions.utilities import variables as vrs
from functions.utilities import utils


def main():
    """
    This function accesses the sheets for each day of Mentor Madness and ONLY SAVES THEM.

    This DOES NOT do any comparisons or alerts.

    This function is from the previous iteration of this system, when the schedules were
    compared using cached CSVs rather than calls to a database.
    """
    # Build Google API response object for sheets
    sheets_api = utils.google_sheets_login()

    # Set spreadsheet ID
    spreadsheet_id = vrs.spreadsheet_id

    # Set query options
    week1 = ['Mon 2/13', 'Tue 2/14', 'Wed 2/15', 'Thu 2/16', 'Fri 2/17']
    week2 = ['Mon 2/20', 'Tue 2/21', 'Wed 2/22', 'Thu 2/23', 'Fri 2/24']
    week3 = ['Mon 2/27', 'Tue 2/28', 'Wed 3/1', 'Thu 3/2', 'Fri 3/3']

    # Determine which days to check for
    sheet_names = week3
    sheet_names = week2
    sheet_names = week1

    full_range = vrs.full_range

    for day in sheet_names:
        # String formatting for API query and file saving
        sheet_query = day + '!' + full_range
        csv_name = utils.day_to_filename(day)

        # Get the sheet
        sheet = utils.get_sheet(sheets_api, spreadsheet_id=spreadsheet_id, sheet_query=sheet_query)

        # Save the sheet
        with open(csv_name, 'w') as file:
            writer = csv.writer(file)
            writer.writerows(sheet)

        print('Saved ' + day)


if __name__ == '__main__':
    main()
