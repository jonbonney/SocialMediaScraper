import requests
from webpage import read_config
import time
import re
import pandas
from os.path import exists


def parse(html):
    p = r'"joinedDateText":{"runs":\[{"text":"Joined "},{"text":"(?P<join_date>[^"]*)"}]}'
    join_date = re.search(p, html, re.DOTALL).group('join_date')
    return join_date


def main():
    # Start timer to track how long the program has been running
    time_start = time.perf_counter()

    # Get config file properties
    config = read_config()
    user_agent = config['user_agent']
    print('user_agent: ', user_agent)
    timeout = config['timeout']
    conn_limit = config['conn_limit']

    headers = {'User-Agent': user_agent}

    # Import youtube channels and users
    excel_path = 'data/socials2.xlsx'
    print('Importing data...')
    channel_ids = pandas.read_excel(excel_path, usecols=['YouTube ID'])['YouTube ID'].tolist()

    # Check if any handles have been scraped
    if exists('data/youtube_id_data.csv'):
        # If they have, make a list of the handles that have been scraped so far
        scraped = pandas.read_csv('data/youtube_id_data.csv')['channel_id'].tolist()
    else:
        # If not, create the csv file with the appropriate header
        with open("data/youtube_id_data.csv", "a+") as file:
            # Create the header row for the .csv file
            header = 'channel_id,join_date\n'
            file.write(header)
        file.close()
        scraped = []

    for channel in channel_ids:
        # Check to see if this is a missing value in the data source. skip if it is.
        if pandas.isna(channel):
            continue
        # Check to see if the value has a space, which will make it unusable in a url
        if ' ' in channel:
            continue
        # Check to see if the handle has already been scraped
        if channel in scraped:
            continue

        # After passing these initial checks, we're ready to start working with the handle
        print(channel, end=': ')
        scraped.append(channel)

        # Since we are using the Channel ID instead of its handle, we use /channel/ instead of /user/ or /c/
        url = 'https://www.youtube.com/channel/{}/about'.format(channel)
        # Request the about page for the given user
        page = requests.get(url, headers=headers)

        # If we have an existing account, parse the page
        if page.status_code == 200:
            try:
                join_date = parse(page.text)
            except AttributeError:
                print('parse error.')
                with open("data/youtube_errorlog.csv", "a+") as file:
                    # append handle to 404 log
                    file.write(channel + ',parse error\n')
                file.close()
                continue

        # If there is status code 429, that indicates that Google has detected the bot, so we need to stop
        elif page.status_code == 429:
            raise Exception('Google detected unusual activity')

        # Else if we still don't have an existing account, print and move on
        elif page.status_code == 404:
            print('not found.')
            with open("data/youtube_404log.csv", "a+") as file:
                # append handle to 404 log
                file.write(channel + '\n')
            file.close()
            continue
        # If there's some other non-200 html code, log the handle and move on
        else:
            print('error in request')
            with open("data/youtube_errorlog.csv", "a+") as file:
                # append handle to 404 log
                file.write('{}, html status {}\n'.format(channel, page.status_code))
            file.close()
            continue

        # Print extracted date to system
        print(join_date)

        # Log data
        with open("data/youtube_id_data.csv", "a+") as file:
            # format results for the .csv file and then append the row
            cols = ['"'+channel+'"',
                    '"'+join_date+'"']
            row = ','.join(cols) + '\n'
            file.write(row)
        file.close()

        # Wait briefly to avoid overloading the server and getting blocked
        time.sleep(0.2)


if __name__ == '__main__':
    main()