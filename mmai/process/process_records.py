import pandas as pd

from mmai.scrape.scrape_fighters import get_fighter_links
from mmai.scrape.scrape_records import get_record_from_link



def raw_fighter_record_to_clean_record(record_df):
    """
    Processes raw fighter records to clean records.
    """
    pass




if __name__ == "__main__":
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    links = get_fighter_links()
    link = links[22]
    df = get_record_from_link(link)
    print(df)