import requests
import pandas
from webpage import read_config
import time
import re


def parse(html):
    # Extract display name, handle, and date from headline
    p = r'<h2>(?P<headline>.*)<\/h2>'
    headline = re.search(p, html, re.DOTALL).group('headline')
    p = r'(?P<display_name>.*) \(@<a'
    display_name = re.search(p, headline).group('display_name')
    p = r'>(?P<handle>.*)<\/a>'
    handle = re.search(p, headline).group('handle')
    p = r'joined Twitter on (?P<date>[^<]*)'
    date = re.search(p, headline).group('date')
    # Extract user id
    p = r'<h3>User id: (?P<user_id>.*)<\/h3>'
    user_id = re.search(p, html).group('user_id')
    user_id = int(user_id.replace(',', ''))
    return {'display_name': display_name, 'handle': handle, 'user_id': user_id, 'join_date': date}


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

    # Import indeed URL data to webscrape
    excel_path = 'data/socials.xlsx'
    # dataframe = pandas.read_excel(excel_path)
    twitter_handles = ['jack', 'hottopic', 'mizzou']

    for handle in twitter_handles:
        url = 'http://www.twitterjoindate.com/search?utf8=✓&name={}&commit=Search'.format(handle)

        # Wait to avoid overloading server and getting blocked
        time.sleep(0.5)
        # Request page from twitterjoindate.com
        page = requests.get(url, headers=headers)
        # Parse the page and extract data
        data_dict = parse(page.text)
        print(data_dict)
        # Check to make sure that twitterjoindate.com is giving us information about the correct user
        if not handle == data_dict['handle']:
            raise Exception('handle mismatch: requested {}, but received {}'.format(handle, data_dict['handle']))

        # Log data
        with open("data/twitter_data.csv", "a+") as file:
            # format results for the .csv file and then append the row
            cols = ['"'+data_dict['display_name']+'"',
                    data_dict['handle'],
                    str(data_dict['user_id']),
                    '"'+data_dict['join_date']+'"']
            row = ','.join(cols) + '\n'
            file.write(row)
        file.close()


if __name__ == '__main__':
    main()
