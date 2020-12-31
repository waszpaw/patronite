import pandas as pd
import numpy as np

import time

import urllib.request
import urllib.error

from bs4 import BeautifulSoup


def grab_page():
    # budujemy urla strony
    page_url = f"https://patronite.pl/radio357"

    # zapytanie razem z UserAgent udającym rzeczywistą przeglądarkę na desktopie
    req = urllib.request.Request(page_url,
                                 headers={
                                     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
                                 })

    # czy da się wczytać stronę?
    try:
        page = urllib.request.urlopen(req)
    except Exception as e:
        # zakomentowane, żeby nie psuć progress bara
        # print(f"\n{patronite_id}: {e}")
        return None

    # wczytanie strony i przerobienie na string
    page_doc = page.read().decode('utf-8')

    # parser HTMLa przez BeautifulSoup
    soup = BeautifulSoup(page_doc, 'html.parser')

    # nazwa usera - H1 na stronie
    user_name = soup.find_all("h1")[0].getText().strip()

    # od kiedy w Partonite?
    el = soup.find_all(
        "div", attrs={"class": "author__bio--joinDate"})[0].getText().strip()
    el = el.replace('W Patronite od ', "")
    el = time.strptime(el, "%d.%m.%Y")
    user_date = (el.tm_year, el.tm_mon, el.tm_mday)

    # tagi
    tags = soup.find("div", attrs={"class": "author__header--tags"})
    tags = tags = [t.getText().strip() for t in tags.children if len(t) > 1]
    tags = "|".join(tags)

    dct = {
        "name": user_name,
        "registration_year": user_date[0],
        "registration_month": user_date[1],
        "registration_day": user_date[2],
        "patrons": np.NaN,
        "dotations_per_month": np.NaN,
        "total_dotations": np.NaN,
        "tags": tags
    }

    # ilu darczyńców, ile miesięcznie i ile łącznie?
    if soup.find("div", attrs={"class": "author__stats--wrapper"}) is not None:
        for elem in soup.find("div", attrs={"class": "author__stats--wrapper"}).children:
            if len(elem) > 1:

                ciag = elem.getText().strip().replace("\n", " ")
                if "łącznie" in ciag:
                    liczba = ciag.replace(" zł łącznie", "").replace(" ", "")
                    dct['total_dotations'] = float(liczba)

                if "miesięcznie" in ciag:
                    liczba = ciag.replace(
                        " zł miesięcznie", "").replace(" ", "")
                    dct['dotations_per_month'] = float(liczba)

                if "patronów" in ciag:
                    liczba = ciag.replace("patronów", "").replace(" ", "")
                    dct['patrons'] = int(liczba)

    return pd.DataFrame(dct, index=[0])


if __name__ == "__main__":
    # ramka na zebrane dane
    full_df = pd.DataFrame()
    temp_df = grab_page()

    print(temp_df.dotations_per_month.values[0])
