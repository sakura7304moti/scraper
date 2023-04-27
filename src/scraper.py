from . import const
from . import motitter
import os
from tqdm import tqdm

output = const.Output()


def base_scraper(hashtag: str, since: str):
    save_path = output.base_database(hashtag)
    df = motitter.scrape(since, save_path, hashtag=hashtag)
    return df


def holo_scraper(since: str):
    holoList = const.holoList
    for hashtag in tqdm(holoList):
        save_path = output.holo_database(hashtag)
        motitter.scrape(since, save_path, hashtag=hashtag)


def user_scraper(userName: str, since: str):
    save_path = output.user_database(userName)
    df = motitter.scrape(since, save_path, from_account=userName)
    return df
