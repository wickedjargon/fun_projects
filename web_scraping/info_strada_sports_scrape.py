#!/usr/bin/env python
# coding: utf-8
# # info_strada_sports_scrape
#
# This python script pulls athlete profile information from certain `infostradasports.com` pages. It obviously will work on the currently set `INFOSTRADASPORTS_URL` url and likely on other pages with a matching template / design.
#
# ## Global Variables
#
# - `INFOSTRADASPORTS_URL` : URL which data is pulled from.
# - `NUM_OF_ATHLETE_PROFILES_TO_CAPTURE` : number of profiles to capture. Set this to `0` to capture all profiles from page

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
from pprint import pprint

NUM_OF_ATHLETE_PROFILES_TO_CAPTURE = 20
INFOSTRADASPORTS_URL = 'http://ipc.infostradasports.com/asp/lib/TheASP.asp?pageid=8903&sportid=514&NOCClubID=-1&Olympic=0&WinterGames=-1&ContinentGeoID=-1'


def get_unique_keys(athlete_profiles):
    athlete_profile_keys = set()
    for athlete_profile in athlete_profiles:
        for key in athlete_profile:
            athlete_profile_keys.add(key)
    return athlete_profile_keys


def initialize_database(unique_keys):
    athlete_database = {}
    for key in unique_keys:
        athlete_database[key] = []
    return athlete_database


def fill_database(database, athlete_profiles):
    for athlete_profile in athlete_profiles:
        for key_d, value_d in database.items():
            if key_d in athlete_profile:
                database[key_d].append(athlete_profile[key_d])
            else:
                database[key_d].append('--')
    return database


def get_athlete_database(athlete_profiles):
    unique_keys = get_unique_keys(athlete_profiles)
    database = initialize_database(unique_keys)
    database = fill_database(database, athlete_profiles)
    return database


def fixup_whitespace(text):
    return " ".join(text.split())


def scrape_athlete_profile(bio_table):
    bio_table_trs = bio_table.find_all('tr')
    details = {}
    for index, tr in enumerate(bio_table_trs):
        if index == 0:
            details['Name'] = fixup_whitespace(tr.get_text())
        else:
            tds = tr.find_all('td')
            details[tds[0].get_text()] = fixup_whitespace(tds[1].get_text())
    return details


def scrape_human_interest_info(bio_table):
    bio_table_trs = bio_table.find_all('tr')
    details = {}
    for index, tr in enumerate(bio_table_trs):
        if len(tr.find_all('td')) == 1:
            continue
        else:
            tds = tr.find_all('td')
            details[tds[0].get_text()] = fixup_whitespace(tds[1].get_text())
    return details

# Script:


driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(INFOSTRADASPORTS_URL)
links = driver.find_elements_by_xpath("//a[@href]")
athlete_profiles = []
human_interest_infos = []
competition_highlights_infos = []

for index, link in enumerate(links):
    if index == 0:
        continue
    else:
        link.click()
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        bio_tables = soup.find_all('table', {'class': 'table_layout1'})
        athlete_profile_soup = bio_tables[0]
        human_interest_info_soup = bio_tables[1]
        athlete_profile = scrape_athlete_profile(athlete_profile_soup)
        athlete_profiles.append(athlete_profile)
        human_interest_info = scrape_human_interest_info(human_interest_info_soup)
        human_interest_infos.append(human_interest_info)
        driver.back()
    if NUM_OF_ATHLETE_PROFILES_TO_CAPTURE == 0:
        continue
    elif index == NUM_OF_ATHLETE_PROFILES_TO_CAPTURE:
        break
athlete_database = get_athlete_database(athlete_profiles)
df1 = pd.DataFrame(athlete_database)
athlete_interest_database = get_athlete_database(human_interest_infos)
df2 = pd.DataFrame(athlete_interest_database)
df_final = pd.concat([df1, df2], axis=1)
df_final.to_csv('infostradasports_scrape_data.csv')
