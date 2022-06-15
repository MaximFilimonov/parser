import fire
from bs4 import *
from tqdm import tqdm
from time import sleep
import urllib.request, urllib.error, urllib.parse


URL_SITE = "https://nf-truba.ru"
CATALOG = "/polimernye-truby"
URL_CATALOG = URL_SITE + "/catalog" + CATALOG

def get_page(url):
    """
    This function returns a whole webpage.
    """
    response = urllib.request.urlopen(url)
    return response.read().decode("UTF-8")


def get_all_pages(url_catalog, pages_num=1):
    """
    This function returns a list of whole webpages. Used to send a list of webpages to parser
    """
    all_pages = []
    pbar = tqdm(range(pages_num))

    for url_num in pbar:
        pbar.set_description("Downloading whole page. Processing %s page" % (url_num + 1))
        url = url_catalog + "/?PAGEN_1=" + str(url_num + 1)
        webContent = get_page(url)
        all_pages.append(webContent)
        sleep(2)

    return all_pages


def get_urls_list(page):
    """
    This function parses a webpage and generates a list of URLs of objects on one page
    """
    soup = BeautifulSoup(page, features="html.parser")
    divs = soup.find_all("div", {"class": "item-info table-view__info-top"})

    urls = []

    for div in divs:
        for a in div.find_all("a", href=True):
            urls.append(URL_SITE + a["href"])

    return urls


def flatten(lst):
    """
    This function flattens the list
    """
    return [x for xs in lst for x in xs]


def get_all_urls_list(all_pages):
    """
    This function gets a list of URLs of objects. 
    """
    all_urls = []
    pbar = tqdm(range(len(all_pages)))

    for page in pbar:
        pbar.set_description("Processing %s page" % (page + 1))
        urls = get_urls_list(all_pages[page])
        all_urls.append(urls)

    return flatten(all_urls)


def get_urls(category: str, pages_num=1):
    print("Processing category: %s" % category)
    url_catalog = URL_SITE + "/catalog/" + category
    all_pages = get_all_pages(url_catalog, int(pages_num))
    url_list = get_all_urls_list(all_pages)

    print("Got %s object urls. Saving..." % len(url_list))

    with open("../data/links/" + category + ".txt", "w") as f:
        for url in url_list:
            f.write("%s\n" % url)

    print("All links for category \"%s\" saved!" % category)


if __name__ == "__main__":
    fire.Fire(get_urls)
