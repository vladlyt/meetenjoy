import time

import requests

from bs4 import BeautifulSoup
import random
from lxml.html import fromstring
from itertools import cycle

USER_AGGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',

    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]


def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


class DOUApi:
    url = "https://dou.ua/calendar/city/%D0%9A%D0%B8%D0%B5%D0%B2"
    running = False
    proxies = None

    def _get_headers(self):
        return {
            'User-Agent': random.choice(USER_AGGENTS),
        }

    def get_meetings_by_page(self, page_number):
        proxy = next(self.proxies)
        print("Proxy", proxy)
        time.sleep(3)
        page = requests.get(url=f"{self.url}/{page_number}/",
                            headers=self._get_headers(),
                            # proxies={"http": proxy, "https": proxy}
                            )
        if not page.ok:
            print(f"Something went wrong: {page.content}")
            return None
        soup = BeautifulSoup(page.text, 'html.parser')
        meetings = soup.find_all("article")
        meetings_data = []
        for meeting in meetings:
            meeting_url = meeting.h2.a.attrs.get("href")
            meeting_id = meeting_url.split("/")[-2]
            meeting_name = meeting.h2.text.strip("\t\n").replace(u'\xa0', u' ')
            meeting_description = meeting.find("p").text.strip("\n\t").replace(u'\xa0', u' ')
            meeting_date = meeting.find("span", {"class": "date"}).text.replace(u'\xa0', u' ')
            meetings_data.append(
                {
                    "id": meeting_id,
                    "url": meeting_url,
                    "name": meeting_name,
                    "description": meeting_description,
                    "date_string": meeting_date,
                }
            )
        return meetings_data

    def get_meetings(self):
        if self.running:
            return None
        if self.proxies is None:
            self.proxies = cycle(get_proxies())
        self.running = True
        try:
            page_number = 1
            full_meetings_data = []
            print("Running get_meetings()")
            while True:
                print(f"Getting data for page number: {page_number}")
                meetings_data = self.get_meetings_by_page(page_number)
                if meetings_data is None:
                    break
                full_meetings_data += meetings_data
                page_number += 1
            return full_meetings_data
        except Exception:
            raise
        finally:
            self.running = False

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super(DOUApi, cls).__new__(cls)
        return cls._instance
