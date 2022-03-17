import aiohttp
import asyncio
from webpage import read_config
import pandas
import time


async def is_tiktok(handle, session, timeout=aiohttp.ClientTimeout(total=None, sock_read=10, sock_connect=10)):
    url = 'https://www.tiktok.com/@' + handle
    try:
        async with session.get(url, timeout=timeout) as response:
            page = await response.text()
    except Exception as e:
        print(e)
        return handle, 'Error'
    no_account = '<title data-rh="true">Couldn&#x27;t find this account.'
    captcha = 'unusual network activity'
    if captcha in page:
        raise Exception
    if no_account in page:
        return handle, False
    return handle, True


async def is_tiktoks(handles, session):
    tasks = []
    print(handles)
    for handle in handles:
        tasks.append(is_tiktok(handle, session))
    results = await asyncio.gather(*tasks)
    exist = {}
    print(results)
    for i in results:
        exist[i[0]] = i[1]
    return exist


async def main():
    # Get config file properties
    config = read_config()
    user_agent = config['user_agent']
    print('user_agent: ', user_agent)
    timeout = config['timeout']
    conn_limit = config['conn_limit']

    headers = {'user-agent': user_agent}
    conn = aiohttp.TCPConnector(limit=conn_limit, enable_cleanup_closed=True, force_close=True)

    handles_df = pandas.read_csv('socials_log.csv')
    handles_test = ['tiktok', 'apple', 'akdjflakjf', 'jonbonney', 'billybobjoe']


    jar = aiohttp.DummyCookieJar()
    async with aiohttp.ClientSession(headers=headers, connector=conn, cookie_jar=jar) as session:
        for index, row in handles_df.iterrows():
            handles = set()
            for i in row[1:]:
                if not pandas.isna(i):
                    handles.add(i)
            tiktoks = await is_tiktoks(handles, session)

            for i in tiktoks:
                if tiktoks[i]:
                    print('tiktok found:', i)


if __name__ == '__main__':
    asyncio.run(main())
