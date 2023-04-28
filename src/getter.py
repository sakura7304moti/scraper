from . import downloader
from . import scraper
from . import const

output = const.Output()
holoList = const.holoList()

from tqdm import tqdm


def base_main(hashtag: str, since: str):
    csv_path = output.base_database(hashtag)
    scraper.base_scraper(hashtag, since)
    downloader.image_download(csv_path)


def holo_main(since: str):
    scraper.holo_scraper(since)
    for hashtag in tqdm(holoList, desc="hashtag"):
        csv_path = output.holo_database(hashtag)
        downloader.image_download(csv_path)


def user_main(userName: str, since: str):
    csv_path = output.user_database(userName)
    scraper.user_scraper(userName, since)
    downloader.image_download(csv_path)
