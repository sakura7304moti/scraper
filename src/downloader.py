# Import--------------------------------------------------
import time
import os
import urllib
import datetime

# import timeout_decorator as td
import shutil
import pandas as pd
from tqdm import tqdm
from src import const
import sys
import ast

# Option--------------------------------------------------
output = const.Output()


# Sub Funtion--------------------------------------------------
# URLを指定して画像を保存する
def download(url, save_path):
    try:
        if not os.path.exists(save_path):
            try:
                response = urllib.request.urlopen(url, timeout=10)
            except Exception as e:
                print(e)
                pass
            else:
                if response.status == 200:
                    try:
                        with open(save_path, "wb") as f:
                            f.write(response.read())
                            time.sleep(0.5)
                    except Exception as e:
                        print(e)
                        pass
    except Exception as e:
        print(e)
        pass
    finally:
        if os.path.exists(save_path):
            if os.path.getsize(save_path) == 0:
                os.remove(save_path)


# ALLでの画像保存先を取得
def get_save_path_all(url, mode, query):
    file_name = url.split("/")[-1].split("?")[0] + ".jpg"
    if mode == "base":
        save_path = os.path.join(output.base_image(query), "All", file_name)
    if mode == "holo":
        save_path = os.path.join(output.holo_image(query), "All", file_name)
    if mode == "user":
        save_path = os.path.join(output.user_image(query), "All", file_name)
    folder = os.path.dirname(save_path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    return save_path


# 日付で画像を保存する
def save_date_image(date, image_path, mode, query):
    year = str(date.year)
    month = str(date.month).zfill(2)

    now_week = pd.to_datetime(date).week
    #first_date = date.replace(day=1)
    first_date = datetime.datetime(date.year,date.month,1)
    start_week = pd.to_datetime(first_date).week
    if date.month == 1:
        start_week = 1

    week_num = now_week - start_week + 1
    if week_num < 0:
        week_num = 0
    week_str = str(week_num).zfill(2)
    date_dir = year + month + week_str

    file_name = os.path.basename(image_path)
    if mode == "base":
        save_path = os.path.join(output.base_image(query), "Date", date_dir, file_name)
    if mode == "holo":
        save_path = os.path.join(output.holo_image(query), "Date", date_dir, file_name)
    if mode == "user":
        save_path = os.path.join(output.user_image(query), "Date", date_dir, file_name)

    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    if not os.path.exists(save_path):
        shutil.copyfile(image_path, save_path)


# 高評価別の画像の保存先を取得
def get_good_save_path(good, image_path, mode, query):
    file_name = os.path.basename(image_path)
    if mode == "base":
        # set save path
        if good >= 10000:
            save_path = os.path.join(
                output.base_image(query), "Good", "10000_More", file_name
            )
        if 10000 > good and good >= 5000:
            save_path = os.path.join(
                output.base_image(query), "Good", "05000_More", file_name
            )
        if 5000 > good and good >= 1000:
            save_path = os.path.join(
                output.base_image(query), "Good", "01000_More", file_name
            )
        if 1000 > good:
            save_path = os.path.join(
                output.base_image(query), "Good", "01000_Under", file_name
            )

    if mode == "holo":
        # set save path
        if good >= 10000:
            save_path = os.path.join(
                output.holo_image(query), "Good", "10000_More", file_name
            )
        if 10000 > good and good >= 5000:
            save_path = os.path.join(
                output.holo_image(query), "Good", "05000_More", file_name
            )
        if 5000 > good and good >= 1000:
            save_path = os.path.join(
                output.holo_image(query), "Good", "01000_More", file_name
            )
        if 1000 > good:
            save_path = os.path.join(
                output.holo_image(query), "Good", "01000_Under", file_name
            )

    if mode == "user":
        # set save path
        if good >= 10000:
            save_path = os.path.join(
                output.user_image(query), "Good", "10000_More", file_name
            )
        if 10000 > good and good >= 5000:
            save_path = os.path.join(
                output.user_image(query), "Good", "05000_More", file_name
            )
        if 5000 > good and good >= 1000:
            save_path = os.path.join(
                output.user_image(query), "Good", "01000_More", file_name
            )
        if 1000 > good:
            save_path = os.path.join(
                output.user_image(query), "Good", "01000_Under", file_name
            )
    return save_path


# 高評価で画像を保存する
def save_good_image(good, image_path, mode, query):
    # get save path
    save_path = get_good_save_path(good, image_path, mode, query)
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))

    # すでにほかの場所にあるか調べる
    before_image_path = ""
    for g in [10010, 5010, 1010, 100]:
        test_save_path = get_good_save_path(g, image_path, mode, query)
        if os.path.exists(test_save_path):
            before_image_path = test_save_path

    # ローカルにないならそのままsave_pathへコピー
    if before_image_path == "":
        shutil.copyfile(image_path, save_path)

    # ローカルにあってsave_pathと異なるなら新しいほうに置き換え
    if before_image_path != "" and before_image_path != save_path:
        os.remove(before_image_path)
        shutil.copyfile(image_path, save_path)


# Main Function--------------------------------------------------
def image_download(csv_path):
    file_name = os.path.basename(csv_path)
    query = file_name.replace("#", "")
    query = query.replace("_" + (query.split("_")[-1]), "")
    mode = os.path.basename(os.path.dirname(os.path.dirname(csv_path)))
    print(f"query : {query}")
    print(f"mode : {mode}")

    tweet_df = pd.read_csv(csv_path, index_col=None)
    tweet_df["images"] = [
        ast.literal_eval(d) for d in tweet_df["images"]
    ]  # images str -> list[str]

    tweet_df["date"] = pd.to_datetime(tweet_df["date"])  # date列をdatetime型に変換
    saved = 0
    for index, row in tqdm(
        tweet_df.iterrows(), total=len(tweet_df), desc="image DL"
    ):  # 画像のダウンロード&保存処理
        images = row["images"]
        for url in images:
            save_path = get_save_path_all(url, mode, query)
            if not os.path.exists(save_path):
                try:
                    download(url, save_path)
                except Exception as e:
                    print(e)
                    pass

            # ALLにダウンロードできた場合
            if os.path.exists(save_path):
                saved = saved + 1
                date = row["date"]
                save_date_image(date, save_path, mode, query)  # YYYYMMWWで画像を保存する
                good = row["likeCount"]
                save_good_image(good, save_path, mode, query)  # 高評価別で画像を保存する
