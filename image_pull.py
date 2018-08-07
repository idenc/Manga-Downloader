import os
import queue
import re
import threading

import requests
from bs4 import BeautifulSoup

from display import Display


class ImagePull:

    def __init__(self):
        """Create window and bind go button"""
        self.queue = queue.Queue()
        self.display = Display(self.queue)
        self.display.go_button.bind("<Button-1>", lambda x: self.on_click())
        self.periodic_call()
        self.display.root.mainloop()
        os._exit(1)

    def download_manga(self, start_link, end_link=""):
        """given a start link and end link from twistedhelscans.com, downloads all manga images"""
        next_link = start_link
        counter = 1

        # Deal with end link being first page
        if end_link.endswith('1'):
            end_link = end_link[:-6]

        # get title of manga
        try:
            title = self.gen_title(start_link)
        except requests.exceptions.MissingSchema:
            self.queue.put("Could not find title. Website is not Twisted Hel Scan page?")
            return

        while next_link != end_link:
            # Open initial page
            page = requests.post(next_link, data=dict(adult="true"))

            # check if end link is first page redirect
            if page.url == end_link:
                break

            self.queue.put(page.url)
            soup = BeautifulSoup(page.text, 'lxml')

            if not end_link:
                end_link = soup.find('h1', {"class": "hb dnone"}).find('a').get('href')

            # Find image link and vol. num
            try:
                volume = self.get_volume(soup)
                image = soup.find('div', {"class": "inner"}).find('img').get('src')
            except requests.exceptions.MissingSchema:
                self.queue.put("Could not find image link. Website is not Twisted Hel Scan page?")
                return

            # Download the image
            image = requests.get(image)

            # Make manga directory
            if not os.path.exists(title):
                try:
                    os.mkdir(title)
                except IOError:
                    self.queue.put("Could not make directory")
                    return

            # Make volume directory
            if not os.path.exists(title + "/" + volume):
                try:
                    os.mkdir(title + "/" + volume)
                except IOError:
                    self.queue.put("Could not make directory")
                    return

                counter = 1

            # Write image to file
            self.write_image(image, title, volume, counter)
            counter += 1

            # Find next link
            next_link = soup.find('div', {"class": "inner"}).find('a').get('href')
        self.queue.put("Done")

    def gen_title(self, link):
        """Finds title of manga and removes any illegal characters"""
        page = requests.post(link, data=dict(adult="true"))
        soup = BeautifulSoup(page.text, 'lxml')

        title = soup.find('h1', {"class": "hb dnone"}).find('a').get('title')

        # Search for invalid characters and remove them.
        return re.sub('[^A-Za-z0-9 ]+', '', title)

    def get_volume(self, soup):
        """Finds volume num"""
        volume = soup.find('h1', {"class": "hb dnone"}).findAll('a')
        volume = volume[1].get('title')

        # Grab first number in title
        temp = re.findall('\d+', volume)
        return "Volume " + temp[0]

    def write_image(self, image, title, volume, counter):
        """Writes image to a file"""
        # Write the image to a file in chapter directory
        try:
            with open(f"{title}/{volume}/{counter}.png", 'wb') as imagefile:
                imagefile.write(image.content)
        except IOError:
            self.queue.put("Could not write image")
            return

    def on_click(self):
        """Fetches text from entries and calls download manga"""
        start_link = self.display.start_entry.get()
        end_link = self.display.end_entry.get()

        if not start_link.strip():
            self.queue.put("No start link given")
            return

        def callback():
            self.download_manga(start_link, end_link)

        t = threading.Thread(target=callback)
        t.start()
        self.display.progress.pack(fill='x')
        self.display.progress.start(15)

    def periodic_call(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.display.process_incoming()
        self.display.root.after(100, self.periodic_call)


i = ImagePull()
