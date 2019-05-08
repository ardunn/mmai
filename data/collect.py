
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
# print(soup.find_all('a'))


def is_fighter(link):
    candidate = str(link).lower()

    excluded_terms = ["flag_", "championship", "king of the cage", " mma", "pancrase", "k-1", "shooto", "cite_note",
                      "cite_ref", "fighting",  "affliction entertainment", "super fight league", "cage warriors",
                      "strikeforce", "world series", "list of", "kotc", "association", "elitexc", "m-1", "shoxc"
                      "category", "content", "discussion", "fights", "article", "wikipedia", "wikimedia",
                      ]
    if any([term in candidate for term in excluded_terms]):
        return False

    required_terms = ["/wiki/"]

    if not all([term in candidate for term in required_terms]):
        return False

    return True



fighters = []
garbage = []
for link in soup.find_all('a'):
    if is_fighter(link):
        fighters.append(link)
    else:
        garbage.append(link)



# for g in garbage:
#     print(g)

for f in fighters:
    print(f)