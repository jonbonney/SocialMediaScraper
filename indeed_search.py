import googleapiclient.errors
from googleapiclient.discovery import build
import pandas
import time
from os.path import exists
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


def check_log():
    # Check if any companies have been queried
    if exists('indeed_log.csv'):
        # If they have, make a list of the company_ids that have been queried so far
        queried = pandas.read_csv('indeed_log.csv')['company_id'].tolist()
    else:
        # If not, create the csv file with the appropriate header
        with open("indeed_log.csv", "a+") as file:
            # Create the header row for the .csv file
            header = 'company_id,company_name,result_num,result_title,result_link\n'
            file.write(header)
        file.close()
        queried = []
    # Insert into set to remove duplicates, then put back into list
    queried = list(set(queried))
    return queried


def main():
    csv_path = 'data/tiktok4:7:2022.csv'
    # Reads the csv file containing company names
    # Only reads the company key and company name columns
    dataframe = pandas.read_csv(csv_path, usecols=[0, 2])
    print(dataframe)

    queried = check_log()
    print(queried)

    for index, row in dataframe.iterrows():
        # initialize the data as a variable
        company_name = row['Company Legal Name']
        company_id = row['Global Company Key']
        # Check to see if the company_id has already been queried
        if company_id in queried:
            print(company_name + ' already queried.')
            continue

        # pause to keep under the 100 requests/minute query limit
        time.sleep(.6)

        # Create search_term for the Google Search
        search_term = company_name + ' reviews site:indeed.com/cmp/'
        # calls the google search method and limits to only the first 5 search results
        try:
            results = google_search(search_term, my_api_key, my_cse_id, num=5)
        except googleapiclient.errors.HttpError as e:
            print(e)
            with open("indeed_errorlog.csv", "a+") as file:
                # append company to error log
                file.write('{},{},HttpError\n'.format(company_name, company_id))
            file.close()
            continue
        # check for None results. if none, log the lack of results, then skip to next row
        if not results:
            print('no results for ' + company_name)
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
        queried.append(company_id)
        for result in results:
            result_num += 1
            with open("indeed_log.csv", "a+") as file:
                # format results for the .csv file and then append the row
                # company_name, title, and link must be surrounded by double quotes because they may contain commas
                cols = [str(company_id),
                        '"'+company_name+'"',
                        str(result_num),
                        '"'+result['title']+'"',
                        '"'+result['link']+'"']
                row = ','.join(cols) + '\n'
                file.write(row)
            file.close()

            # print to console to provide feedback to user during runtime
            print(result['title'], result['link'], sep='\n')


if __name__ == '__main__':
    main()




