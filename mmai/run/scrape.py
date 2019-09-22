import tqdm

from mmai.scrape.scrape_fighters import get_fighter_links
from mmai.scrape.scrape_records import get_fighter_record_and_info_from_relative_link



if __name__ == "__main__":
    links = get_fighter_links()
    fighter_links = [links[261]]
    for link in tqdm.tqdm(fighter_links):
        record = get_fighter_record_and_info_from_relative_link(link)
