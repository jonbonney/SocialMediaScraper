import requests
from webpage import read_config
import time


def is_claimed(html):
    claim_widget_css = '<div class="css-7avtx3 eu4oa1w0">'  # css id used for the "claimed-profile-section-widget"
    claimed_css = '<button class="css-1ffk1q e8ju0x51">'  # css id used for the "Claimed Profile" button

    # Check if the claimed profile widget css is present in the page
    if claim_widget_css not in html:
        # If this error is raised, it is likely that indeed has changed their css or the URL is not correct
        raise Exception('Claim error. "claimed-profile-section-widget" css not found in page.')
    print('claimed-profile-section-widget css found.')

    # Check if the 'Claimed Profile' css is present in the page
    if claimed_css in html:
        print('Profile is claimed.')
        return True
    print('Profile is NOT claimed.')
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

    # Import indeed URLs to webscrape
    url = 'https://www.indeed.com/cmp/Bnsf-Railway/reviews'

    # # # Request webpage # # #
    page = requests.get(url, headers=headers)
    print(url)

    # # # Parse webpage # # #
    claimed = is_claimed(page.text)

    # # # Log data # # #


if __name__ == '__main__':
    main()
