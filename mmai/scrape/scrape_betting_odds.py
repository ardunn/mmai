import requests
from bs4 import BeautifulSoup


# src = "https://www.bestfightodds.com/events/ufc-236-holloway-vs-poirier-2-1666"
src = "https://www.bestfightodds.com/fighters/Jon-Jones-819"
headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0"}

r = requests.get(src, headers=headers)
odds_html = r.content
soup = BeautifulSoup(odds_html, features="html5lib")

# print(soup.prettify())
cells = soup.find_all(
    'table',
)

print(cells)

# print(table_body)
# rows = table_body.find_all('tr')
#
# for row in rows:
#     print("ROW IS", row)


# print(soup)