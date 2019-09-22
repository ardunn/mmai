import pandas as pd

from mmai.data.scrape_fighters import get_fighter_links
from mmai.data.scrape_records import link_to_raw_fighter_record



def raw_fighter_record_to_clean_record(record_df):
    """
    Processes raw fighter records to clean records.
    """
    pass




if __name__ == "__main__":
    links = get_fighter_links()
    link = links[22]
    df = link_to_raw_fighter_record(link)
    print(df)