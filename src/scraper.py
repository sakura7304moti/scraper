from . import const
from . import motitter
import os
from tqdm import tqdm
import pandas as pd
import datetime

output = const.Output()


def base_scraper(hashtag: str, since: str):
    save_path = output.base_database(hashtag)
    diffs = get_diff_date(save_path, since)
    for dates in diffs:
        since = dates[0]
        until = dates[1]
        print("since ", since)
        print("until", until)
        motitter.scrape(since, save_path, hashtag=hashtag, until=until)
    df = pd.read_csv(save_path, index_col=None)
    return df


def holo_scraper(since: str):
    holoList = const.holoList
    for hashtag in tqdm(holoList):
        save_path = output.holo_database(hashtag)
        diffs = get_diff_date(save_path, since)
        for dates in diffs:
            since = dates[0]
            until = dates[1]
            print("since ", since)
            print("until", until)
            motitter.scrape(since, save_path, hashtag=hashtag, until=until)


def user_scraper(userName: str, since: str):
    save_path = output.user_database(userName)
    diffs = get_diff_date(save_path, since)
    for dates in diffs:
        since = dates[0]
        until = dates[1]
        print("since ", since)
        print("until", until)
        motitter.scrape(since, save_path, from_account=userName, until=until)
    df = pd.read_csv(save_path, index_col=None)
    return df


# まだ取得していない日付を取得
def get_diff_date(save_path: str, since: str):
    today = datetime.date.today().strftime("%Y-%m-%d")
    if not os.path.exists(save_path):
        return [[since, today]]

    df = pd.read_csv(save_path, index_col=None)
    df["date"] = pd.to_datetime(df["date"])

    # df_since to since
    under_util = df["date"].iloc[-1].strftime("%Y-%m-%d")
    under = [since, under_util]

    # df_util to today
    up_since = df["date"].iloc[0].strftime("%Y-%m-%d")
    up = [up_since, today]
    return [under, up]
