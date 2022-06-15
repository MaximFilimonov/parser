import csv
import fire
from bs4 import *
from tqdm import tqdm
from time import sleep
from os.path import join
from uuid import uuid4 as uuid
import urllib.request, urllib.error, urllib.parse

DATA_DIR = "./data/links"
FILENAME = "polimernye-truby.txt"

def get_page(url):
    """
    This function returns a whole webpage.
    """
    response = urllib.request.urlopen(url)
    return response.read().decode("UTF-8")


def get_data(url):
    """
    This function parses the page and gets the object data, i.e. name, price, etc.
    """
    page = urllib.request.urlopen(url).read().decode("UTF-8")
    page = BeautifulSoup(page, features="html.parser")
    data = {}
    data["id"] = str(uuid())
    data["url"] = url
    data["title"] = page.find("h1", {"id": "pagetitle"}).string

    price = page.find("span", {"class": "price_value"})

    if price is not None:
        data["price"] = page.find("span", {"class": "price_value"}).string
    else:
        data["price"] = "NaN"

    data["currency"] = "rub"

    features = page.find("div", {"class": "char_block bordered rounded3 js-scrolled"})
    for feature in features.find_all("li"):
        data[feature.find("span").string] = feature.find("b").string

    caption = page.find("div", {"class": "content detail-text-wrap"}).string
    data["caption"] = " ".join(caption.split()) # clean caption from tabs and redundant spaces

    return data

def get_all_data(filename=FILENAME):
    """
    This function parses all objects from file with links and saves them to .csv file
    """
    filename = join(DATA_DIR, filename)
    with open(filename, "r") as f:
        urls = [x.strip() for x in f.readlines()]
    
        pbar = tqdm(urls)
        data_all = []

        for url in pbar:
            data = get_data(url)
            data_all.append(data)
            pbar.set_description("Processing url %s" % url)

        with open((filename[:-4] + ".csv"), "w") as output:
            # workoaround for key mismatch
            keys = set()
            for d in data_all:
                keys.update(d.keys())
            
            w = csv.DictWriter(output, restval="NaN", fieldnames=keys)
            w.writeheader()
            w.writerows(data_all)


if __name__ == "__main__":
    fire.Fire(get_all_data)
