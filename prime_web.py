import re
import random
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class PrimeNewsScraper:
    def __init__(self):
        self.links = []

    def get_soup(self, link):
        page = requests.get(link, headers={'User-Agent': UserAgent().chrome})
        page = page.content.decode('utf-8')
        soup = BeautifulSoup(page, features='html.parser')
        return soup

    def parse_links(self, count_of_page=0):
        while count_of_page < 25000:
            soup = self.get_soup(f'https://1prime.ru/search/?query=&list_sids_or%5B%5D=state_regulation&interval=period'
                                 f'&date_from=2023-01-01&date_to=2023-12-31'
                                 f'&offset={count_of_page}')
            links = soup.find_all("h2", attrs={'class': 'rubric-list__article-title'})
            for link in links:
                href = link.a['href']
                if href not in self.links:
                    self.links.append((href, link.a.text))
            count_of_page += 500
        random.shuffle(self.links)
        self.links = self.links[:250]

    def create_clear_text(self, link):
        try:
            data = requests.get(link, headers={'User-Agent': UserAgent().chrome})
            page = data.content.decode('utf-8')
            soup = BeautifulSoup(page, features='html.parser')
            div = soup.find('div', attrs={'class': 'article-body__content'})
            clear_text = re.sub(r"<[^>]+>", r'', ' '.join(list(map(str, div.find_all('p')))))
            return clear_text
        except:
            return None

    def save_news_to_file(self, filename):
        with open(filename, "w", encoding='utf-8') as outfile:
            for ind, (link, name) in enumerate(self.links, 1):
                text = self.create_clear_text(f"https://1prime.ru/{link}")
                print(f"Added text {ind}")
                if text:
                    print(f"{ind}.{name}\n\n{text}\n", file=outfile)


scraper = PrimeNewsScraper()
scraper.parse_links()
scraper.save_news_to_file('Прайм_news_2023.txt')
