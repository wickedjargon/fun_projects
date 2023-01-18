#!/usr/bin/env python3

# Documentation
#
# # The Infostradasports Scraper
# This python script pulls athlete profile information from `infostradasports.com`.

# Imports

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from sys import argv

# Get number of profiles to scrape from command line argument

if len(argv) > 2:
    raise TypeError(
        "This script accepts 1 optional integer command line argument. {len(argv) - 1} were provided."
    )
if len(argv) == 1:
    NUM_OF_ATHLETE_PROFILES_TO_CAPTURE = 0
else:
    try:
        NUM_OF_ATHLETE_PROFILES_TO_CAPTURE = int(argv[1])
    except ValueError:
        raise ValueError(
            "This script accepts 1 optional integer command line argument. Another type was provided."
        )
INFOSTRADASPORTS_URL = "http://ipc.infostradasports.com/asp/lib/TheASP.asp?pageid=8903&sportid=514&NOCClubID=-1&Olympic=0&WinterGames=-1&ContinentGeoID=-1"

# Functions


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
                database[key_d].append("--")
    return database


def get_athlete_database(athlete_profiles):
    unique_keys = get_unique_keys(athlete_profiles)
    database = initialize_database(unique_keys)
    database = fill_database(database, athlete_profiles)
    return database


def fixup_whitespace(text):
    return " ".join(text.split())


## scrape functions


def scrape_athlete_profile(bio_table):
    bio_table_trs = bio_table.find_all("tr")
    details = {}
    for index, tr in enumerate(bio_table_trs):
        if index == 0:
            details["Name"] = fixup_whitespace(tr.get_text())
        else:
            tds = tr.find_all("td")
            details[tds[0].get_text()] = fixup_whitespace(tds[1].get_text())
    return details


def scrape_human_interest_info(bio_table):
    bio_table_trs = bio_table.find_all("tr")
    details = {}
    for index, tr in enumerate(bio_table_trs):
        if len(tr.find_all("td")) == 1:
            continue
        else:
            tds = tr.find_all("td")
            details[tds[0].get_text()] = fixup_whitespace(tds[1].get_text())
    return details


def get_person_id(current_url):
    personid_object = re.search(r"&personid=([0-9]*)&", current_url)
    return personid_object.group(1)


# Script

## Initialize requests session
session = requests.Session()

## Scrape

r = session.get(INFOSTRADASPORTS_URL)
html_parent = r.content
soup = BeautifulSoup(html_parent, "html.parser")
base_url = "http://ipc.infostradasports.com"

if NUM_OF_ATHLETE_PROFILES_TO_CAPTURE == 0:
    paths = [a["href"] for a in soup.find_all("a", href=True)][1:]
else:
    paths = [a["href"] for a in soup.find_all("a", href=True)][
        1 : NUM_OF_ATHLETE_PROFILES_TO_CAPTURE + 1
    ]

athlete_profiles = []
human_interest_infos = []
person_ids = []

for path in paths:
    r = session.get(base_url + path)
    person_id = get_person_id(path)
    person_ids.append(person_id)
    html = r.content
    soup = BeautifulSoup(html, "html.parser")
    bio_tables = soup.find_all("table", {"class": "table_layout1"})
    athlete_profile_soup = bio_tables[0]
    human_interest_info_soup = bio_tables[1]
    athlete_profile = scrape_athlete_profile(athlete_profile_soup)
    athlete_profiles.append(athlete_profile)
    human_interest_info = scrape_human_interest_info(human_interest_info_soup)
    human_interest_infos.append(human_interest_info)

athlete_database = get_athlete_database(athlete_profiles)
df1 = pd.DataFrame(athlete_database)
athlete_interest_database = get_athlete_database(human_interest_infos)
df2 = pd.DataFrame(athlete_interest_database)
df_final = pd.concat([df1, df2], axis=1)
df_final["person_id"] = person_ids

## create csv output
df_final.to_csv("infostradasports_scrape_data.csv", index=False)
