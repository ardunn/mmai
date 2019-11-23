import json

import tqdm

from mmai.scrape.scrape_wiki_fighter_list import get_fighter_links
from mmai.scrape.scrape_wiki_fighter_record import get_fighter_record_and_info_from_relative_link


def scrape_wikipedia():

    links = get_fighter_links()

    good = []
    bad = []
    ugly = []

    fighters = []

    for link in tqdm.tqdm(links):
        fighter_data = get_fighter_record_and_info_from_relative_link(link, quiet=True, silent=False)

        w = fighter_data["warning_level"]
        if w == 0:
            good.append(link)
        elif w == 1:
            bad.append(link)
        elif w == 2:
            ugly.append(link)
        else:
            raise ValueError("Warning value not [0-2]!")

        fighter_data["link"] = str(link)
        fighter_data["title"] = link.text

        # pprint.pprint(fighter_data)
        fighters.append(fighter_data)

    n_links = len(links)
    print(f"Links successfully parsed: {len(good)}/{n_links}"
          f"\nLinks having one problem: {len(bad)}/{n_links}"
          f"\nLinks having multiple problems: {len(ugly)}/{n_links}")

    filenames = {"good.txt": good, "bad.txt": bad, "ugly.txt": ugly}
    for k, v in filenames.items():
        with open(k, "w") as f:
            for l in v:
                f.write(l.text)
                f.write("\n")

    with open("data/wiki_fighters_raw.json", "w") as f:
        json.dump(fighters, f)


if __name__ == "__main__":
    scrape_wikipedia()