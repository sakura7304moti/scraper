import csv
import os
import datetime
import argparse
from time import sleep
import random
import pandas as pd

from .utils import init_driver, search_page, keep_scroling


def scrape(since, hashtag, save_path, headless=True, interval=5, limit=float("inf")):
    header = ["url", "date", "images", "userId", "userName", "likeCount"]
    data = []
    tweet_ids = set()
    write_mode = "w"
    refresh = 0

    until = datetime.date.today().strftime("%Y-%m-%d")
    until_local = datetime.datetime.strptime(since, "%Y-%m-%d") + datetime.timedelta(
        days=interval
    )

    if os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    driver = init_driver(headless)
    with open(save_path, write_mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_mode == "w":
            # write the csv header
            writer.writerow(header)
        while until_local <= datetime.datetime.strptime(until, "%Y-%m-%d"):
            scroll = 0
            if type(until_local) != str:
                until_local = datetime.datetime.strftime(until_local, "%Y-%m-%d")
            path = search_page(driver, since, hashtag)

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

    return data
