import requests
from webpage import read_config
import time
import re
import math
import pandas


def is_claimed(html):
    claim_widget_css = '<div class="css-7avtx3 eu4oa1w0">'  # css id used for the "claimed-profile-section-widget"
    claimed_css = '<button class="css-1ffk1q e8ju0x51">'  # css id used for the "Claimed Profile" button

    # Check if the claimed profile widget css is present in the page
    if claim_widget_css not in html:
        # If this error is raised, it is likely that indeed has changed their css or the URL is not correct
        raise Exception('Claim error. "claimed-profile-section-widget" css not found in page.')

    # Check if the 'Claimed Profile' css is present in the page
    if claimed_css in html:
        print('Profile is claimed.')
        return True
    print('Profile is NOT claimed.')
    return False


def is_reviews(url):
    p = r'indeed\.com/cmp/[^/]+/reviews'
    if re.search(p, url, re.IGNORECASE):
        return True
    return False


def reformat(url):
    p = r'indeed\.com/cmp/(?P<company>[^/]+)/reviews'
    company = re.search(p, url, re.IGNORECASE).group('company')
    url = 'https://www.indeed.com/cmp/' + company + '/reviews/?fcountry=ALL&sort=date_asc'
    return url, company


def first_review_date(html):
    # first need to check if there is a featured review and remove it, since it will not be relevant
    p = r'cmp-FeaturedReviewHeader-highlighted'
    if re.search(p, html, re.IGNORECASE):
        print('featured review present. splitting...')
        html = html.split(p)[1]
    # look for first (relevant) review
    p = r'(?P<review><span itemProp=\"author\".+?</span>)'
    first_review = re.search(p, html, re.DOTALL).group('review')
    # extract date of the review
    p = r'.*>(?P<date>[^"]*)<'
    date = re.search(p, first_review, re.DOTALL).group('date')
    print(date)
    return date


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
    csv_path = 'indeed_log.csv'
    dataframe = pandas.read_csv(csv_path)
    urls = ['https://www.indeed.com/cmp/Bnsf-Railway/reviews',
            'https://www.indeed.com/cmp/Bank-of-America/reviews',
            'https://www.indeed.com/cmp/Popular,-Inc./reviews?fcountry=ALL&ftopic=mgmt&start=80',
            'https://www.indeed.com/cmp/Aramark/reviews',
            'https://www.indeed.com/cmp/Amgen/reviews?fcountry=US&floc=Fort+Lauderdale%2C+FL']
    scraped = []

    for index, row in dataframe.iterrows():
        company_id = row[0]
        company_name = row[1]
        result_number = row[2]
        print(company_id, company_name, result_number, sep=' | ')
        url = row[4]
        print(url)

        # Confirm URL is for an indeed review page
        if not is_reviews(url):
            continue
        # Reformat the URL to include search query fcountry=ALL and sort=date_asc and extract indeed_id from URL
        url, indeed_id = reformat(url)
        print(url)
        # If, after reformatting, it is the same URL as one already scraped, we will skip this row
        if url in scraped:
            print('URL already scraped. Skipping row...')
            continue

        # # # Request webpage # # #
        time.sleep(1)  # pause before each page request to ensure we don't overload indeed servers
        page = requests.get(url, headers=headers)

        # Append the URL to the list of URLs that have been webscraped
        scraped.append(url)

        # # # Parse webpage # # #
        # check if profile is claimed by the company
        claimed = is_claimed(page.text)

        # check date of first review
        date = first_review_date(page.text)

        # # # Log data # # #
        with open("indeed_data.csv", "a+") as file:
            # format results for the .csv file and then append the row
            cols = [str(company_id),
                    '"'+company_name+'"',
                    '"'+indeed_id+'"',
                    str(claimed),
                    '"'+date+'"']
            row = ','.join(cols) + '\n'
            file.write(row)
        file.close()

        # Display time elapsed
        time_elapsed = round(time.perf_counter() - time_start)
        print('Time Elapsed: ' + str(math.floor(time_elapsed/60)) + ':' + str(time_elapsed % 60).zfill(2))

        print('')


if __name__ == '__main__':
    main()
