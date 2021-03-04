import time
from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_pegi_rating(query, game_title):
    # Return game age rating from Pan European Game Information (PEGI) website
    url = "https://pegi.info/search-pegi?q=" + query
    with requests.Session() as s:
        response = s.get(url)
        soup = BeautifulSoup(response.content, features="html.parser")
        content = soup.find('div', class_="page-content")
        containers = content.find_all('div', class_="game-content")

        for result in containers:
            game_name = re.sub('[^A-Za-z0-9]+', ' ', result.find('h3').text).lower().strip()

            if game_name == game_title:
                img_name = result.find('img')['src'].split('/')[-1]
                age_rating = re.sub("[^0-9]", "", img_name)
                return [("PEGI", age_rating)]
        return [("PEGI", "No data")]


def get_esrb_rating(query, game_title):
    # Return game age rating from Entertainment Software Rating Board (ESRB) website
    url = "https://www.esrb.org/search/?searchKeyword=" + query

    options = Options()
    options.add_argument('--headless')

    with webdriver.Chrome(options=options) as driver:
        driver.get(url)
        time.sleep(1)
        games_container = driver.find_elements_by_css_selector("#results > div.game")

        for game in games_container:
            # Find title, clean it and put to lower case
            title = re.sub('[^A-Za-z0-9]+', ' ', game.find_element_by_css_selector("h2").text).lower().strip()
            if title == game_title:
                img_path = game.find_element_by_css_selector("table > tbody > tr:nth-child(2) > td:nth-child(1) > img")\
                    .get_attribute("src")
                age_rating = (img_path.split('/')[-1]).split('.')[0]
                return [("ESRB", age_rating)]
        return [("ESRB", "No data")]


def get_csm_rating(game_title):
    # Return game age rating from Common Sense Media (nonprofit organization) website
    query = "-".join(game_title.split(" "))
    url = "https://www.commonsensemedia.org/game-reviews/" + query

    with requests.Session() as s:
        response = s.get(url)
        soup = BeautifulSoup(response.content, features="html.parser")
        adult_rating = soup.select_one("div.panel-pane.pane-user-review-statistics.stats-adult.stats-adult > div > "
                                       "div > div.stat-wrapper.age")
        kids_rating = soup.select_one("div.panel-pane.pane-user-review-statistics.stats-child.stats-child > div > div "
                                      "> div.stat-wrapper.age")
        if adult_rating:
            parents = adult_rating.text
        else:
            parents = "No data"

        if kids_rating:
            kids = kids_rating.text
        else:
            kids = "No data"

        return [("CSM-parents", parents), ("CSM-kids", kids)]


def find_game(name):
    # Transform game name to a query line
    game_title = re.sub('[^A-Za-z0-9]+', ' ', name).lower().strip()
    query = "+".join(game_title.split(" "))

    esrb = get_esrb_rating(query, game_title)
    pegi = get_pegi_rating(query, game_title)
    csm = get_csm_rating(game_title)

    return esrb + pegi + csm


if __name__ == '__main__':
    print(find_game("Terraria"))
