import csv
import os
import datetime
import argparse
from time import sleep
import random
import pandas as pd

from .utils import init_driver, search_page, keep_scroling


def scrape(
    since: str,
    save_path: str,
    until: str = None,
    hashtag: str = None,
    from_account: str = None,
    headless=True,
    interval=5,
    limit=float("inf"),
):
    header = ["url", "date", "images", "userId", "userName", "likeCount"]
    data = []
    tweet_ids = set()
    write_mode = "w"
    refresh = 0

    if until == None:
        until = datetime.date.today().strftime("%Y-%m-%d")
    until_local = datetime.datetime.strptime(since, "%Y-%m-%d") + datetime.timedelta(
        days=interval
    )

    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    driver = init_driver(headless)
    before_save_path = save_path
    after_save_path = save_path.replace(".csv", "_after.csv")
    if os.path.exists(save_path):
        save_path = after_save_path
    with open(save_path, write_mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_mode == "w":
            # write the csv header
            writer.writerow(header)
        while until_local <= datetime.datetime.strptime(until, "%Y-%m-%d"):
            scroll = 0
            if type(since) != str:
                since = datetime.datetime.strftime(since, "%Y-%m-%d")
            if type(until_local) != str:
                until_local = datetime.datetime.strftime(until_local, "%Y-%m-%d")
            path = search_page(driver, since, until_local, hashtag, from_account)

            refresh += 1
            last_position = driver.execute_script("return window.pageYOffset;")
            scrolling = True
            print(
                "looking for tweets between "
                + str(since)
                + " and "
                + str(until_local)
                + " ..."
            )
            print(" path : {}".format(path))
            tweet_parsed = 0
            # sleep
            sleep(random.uniform(0.5, 1.5))
            # start scrolling and get tweets
            (
                driver,
                data,
                writer,
                tweet_ids,
                scrolling,
                tweet_parsed,
                scroll,
                last_position,
            ) = keep_scroling(
                driver,
                data,
                writer,
                tweet_ids,
                scrolling,
                tweet_parsed,
                limit,
                scroll,
                last_position,
            )
            # keep updating <start date> and <end date> for every search
            if type(since) == str:
                since = datetime.datetime.strptime(
                    since, "%Y-%m-%d"
                ) + datetime.timedelta(days=interval)
            else:
                since = since + datetime.timedelta(days=interval)
            if type(since) != str:
                until_local = datetime.datetime.strptime(
                    until_local, "%Y-%m-%d"
                ) + datetime.timedelta(days=interval)
            else:
                until_local = until_local + datetime.timedelta(days=interval)
    # breaked with open
    data = pd.DataFrame(data, columns=header)
    driver.close()

    if os.path.exists(after_save_path):
        before_df = pd.read_csv(before_save_path, index_col=None)
        marged = pd.merge(data, before_df, on="url", how="outer")

        # 結合後のデータフレームの列を条件にしてデータを更新する
        marged["date"] = marged["date_y"].fillna(marged["date_x"])
        marged["images"] = marged["images_y"].fillna(marged["images_x"])
        marged["userId"] = marged["userId_y"].fillna(marged["userId_x"])
        marged["userName"] = marged["userName_x"].fillna(marged["userName_y"])
        marged["likeCount"] = marged["likeCount_x"].fillna(marged["likeCount_y"])

        result = marged[header]  # 結合後のデータフレーム
        # date列を日付として認識する
        result["date"] = pd.to_datetime(result["date"])
        # 日付順に降順にソートする
        result = result.sort_values("date", ascending=False)
        result.to_csv(before_save_path)
        os.remove(after_save_path)

    return data
