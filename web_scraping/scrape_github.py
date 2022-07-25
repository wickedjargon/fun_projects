from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

# DOCUMENTATION:
# Purpose: This script pulls a personal (non-special account) github account's reppo information
# global varialbles:
# `GITHUB_USER_NAME` can be changed to another github user


GITHUB_USER_NAME = 'protesilaos'


def get_driver():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    return driver


def get_soup(driver, user_name, page_num=None):
    if page_num is None or page_num == 1:
        url = f'https://github.com/{user_name}?tab=repositories'
    else:
        url = f'https://github.com/{user_name}?page={page_num}&tab=repositories'
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    return soup


def get_df(page_num, soup):
    repos_section = soup.find('div', {'id': 'user-repositories-list'})
    try:
        repos = repos_section.find_all('li')
    except AttributeError:
        repos = []
    rows = []
    for repo in repos:
        name_all = repo.find('a', {'itemprop': 'name codeRepository'})
        name_text = name_all.text
        name_text = name_text.replace('\n', '').strip()
        name_link = name_all['href']
        description = repo.find('p', {
            'itemprop': 'description'
        }).get_text().replace('\n', '').strip()
        time_updated = repo.find('relative-time')['datetime']
        pri_language = repo.find('span', {'itemprop': 'programmingLanguage'})
        try:
            pri_language = pri_language.text
        except AttributeError:
            pri_language = str(pri_language)
        row = [name_text, name_link, description, time_updated, pri_language]
        rows.append(row)
    if page_num == 0 or page_num is None:
        df = pd.DataFrame(rows)
    else:
        df = pd.DataFrame(rows,
                          columns=[
                              'name_text', 'name_link', 'description',
                              'time_updated', 'pri_language'
                          ])
    return df


def is_page_num_out_of_range(soup):
    return soup.find('h2', {'class': 'blankslate-heading'})


def main():
    driver = get_driver()
    df_all = pd.DataFrame()
    for page_num in range(1, 1000):
        soup = get_soup(driver, GITHUB_USER_NAME, page_num)
        if is_page_num_out_of_range(soup):
            break
        df = get_df(page_num, soup)
        df_all = pd.concat([df_all, df])
    df_all.to_csv('github_repos.csv', index=False)


if __name__ == '__main__':
    main()
