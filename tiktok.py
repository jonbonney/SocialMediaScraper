import aiohttp
import asyncio
from webpage import read_config


async def is_account(handle, session, timeout=aiohttp.ClientTimeout(total=None, sock_read=10, sock_connect=10)):
    url = 'https://www.tiktok.com/@' + handle
    try:
        async with session.get(url, timeout=timeout) as response:
            page = await response.text()
    except Exception as e:
        print(e)
    no_account = '<title data-rh="true">Couldn&#x27;t find this account.'
    if no_account in page:
        return handle, False
    return handle, True


async def check_accounts_exist(handles, session):
    tasks = []
    results = []
    async with session:
        for handle in handles:
            tasks.append(is_account(handle, session))
        results = await asyncio.gather(*tasks)
        print(results)

    exist = {}
    for i in results:
        exist[i[0]] = i[1]
    print(exist)



async def main():
    # Get config file properties
    config = read_config()
    user_agent = config['user_agent']
    print('user_agent: ', user_agent)
    timeout = config['timeout']
    conn_limit = config['conn_limit']

    headers = {'user-agent': user_agent}
    conn = aiohttp.TCPConnector(limit=conn_limit, enable_cleanup_closed=True, force_close=True)

    handles_test = ['tiktok', 'apple', 'akdjflakjf', 'jonbonney', 'billybobjoe']

    jar = aiohttp.DummyCookieJar()
    async with aiohttp.ClientSession(headers=headers, connector=conn, cookie_jar=jar) as session:
        await check_accounts_exist(handles_test, session)


if __name__ == '__main__':
    asyncio.run(main())
