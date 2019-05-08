import requests
from bs4 import BeautifulSoup

FIGHTER_M_SRC = "https://en.wikipedia.org/wiki/List_of_male_mixed_martial_artists"


def is_fighter(link):
    """
    Determine whether a link from a wikipedia table represents a fighter or is just garbage.

    Args:
        link: A BeautifulSoup result object (or link that can be converted to string).

    Returns:
        (bool): True, if link appears to be fighter. Else, garbage.
    """
    candidate = str(link).lower()

    excluded_terms = ["flag_", "championship", "king of the cage", " mma", "pancrase", "k-1", "shooto", "cite_note",
                      "cite_ref", "fighting", "affliction entertainment", "super fight league", "cage warriors",
                      "strikeforce", "world series", "list of", "kotc", "association", "elitexc", "m-1", "shoxc",
                      "category", "content", "discussion", "fights", "article", "wikipedia", "wikimedia", "logo",
                      "accesskey", "developers", "mixed martial arts", "Sengoku", "international fight league",
                      "list_of", "current_events", "help:section", "ksw"
                      ]
    if any([term in candidate for term in excluded_terms]):
        return False

    required_terms = ["/wiki/"]

    if not all([term in candidate for term in required_terms]):
        return False

    return True


def get_fighter_links(src=FIGHTER_M_SRC, return_garbage=False):
    """
    Get a list of fighters as links to their individual wikipedia pages.
    Args:
        src (str): A string url representing a table of mma fighters on wikipedia with links.
        return_garbage (bool): If True, returns the links determined as garbage.

    Returns:
        a list of links: either fighters as determined by screning or a list of garbage links

    """

    r = requests.get(src)
    fighter_hmtl = r.content
    soup = BeautifulSoup(fighter_hmtl, features="html.parser")
    fighters = []
    garbage = []
    for link in soup.find_all('a'):
        if is_fighter(link):
            fighters.append(link)
        else:
            garbage.append(link)

    if return_garbage:
        return garbage
    else:
        return fighters
