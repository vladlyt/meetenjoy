import re
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


class MeetupApi:
    url = "https://www.meetup.com/ru-RU/find/events/?allMeetups=true&radius=3&userFreeform=%D0%9A%D0%B8%D0%B5%D0%B2&mcId=c1039926&mcName=%D0%9A%D0%B8%D0%B5%D0%B2%2C+UA"
    site = "https://www.meetup.com/"

    def _get_headers(self):
        return {
            'User-Agent': random.choice(USER_AGGENTS),
        }

    def get_data_from_group(self, url):
        time.sleep(0.1)
        page = requests.get(url=url, headers=self._get_headers())
        soup = BeautifulSoup(page.text, 'html.parser')

        meetings = []

        div = soup.find("div", {"class": "groupHome-eventsList-upcomingEvents"})
        if div:
            for meeting_data in div.find_all("div", {"class": "chunk"}):
                meetings.append(self.get_meeting(f'{self.site}{meeting_data.div.a.attrs.get("href").lstrip("/")}'))
        return meetings

    def get_meetings(self):
        page = requests.get(url=f"{self.url}", headers=self._get_headers(), )
        if not page.ok:
            print("ERROR")
            return []
        soup = BeautifulSoup(page.text, 'html.parser')
        meetings_data = soup.find("ul", {"class": "searchResults"})
        parsed_meetings_data = []
        for meeting_data in meetings_data.find_all("li"):
            if "event-listing-container-li" in meeting_data.attrs["class"]:
                for meeting in meeting_data.find("ul", {"class": "event-listing-container"}).find_all("li"):
                    if "event-listing" in meeting.attrs["class"]:
                        div1, div2, *_ = meeting.find_all("div")
                        url = div2.div.a.attrs.get("href")
                        print(url)
                        if "events" not in url:
                            parsed_meetings_data += self.get_data_from_group(url)
                        else:
                            parsed_meetings_data.append(
                                self.get_meeting(url)
                            )
            else:
                pass
        return parsed_meetings_data

    def get_meeting(self, meeting_url):
        print("meeting_url", meeting_url)
        time.sleep(0.1)
        page = requests.get(url=meeting_url, headers=self._get_headers())
        soup = BeautifulSoup(page.text, 'html.parser')

        uuid = meeting_url.split("/")[-2]
        title = soup.find("h1", {"class": "text--pageTitle"})
        if title:
            title = title.text

        date_string = soup.find("time", {"class": "eventStatusLabel"})
        if date_string:
            date_string = date_string.span.text

        description = soup.find("div", {"class": "event-description"})
        description_html = None
        if description:
            description_html = description.contents[0]
            description = description.text
        photo = soup.find("div", {"class": "photoCarousel-photoContainer"})
        if photo:
            photo = re.fullmatch(r".*\((http.*)\)", photo.attrs["style"])[1]
        return {
            "uuid": uuid,
            "url": meeting_url,
            "title": title,
            "date_string": date_string,
            "description": description,
            "description_html": description_html,
            "photo_url": photo,
        }


class MeetupLoader:
    api = None
    site = "https://www.meetup.com/"

    def __init__(self, api: MeetupApi):
        assert isinstance(api, MeetupApi)
        self.api = api

    def load_meetings(self):
        all_meetings = []
        meetings_data = self.api.get_meetings()
        for meeting in meetings_data:
            try:
                meeting_obj = Meeting.objects.get(
                    from_site=self.site,
                    related_id=meeting.get("id")
                )
            except Meeting.DoesNotExist:
                meeting_obj = Meeting.objects.create(
                    related_id=meeting.get("uuid"),
                    from_site=self.site,
                    from_url=meeting.get("url"),
                    title=meeting.get("title"),
                    description=meeting.get("description"),
                    date_string=meeting.get("date_string"),
                    photo_url=meeting.get("photo_url"),
                    status=MeetingStatus.PUBLISHED,
                    is_main=False,
                )
            all_meetings.append(meeting_obj)
        return all_meetings
