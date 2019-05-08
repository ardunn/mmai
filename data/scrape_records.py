import requests

from bs4 import BeautifulSoup

from scrape_fighters import get_fighter_links


WIKI_BASE_LINK = "https://en.wikipedia.org"



def get_page_content_by_wiki_relative_link(relative_link, base_link=WIKI_BASE_LINK):
    r = requests.get(base_link + relative_link.get("href"))
    return r

if __name__ == "__main__":
    links = get_fighter_links()

    print(links)

    link = links[0]
    request = get_page_content_by_wiki_relative_link(link)

    soup = BeautifulSoup(request.content, features="html.parser")

    print(soup.prettify())