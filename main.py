import requests
import pandas
import re
import yaml


def is_social_account(url):
    # List of the major social media platforms
    platforms = ['youtube.com/user/',
                 'youtube.com/channel/',
                 'facebook.com/',
                 'instagram.com/',
                 'linkedin.com/company/',
                 'tiktok.com/',
                 'pinterest.com/']
    # Check if URL could be an account of any of the major social media platforms
    for i in platforms:
        if re.search(i, url, re.IGNORECASE):
            return True
    # Check if the URL is a Twitter URL (separately because it requires additional condition)
    # /i/ indicates a tweet and /hashtag/ indicates a hashtag, so we can eliminate twitter URLs that include those
    twitter = re.search('twitter.com/', url, re.IGNORECASE)
    tweet_or_hashtag = re.search('/i/|/hashtag/', url, re.IGNORECASE)
    if twitter and not tweet_or_hashtag:
        return True
    # If the URL has not met any of the conditions, it looks like it isn't a social account, so return False
    return False


def read_urls():
    # Read config file and instantiate variables
    config = read_config()
    data_path = config['data_path']
    url_col = config['url_col']
    # Read Web URL column of data set as list
    raw_urls = pandas.read_excel(data_path)[url_col].to_list()
    # Remove all NaN (Not a Number) from list which arose from missing values in data set
    urls = [i for i in raw_urls if not pandas.isna(i)]
    print('Removed', len(raw_urls) - len(urls), 'empty URL elements from list.', sep=' ')
    print(urls)
    # Clean up beginning of URL to ensure that they all use secure https schema
    for i in range(len(urls)):
        clean_url = 'https://www.' + urls[i].replace('https://', '').replace('http://', '').replace('www.', '')
        urls[i] = clean_url
    # Insert urls list into set to remove duplicates, then convert back to list
    urls = list(set(urls))
    # Sort URls
    urls.sort(key=str.lower)
    return urls


def review_url(url, error='ErrorUnknown', traceback='No traceback'):
    # Read config file and instantiate variables
    with open("review_urls.csv", "a+") as file:
        file.write('\n' + url + ', ' + error)
        print(traceback)
    file.close()


def get_page(url, timeout, user_agent):
    # Set user agent
    headers = {'user-agent': user_agent}
    # Request HTML code from URL
    try:
        page = requests.get(url, timeout=timeout, headers=headers)
    # Handle errors
    except requests.exceptions.Timeout as e:
        print('Exception: Timeout | Adding to review_urls.')
        review_url(url, 'Timeout', e)
        return
    except requests.exceptions.ConnectionError as e:
        print('Exception: ConnectionError | Adding to review_urls.')
        review_url(url, 'ConnectionError', e)
        return
    except requests.exceptions.TooManyRedirects as e:
        print('Exception: TooManyRedirects | Adding to review_urls.')
        review_url(url, 'TooManyRedirects', e)
        return
    except BaseException as e:
        # Most common exception will be due to a timeout
        # Other errors are possible, ie: URL is invalid or there is no trusted certificate
        print('Error in HTML request. Adding to review_urls.')
        review_url(url, traceback=e)
        return
    # If no errors, return page
    return page


def parse_socials(page):
    # Use a Regular Expression pattern to search for all href links
    pattern = re.compile(r'href=(\"[^\"]*|\'[\']*)')
    matches = pattern.findall(page.text)

    # For each match, check if it looks like a social media account url and add to list if it is
    # Strip leading " or ' from links before adding to list
    socials = [m.strip('\'\"') for m in matches if is_social_account(m)]

    # Insert socials list into set to remove duplicates, then convert back to list
    socials = list(set(socials))

    # If no socials found, add to review_urls.csv
    if not socials:
        review_url(page.url, error='NoSocialsFound', traceback='No social account links found.')

    return socials


def log_socials(url, socials):
    # Log socials to socials_log.csv
    with open("socials_log.csv", "a+") as file:
        file.write('\n' + url)
        for social in socials:
            file.write(', ' + social)
    file.close()


def read_config():
    # Read and return config file
    with open("config.yml", "r") as file:
        config = yaml.safe_load(file)
    file.close()
    return config


def main():
    # Run read_urls() function to get list of URLs
    urls = read_urls()

    # Get user_agent and timeout from config file
    config = read_config()
    user_agent = config['user_agent']
    timeout = config['timeout']

    # Total URLs and current count for progress output
    total = len(urls)
    count = 0

    # Iterate through list of URLs, scraping the HTML code for each and parsing out social media links
    for url in urls:
        # Display progress through list of URLs
        count += 1
        print('\n', count, '/', total, '|', 'Getting HTML from:', url, sep=' ')

        # Run get_page() to get the HTML page for the specified URL
        page = get_page(url, timeout=timeout, user_agent=user_agent)
        if not page: continue # if there was an error preventing the HTML code from being retrieved, skip to next URL

        # Run parse_socials() to get all social account links found in the HTML code
        socials = parse_socials(page)

        # Log socials to socials_log
        if socials:
            log_socials(url, socials)


if __name__ == '__main__':
    main()









