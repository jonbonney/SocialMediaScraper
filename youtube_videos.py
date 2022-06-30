from undetected_chromedriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.common import exceptions
import pandas
import time
import math
from pprint import pprint
from os.path import exists


def time_elapsed(time_start):
    # Display time elapsed
    elapsed = round(time.perf_counter() - time_start)
    print('Time Elapsed: ' + str(math.floor(elapsed/60)) + ':' + str(elapsed % 60).zfill(2))


def main():
    # Start timer to track how long the program has been running
    time_start = time.perf_counter()

    # Set up selenium driver to load JavaScript elements
    print('Setting up ChromeDriver...')
    options = ChromeOptions()
    options.headless = False
    driver = Chrome(options=options)
    driver.implicitly_wait(5)

    # Import youtube channels and users
    excel_path = 'data/socials2.xlsx'
    print('Importing data...')
    channel_ids = pandas.read_excel(excel_path, usecols=['YouTube ID'])['YouTube ID'].tolist()
    # channel_ids = ['UCj1ysTRFos6wX3D8Z3ECviw', 'UCgxVI90_eCbXCXmDgvYyKaw']

    # Check if any handles have been scraped
    if exists('data/youtube_video_data.csv'):
        # If they have, make a list of the handles that have been scraped so far
        scraped = pandas.read_csv('data/youtube_video_data.csv')['video_url'].tolist()
    else:
        # If not, create the csv file with the appropriate header
        with open("data/youtube_id_data.csv", "a+") as file:
            # Create the header row for the .csv file
            header = 'channel_id,video_url,post_date\n'
            file.write(header)
        file.close()
        scraped = []

    for channel in channel_ids:
        # Check to see if this is a missing value in the data source. skip if it is.
        if pandas.isna(channel):
            continue
        print('Fetching channel: ' + channel)
        # Format the Channel ID into the url for videos, sorted by date ascending
        url = 'https://www.youtube.com/channel/{}/videos?view=0&sort=da'.format(channel)
        # Request the about page for the given user
        driver.get(url)
        # Implicitly wait for page to load by looking for the video element
        try:
            driver.find_element(By.TAG_NAME, 'ytd-grid-video-renderer')
        except exceptions.NoSuchElementException:
            print('This YouTube Channel has no videos')
        # Find all elements with a link
        elements_with_links = driver.find_elements(by=By.XPATH, value="//a[@href]")
        videos = []
        for elem in elements_with_links:
            link = elem.get_attribute("href")
            # If it is a link to a video and has not already been found, append to list
            if 'watch?v=' in link and link not in videos:
                videos.append(link)
        print('The oldest videos on this channel are:')
        pprint(videos)

        time_elapsed(time_start)

        # n = number of videos we want to collect a date for on each channel
        n = 5
        if len(videos) < n:
            n = len(videos)
        video_dates = {}
        for i, video in enumerate(videos[0:n]):
            # Check to see if the video has already been scraped. If it has, skip it
            if video in scraped:
                continue
            # Wait to avoid straining servers and getting blocked
            time.sleep(3)
            # Request the webpage
            driver.get(video)
            # Find the info text
            info = driver.find_element(
                by=By.CSS_SELECTOR,
                value="div[id='info'][class='style-scope ytd-video-primary-info-renderer']")
            # Within the info text, find the post date
            post_date = info.find_element(
                by=By.CSS_SELECTOR,
                value="yt-formatted-string[class='style-scope ytd-video-primary-info-renderer']")
            print('Video {}: {}'.format(i+1, post_date.text))
            if post_date.text == '':
                time.sleep(1000)
                raise Exception('Empty date')
            # Save the post date to the dictionary
            video_dates[video] = post_date.text
            time_elapsed(time_start)

        pprint(video_dates)

        # Log data
        rows = []
        for video in video_dates.keys():
            cols = ['"'+channel+'"',
                    '"'+video+'"',
                    '"'+video_dates[video]+'"']
            row = ','.join(cols) + '\n'
            rows.append(row)
        with open("data/youtube_video_data.csv", "a+") as file:
            for row in rows:
                file.write(row)
        file.close()


if __name__ == '__main__':
    main()
