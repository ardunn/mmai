import pprint

import random
import tqdm
import pymongo

from mmai.scrape.scrape_fighters import get_fighter_links
from mmai.scrape.scrape_records import get_fighter_record_and_info_from_relative_link

if __name__ == "__main__":

    mc = pymongo.MongoClient(host="localhost", port=27017)
    db = mc.mmai
    c = db.raw

    links = get_fighter_links()

    # michael bisping = 144
    # fighter_index = 10
    # print(links[fighter_index])
    # links = [links[fighter_index]]
    # links = [links[fighter_index], links[200], links[1900]]

    # links = ["/wiki/Muhammed_Lawal"]

    # links = [random.choice(links) for _ in range(100)]


    good = []
    bad = []
    ugly = []

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
        c.insert_one(fighter_data)

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

