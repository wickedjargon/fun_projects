import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://news.ycombinator.com/news'
r = requests.get(url)
html_soup = BeautifulSoup(r.text, 'html.parser')
df_content = []
for item in html_soup.find_all('tr', {'class': 'athing'}):
    id_ = int(item.get('id'))
    rank = item.find('span', {'class': 'rank'}).get_text()
    rank = int(re.sub(r'.$', '', rank))
    title_text = item.find('a', {'class': 'titlelink'}).text
    title_link = item.find('a', {'class': 'titlelink'}).get('href')
    next_row = item.find_next_sibling('tr')
    point_count = next_row.find('span', {'class': 'score'})
    point_count = point_count.text if point_count else '0 points'
    point_count = int(re.sub(' points$', '', point_count))
    age = next_row.find('span', {'class': 'age'}).get('title')
    comment_count = next_row.find('a', string=re.compile(r'comments$'))
    comment_count = comment_count.text if comment_count else '0 comments'
    comment_count = re.sub(r'comments$', '', comment_count)
    comment_count = int(comment_count)
    df_row = [id_, rank, title_text, title_link, age, point_count, comment_count]
    df_content.append(df_row)
df = pd.DataFrame(df_content, columns=['id_', 'rank', 'title_text', 'ext_link', 'date_time_posted', 'point_count', 'comment_count'])
df.to_csv('hacker_news.csv', index=False)
