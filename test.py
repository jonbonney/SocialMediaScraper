import re
import requests
from bs4 import BeautifulSoup

page = requests.get('https://www.blackstone.com')
soup = BeautifulSoup(page.text, 'lxml')
print(page.text)

# Use a Regular Expression pattern to search for social media URLs
pattern = re.compile(r'''(tiktok\.com/
                         |linkedin\.com/company/
                         |pinterest\.com/
                         |facebook\.com/
                         |twitter\.com/
                         |youtube\.com/
                         |instagram\.com/
                         )
                         (?P<handle>[^/\"\']*)'''
                     , re.X)
matches = pattern.findall(page.text)

for m in matches:
    print(m)




