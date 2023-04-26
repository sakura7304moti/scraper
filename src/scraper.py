from . import const
from . import motitter
import os

output = const.Output()


def base_scraper(hashtag: str, since: str):
    save_path = output.base_database(hashtag)
    df = motitter.scrape(since, save_path, hashtag)
    return df
