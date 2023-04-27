def get_cookie():
    cookie = [
        {"name": "_ga", "value": "GA1.2.1606686500.1665843538"},
        {"name": "_ga_34PHSZMC42", "value": "GS1.1.1680276654.4.1.1680277116.0.0.0"},
        {"name": "_ga_BYKEBDM7DS", "value": "GS1.1.1682231729.3.0.1682231736.0.0.0"},
        {"name": "_gcl_au", "value": "1.1.815035658.1680276652"},
        {"name": "_gid", "value": "GA1.2.855812465.1682085686"},
        {"name": "auth_token", "value": "d3b80fa59439369f28e36146e5ae4978fb65f0a9"},
        {
            "name": "ct0",
            "value": "78e08e0ea19e7a4c1b35c14b2d737337e4ef5c9cc557ff64aee51ecbe341ba0c6cc82eeab21d8caf41d988ab392f2fa7d2276f8f5909ee4f6eb2691ba29402d51652dfa93be632915477530fa2c885f0",
        },
        {"name": "des_opt_in", "value": "Y"},
        {
            "name": "external_referer",
            "value": "padhuUp37zjgzgv1mFWxJ12Ozwit7owX|0|8e8t2xd8A2w%3D",
        },
        {"name": "guest_id", "value": "v1%3A168213015562035219"},
        {"name": "guest_id_ads", "value": "v1%3A168213015562035219"},
        {"name": "guest_id_marketing", "value": "v1%3A168213015562035219"},
        {"name": "kdt", "value": "OsGwLVRlWxqY7x3WREfZUzFUzv7yXALVN1OANfM8"},
        {
            "name": "mbox",
            "value": "PC#3acb1cda68564596a6ecaf0090b1313b.32_0#1745476508|session#3d7d233d91ad4a6480422ea0c3d9fae5#1682233568",
        },
        {"name": "personalization_id", "value": '"v1_333t+vCpTKTfp9afNmU7bQ=="'},
        {"name": "tweetdeck_version", "value": "beta"},
        {"name": "twid", "value": "u%3D754989150730715137"},
        {"name": "g_state", "value": '{"i_l":0}'},
        {"name": "lang", "value": "ja"},
    ]
    return cookie


import os
import pandas as pd
import yaml

# プロジェクトの相対パス
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# hololive fanart tag list
def holoList():
    holo_path = os.path.join(base_path, "option", "HoloFanArt.csv")
    df = pd.read_csv(holo_path, index_col=0)
    word_list = df["FanArt"].tolist()
    return word_list


def _output() -> dict:
    yaml_path = os.path.join(base_path, "option", "output.yaml")
    with open(yaml_path) as file:
        yml = yaml.safe_load(file)
    return yml


class Output:
    def __init__(self):
        self._base_path = base_path
        self._yml = _output()
        # make folders
        if not os.path.exists(self._yml["base"]["database"]):
            os.makedirs(self._yml["base"]["database"])
        if not os.path.exists(self._yml["base"]["image"]):
            os.makedirs(self._yml["base"]["image"])

        if not os.path.exists(self._yml["holo"]["database"]):
            os.makedirs(self._yml["holo"]["database"])
        if not os.path.exists(self._yml["holo"]["image"]):
            os.makedirs(self._yml["holo"]["image"])

        if not os.path.exists(self._yml["user"]["database"]):
            os.makedirs(self._yml["user"]["database"])
        if not os.path.exists(self._yml["user"]["image"]):
            os.makedirs(self._yml["user"]["image"])

    def base_database(self, hashtag: str):
        return os.path.join(
            self._base_path, self._yml["base"]["database"], f"#{hashtag}_database.csv"
        )

    def base_image(self, hashtag: str):
        return os.path.join(self._base_path, self._yml["base"]["image"], f"#{hashtag}")

    def holo_database(self, hashtag: str):
        return os.path.join(
            self._base_path, self._yml["holo"]["database"], f"#{hashtag}_database.csv"
        )

    def holo_image(self, hashtag: str):
        return os.path.join(self._base_path, self._yml["holo"]["image"], f"#{hashtag}")

    def user_database(self, userName: str):
        return os.path.join(
            self._base_path, self._yml["user"]["database"], f"{userName}_database.csv"
        )

    def user_image(self, userName: str):
        return os.path.join(self._base_path, self._yml["user"]["image"], f"#{userName}")
