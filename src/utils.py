from io import StringIO, BytesIO
import os
import re
from time import sleep
import random
import chromedriver_autoinstaller
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import datetime
import pandas as pd
import platform
from selenium.webdriver.common.keys import Keys

# import pathlib
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import urllib

from .const import get_cookie

def parse_number(text):
    text = text.replace(',', '')
    if '万' in text:
        value = float(text[:-1]) * 10000
    else:
        value = float(text)
    value = int(value)
    return value


def get_data(card, save_images=False, save_dir=None):
    """Extract data from tweet card"""
    image_links = []

    try:
        username = card.find_element(by=By.XPATH, value=".//span").text
    except:
        return

    try:
        userId = card.find_element(
            by=By.XPATH, value='.//span[contains(text(), "@")]'
        ).text
    except:
        return

    try:
        postdate = card.find_element(by=By.XPATH, value=".//time").get_attribute(
            "datetime"
        )
    except:
        return

    try:
        like_cnt = card.find_element(
            by=By.XPATH, value='.//div[@data-testid="like"]'
        ).text
        like_cnt = str(like_cnt)
        like_cnt = parse_number(like_cnt)
    except:
        return
    if like_cnt == "":
        return

    try:
        elements = card.find_elements(
            by=By.XPATH,
            value='.//div[2]/div[2]//img[contains(@src, "https://pbs.twimg.com/media")]',
        )
        for element in elements:
            image_link = re.sub(r"&name=.*", "", element.get_attribute("src"))
            if "mini" not in image_link:
                image_links.append(image_link + "&name=orig")
    except:
        image_links = []
    if len(image_links) == 0:
        return

    try:
        promoted = (
            card.find_element(by=By.XPATH, value=".//div[2]/div[2]/[last()]//span").text
            == "Promoted"
        )
    except:
        promoted = False
    if promoted:
        return

    # tweet url
    try:
        element = card.find_element(
            by=By.XPATH, value='.//a[contains(@href, "/status/")]'
        )
        tweet_url = element.get_attribute("href")
    except:
        return

    tweet = (tweet_url, postdate, image_links, userId, username, like_cnt)
    return tweet


def init_driver(headless=True):
    options = ChromeOptions()
    if headless is True:
        print("Scraping on headless mode.")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")  # An error will occur without this line
        options.headless = True
    else:
        options.headless = False
    try:
        driver_path = chromedriver_autoinstaller.install()
        driver = webdriver.Chrome(options=options, executable_path=driver_path)
    except:
        driver = webdriver.Chrome(options=options)
    driver.get("https://twitter.com/home?lang=ja")
    sleep(5)
    cookie = get_cookie()
    for c in cookie:
        driver.add_cookie(c)
    driver.get("https://twitter.com/home?lang=ja")
    driver.set_page_load_timeout(100)
    return driver


def search_page(driver, since, until, hashtag=None, from_account=None):
    from_account = (
        "(from%3A" + from_account + ")%20" if from_account is not None else ""
    )
    hash_tags = "(%23" + hashtag + ")%20" if hashtag is not None else ""
    since = "since%3A" + since + "%20"
    # today = datetime.date.today() + datetime.timedelta(days=1)
    # today_text = today.strftime("%Y-%m-%d")
    until = "until%3A" + until + "%20"
    filter_replies = "%20-filter%3Areplies"
    minlikes = "%20min_faves%3A5"
    path = f"https://twitter.com/search?q={from_account}{hash_tags}{until}{since}{filter_replies}{minlikes}&src=typed_query&f=live"
    while(True):
        try:
            driver.get(path)
        except:
            pass
        else:
            break
    return path


def keep_scroling(
    driver,
    data,
    writer,
    tweet_ids,
    scrolling,
    tweet_parsed,
    limit,
    scroll,
    last_position,
    save_images=False,
):
    """scrolling function for tweets crawling"""

    save_images_dir = "/images"

    if save_images == True:
        if not os.path.exists(save_images_dir):
            os.mkdir(save_images_dir)

    while scrolling and tweet_parsed < limit:
        sleep(random.uniform(0.5, 1.5))
        # get the card of tweets
        page_cards = driver.find_elements(
            by=By.XPATH, value='//article[@data-testid="tweet"]'
        )  # changed div by article
        for card in page_cards:
            tweet = get_data(card, save_images, save_images_dir)
            if tweet:
                # check if the tweet is unique
                tweet_id = "".join(tweet[0:1])
                if tweet_id not in tweet_ids:
                    tweet_ids.add(tweet_id)
                    data.append(tweet)
                    last_date = str(tweet[1])
                    # print("Tweet made at: " + str(last_date) + " is found.")
                    writer.writerow(tweet)
                    tweet_parsed += 1
                    if tweet_parsed >= limit:
                        break
        scroll_attempt = 0
        while tweet_parsed < limit:
            # check scroll position
            scroll += 1
            # print("scroll ", scroll)
            sleep(random.uniform(0.5, 1.5))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            curr_position = driver.execute_script("return window.pageYOffset;")
            if last_position == curr_position:
                scroll_attempt += 1
                # end of scroll region
                if scroll_attempt >= 2:
                    scrolling = False
                    break
                else:
                    sleep(random.uniform(0.5, 1.5))  # attempt another scroll
            else:
                last_position = curr_position
                break
    return (
        driver,
        data,
        writer,
        tweet_ids,
        scrolling,
        tweet_parsed,
        scroll,
        last_position,
    )
