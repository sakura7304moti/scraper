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
    holoList = const.holoList()
    for hashtag in tqdm(holoList, desc="tag"):
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
        print(f"date {since} -> {until}")
        motitter.scrape(since, save_path, from_account=userName, until=until)
    df = pd.read_csv(save_path, index_col=None)
    return df


# まだ取得していない日付を取得
def get_diff_date(save_path: str, since: str):
    today_date = datetime.date.today()
    if not os.path.exists(save_path):
        today_date = today_date.strftime("%Y-%m-%d")
        return [[since, today_date]]
    else:
        df = pd.read_csv(save_path)
        if len(df) == 0:
            return [[since, today_date]]
        since_date = datetime.datetime.strptime(since, "%Y-%m-%d")
        since_date = since_date.date()
        df["date"] = pd.to_datetime(df["date"])  # date列をdatetime型に変換


        latest_date = df["date"].max().to_pydatetime()
        latest_date = latest_date.date()
        old_date = df["date"].min().to_pydatetime()
        old_date = old_date.date()

        if since_date <= old_date:
            # @->@ |----| @->@|
            under_start_date = since_date
            under_end_date = old_date
            up_start_date = latest_date
            up_end_date = today_date
        else:
            if latest_date <= since_date:
                # |----|  @->@|
                under_start_date = None
                under_end_date = None
                up_start_date = since_date
                up_end_date = today_date
            else:
                # |--@--| @->@|
                under_start_date = None
                under_end_date = None
                up_start_date = latest_date
                up_end_date = today_date
        if under_start_date == None:
            up_start_date = up_start_date.strftime("%Y-%m-%d")
            up_end_date = up_end_date.strftime("%Y-%m-%d")
            return [[up_start_date, up_end_date]]
        else:
            under_start_date = under_start_date.strftime("%Y-%m-%d")
            under_end_date = under_end_date.strftime("%Y-%m-%d")
            up_start_date = up_start_date.strftime("%Y-%m-%d")
            up_end_date = up_end_date.strftime("%Y-%m-%d")
            return [[under_start_date, under_end_date], [up_start_date, up_end_date]]
