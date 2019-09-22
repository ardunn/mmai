import tqdm

from mmai.scrape.scrape_fighters import get_fighter_links
from mmai.scrape.scrape_records import get_record_from_link



if __name__ == "__main__":
    fighter_links = get_fighter_links()
    for link in tqdm.tqdm(fighter_links):
        record = get_record_from_link(link)
