import time

import requests
from bs4 import BeautifulSoup
import random

from meetings.models import Meeting, Tag, MeetingStatus

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


class DOUApi:
    url = "https://dou.ua/calendar/city/%D0%9A%D0%B8%D0%B5%D0%B2"

    def _get_headers(self):
        return {
            'User-Agent': random.choice(USER_AGGENTS),
        }

    def get_meetings_by_page(self, page_number):
        page = requests.get(url=f"{self.url}/{page_number}/", headers=self._get_headers())
        print(page)
        if not page.ok:
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
                    "pre_description": meeting_description,
                    "date_string": meeting_date,
                }
            )
        return meetings_data

    def get_meetings(self):
        page_number = 1
        full_meetings_data = []
        while True:
            meetings_data = self.get_meetings_by_page(page_number)
            if meetings_data is None:
                break
            for meeting in meetings_data:
                meeting.update(self.get_meeting(meeting["url"]))
            full_meetings_data += meetings_data
            page_number += 1
        return full_meetings_data

    def get_meeting(self, meeting_url):
        print(meeting_url)
        time.sleep(0.1)
        page = requests.get(url=meeting_url, headers=self._get_headers())
        soup = BeautifulSoup(page.text, 'html.parser')
        full_meeting_description = soup.find("article").text.strip("\n\t").replace(u'\xa0', u' ')
        photo_url = soup.find("img", {"class": "event-info-logo"})
        if photo_url:
            photo_url = photo_url.attrs.get("src")
        tags = soup.find("div", {"class": "b-post-tags"})
        tags = list(map(lambda t: t.text, tags.find_all("a")))
        return {
            "full_description": full_meeting_description,
            "tags": tags,
            "photo_url": photo_url,
        }


class DOULoader:
    api = None
    site = "https://dou.ua/"

    def __init__(self, api: DOUApi):
        assert isinstance(api, DOUApi)
        self.api = api

    def load_meetings(self):
        all_meetings = []
        meetings_data = self.api.get_meetings()
        print("meetings_data: ", meetings_data)
        for meeting in meetings_data:
            try:
                meeting_obj = Meeting.objects.get(related_id=meeting.get("id"))
            except Meeting.DoesNotExist:
                meeting_obj = Meeting.objects.create(
                    related_id=meeting.get("id"),
                    from_site=self.site,
                    from_url=meeting.get("url"),
                    title=meeting.get("name"),
                    description=meeting.get("full_description"),
                    small_description=meeting.get("pre_description"),
                    date_string=meeting.get("date_string"),
                    photo_url=meeting.get("photo_url"),
                    status=MeetingStatus.PUBLISHED,
                    is_main=False,
                )
            all_meetings.append(meeting_obj)
            for tag in meeting.get("tags"):
                tag_obj, created = Tag.objects.get_or_create(name=tag)
                if meeting_obj not in tag_obj.meetings.all():
                    tag_obj.meetings.add(meeting_obj)
        return all_meetings
