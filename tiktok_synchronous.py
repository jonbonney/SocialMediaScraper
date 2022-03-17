import requests
import asyncio
from webpage import read_config
import pandas
import time
import math
from termcolor import colored


def is_tiktok(handle, headers):
    url = 'https://www.tiktok.com/@' + handle
    page = requests.get(url, headers=headers)
    print(url, page.status_code)
    if page.status_code == 200:
        if 'DivErrorContainer' in page.text:
            print(colored('tiktok found, but has zero posts. handle:', 'yellow'), handle)
            return False
        if '<body class="captcha-disable-scroll">' in page.text:
            print(colored('captcha', 'red'))
            raise Exception('captcha', 'The server responded with a captcha verification.')
        if '"title":"tiktok-verify-page"' in page.text:
            print(colored('verify-page', 'red'))
            raise Exception('verify-page', 'The server ran a JavaScript verify-page script.')
        return True
    else:
        # print(url, '| Status Code:', page.status_code)
        return False

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
    handles_df = pandas.read_csv('socials_log.csv')

    # Iterate through all rows of the dataframe
    for index, row in handles_df.iterrows():
        handles = set()
        # Iterate through each column after the first column (which is an index)
        for i in row[1:]:
            # Don't include cells with missing values
            if not pandas.isna(i):
                handles.add(i.lower())

        for handle in handles:
            try:
                if is_tiktok(handle, headers):
                    print(colored('tiktok found:', 'green'), handle)
                    with open("review_tiktoks.txt", "a+") as file:
                        url = 'https://www.tiktok.com/@' + handle
                        file.write(url + '\n')
                    file.close()
            except Exception as e:
                print(e)
            # Display time elapsed
            time_elapsed = round(time.perf_counter() - time_start)
            print('Time Elapsed: ' + str(math.floor(time_elapsed/60)) + ':' + str(time_elapsed%60).zfill(2))
            # Wait to avoid overburdening TikTok servers and getting blocked
            time.sleep(3)

if __name__ == '__main__':
    main()
