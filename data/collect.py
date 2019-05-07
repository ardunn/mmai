
from bs4 import BeautifulSoup
FIGHTER_M_SRC = "https://en.wikipedia.org/wiki/List_of_male_mixed_martial_artists"

import requests
r = requests.get(FIGHTER_M_SRC)


fighter_hmtl = r.content

print("##################")
print(r.headers)
print(r.status_code)

soup = BeautifulSoup(fighter_hmtl)


print(soup.prettify())



