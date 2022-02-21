import requests
import pandas
import re
import yaml
import aiohttp
import asyncio
from termcolor import colored


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
    # urls = ['homedepot.com', '3m.com', 'www.7-eleven.com', 'www.aflac.com', 'https://www.battlenorthgold.com']
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


def review_url(id, url, error='ErrorUnknown', traceback='No traceback'):
    # Read config file and instantiate variables
    with open("review_urls.csv", "a+") as file:
        file.write('\n' + str(id) + ', ' + url + ', ' + error)
        print('traceback: ', traceback)
    file.close()


async def get_page(session, id, url, timeout, headers):
    # Request HTML code from URL
    try:
        print(colored(('Staging request number ' + str(id) + ': '), color='yellow'), url)
        async with session.get(url, headers=headers) as response:

            print('status of ' + str(id) + ': ' + str(response.status))
            page = await response.text()
    # Handle errors
    except asyncio.exceptions.TimeoutError as e:
        print(colored(('Exception in ' + str(id) + ': asyncio.Timeout'), 'red'), ' | Adding URL to review_urls: ', url)
        review_url(id, url, 'asyncio.Timeout', e)
        return
    except aiohttp.InvalidURL as e:
        print(colored(('Exception in ' + str(id) + ': InvalidURL'), 'red'), ' | Adding URL to review_urls: ', url)
        review_url(id, url, 'InvalidURL', e)
        return
    except aiohttp.ClientConnectionError as e:
        print(colored(('Exception in ' + str(id) + ': ConnectionError'), 'red'), ' | Adding URL to review_urls: ', url)
        review_url(id, url, 'ConnectionError', e)
        return
    except aiohttp.TooManyRedirects as e:
        print(colored(('Exception in ' + str(id) + ': TooManyRedirects'), 'red'), ' | Adding URL to review_urls: ', url)
        review_url(id, url, 'TooManyRedirects', e)
        return
    except aiohttp.ClientPayloadError as e:
        print(colored(('Exception in ' + str(id) + ': ClientPayloadError'), 'red'), ' | Adding URL to review_urls: ', url)
        review_url(id, url, 'ClientPayloadError', e)
        return
    except aiohttp.ClientError as e:
        print(colored(('Exception in ' + str(id) + ': ClientError'), 'red'), ' | Adding URL to review_urls: ', url)
        review_url(id, url, 'ClientError', e)
        return
    except BaseException as e:
        # Most common exception will be due to a timeout
        # Other errors are possible, ie: URL is invalid or there is no trusted certificate
        print(colored(('Exception in ' + str(id) + ': ErrorUnknown'), 'red'), ' | Adding URL to review_urls: ', url)
        review_url(id, url, traceback=e)
        return
    # If no errors, return page
    return page


def parse_socials(id, url, page):
    # Use a Regular Expression pattern to search for all href links
    pattern = re.compile(r'href=(\"[^\"]*|\'[\']*)')
    matches = pattern.findall(page)

    # For each match, check if it looks like a social media account url and add to list if it is
    # Strip leading " or ' from links before adding to list
    socials = [m.strip('\'\"') for m in matches if is_social_account(m)]

    # Insert socials list into set to remove duplicates, then convert back to list
    socials = list(set(socials))

    # If no socials found, add to review_urls.csv
    if not socials:
        review_url(id, url, error='NoSocialsFound', traceback='No social account links found.')
    print(socials)
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


async def fetch(session, id, url, timeout, headers):
    # Run get_page() to get the HTML page for the specified URL
    page = await get_page(session, id, url, timeout=timeout, headers=headers)
    if not page:
        return  # if there was an error preventing the HTML code from being retrieved, skip to next URL
    print(colored(('Received HTML from number ' + str(id) + ': '), color='green'), url)
    # Run parse_socials() to get all social account links found in the HTML code
    socials = parse_socials(id, url, page)

    # Log socials to socials_log
    if socials:
        log_socials(url, socials)


async def main():
    # Run read_urls() function to get list of URLs
    urls = read_urls()

    # Get user_agent and timeout from config file
    config = read_config()
    user_agent = config['user_agent']
    print('user_agent: ', user_agent)
    timeout = config['timeout']
    headers = {'user-agent': user_agent}
    tasks = []

    # limit connection pool to 50 (100 by default) to lessen resource needs
    # enable_cleanup_closed=True to fix any ssl leaking caused by poor server behavior
    conn = aiohttp.TCPConnector(limit=50, enable_cleanup_closed=True)

    # session versus request-specific timeouts are incredibly confusing in aiohttp
    # by default, request-specific timeouts count the time waiting for connection pool to open up
    # this ClientTimeout object should resolve this by specifying None for total timeout
    timeout_seconds = 10
    timeout = aiohttp.ClientTimeout(total=None, sock_connect=timeout_seconds, sock_read=timeout_seconds)
    async with aiohttp.ClientSession(headers=headers, connector=conn) as session:
        # Iterate through list of URLs, scraping the HTML code for each and parsing out social media links
        for i in range(len(urls)):
            tasks.append(fetch(session, i, urls[i], timeout=timeout, headers=headers))

        # Asynchronously run all tasks
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())









