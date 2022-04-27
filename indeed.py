from googleapiclient.discovery import build
import pandas
import time
# indeed_credentials is a .py file containing a user's secret credentials for the Google Search API
# if it does not exist, you will need to obtain the necessary credentials and create this file
from indeed_credentials import my_api_key, my_cse_id


def google_search(search_term, api_key, cse_id, **kwargs):
    # this method makes the request to the Google Search API
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    if "items" in res.keys():
        return res["items"]
    else:
        return None


def main():
    csv_path = 'tiktok4:7:2022.csv'
    # Reads the csv file containing company names
    # Only reads the company key and company name columns
    dataframe = pandas.read_csv(csv_path, usecols=[0, 2])
    print(dataframe)

    for index, row in dataframe.iterrows():
        # pause to keep under the 10 requests/second query limit
        time.sleep(1/9)

        company_name = row['Company Legal Name']
        company_id = row['Global Company Key']
        search_term = company_name + ' reviews site:indeed.com/cmp/'
        # calls the google search method and limits to only the first 5 search results
        results = google_search(search_term, my_api_key, my_cse_id, num=5)
        # check for None results. if none, log the lack of results, then skip to next row
        if not results:
            with open("indeed_log.csv", "a+") as file:
                # format results for the .csv file and then append the row
                cols = [str(company_id), company_name, '0', '', '']
                row = ','.join(cols) + '\n'
                file.write(row)
            file.close()
            continue
        # begin a count of which result we are on for the current search request
        result_num = 0

        # log search results
        for result in results:
            result_num += 1
            with open("indeed_log.csv", "a+") as file:
                # format results for the .csv file and then append the row
                cols = [str(company_id), company_name, str(result_num), result['title'], result['link']]
                row = ','.join(cols) + '\n'
                file.write(row)
            file.close()

            # print to console to provide feedback to user during runtime
            print(result['title'], result['link'], sep='\n')


if __name__ == '__main__':
    main()




