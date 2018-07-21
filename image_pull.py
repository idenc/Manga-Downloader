import os
import queue
import re
import threading

import requests
from bs4 import BeautifulSoup

from display import Display


def gen_title(link):
    """Finds title of manga and removes any illegal characters"""
    page = requests.post(link, data=dict(adult="true"))
    soup = BeautifulSoup(page.text, 'lxml')

    title = soup.find('h1', {"class": "hb dnone"}).find('a').get('title')

    # Search for invalid characters and remove them.
    return re.sub('[^A-Za-z0-9 ]+', '', title)


def get_volume(soup):
    """Finds volume num"""
    volume = soup.find('h1', {"class": "hb dnone"}).findAll('a')
    volume = volume[1].get('title')

    # Grab first number in title
    temp = re.findall('\d+', volume)
    return "Volume " + temp[0]


def write_image(image, title, volume, counter):
    """Writes image to a file"""
    # Write the image to a file in chapter directory
    try:
        imagefile = open(title + "/" + volume + "/" + str(counter) + ".png", 'wb')
        imagefile.write(image.content)
        imagefile.close()
    except IOError:
        queue.put("Could not write image")
        return


def download_manga(start_link, end_link=""):
    """given a start link and end link from twistedhelscans.com, downloads all manga images"""
    next_link = start_link
    counter = 1

    # Deal with end link being first page
    if end_link.endswith('1'):
        end_link = end_link[:-6]

    # get title of manga
    try:
        title = gen_title(start_link)
    except requests.exceptions.MissingSchema:
        queue.put("Could not find title. Website is not Twisted Hel Scan page?")
        return

    while next_link != end_link:
        # Open initial page
        page = requests.post(next_link, data=dict(adult="true"))

        # check if end link is first page redirect
        if page.url == end_link:
            break

        queue.put(page.url)
        soup = BeautifulSoup(page.text, 'lxml')

        if not end_link:
            end_link = soup.find('h1', {"class": "hb dnone"}).find('a').get('href')

        # Find image link and vol. num
        try:
            volume = get_volume(soup)
            image = soup.find('div', {"class": "inner"}).find('img').get('src')
        except requests.exceptions.MissingSchema:
            queue.put("Could not find image link. Website is not Twisted Hel Scan page?")
            return

        # Download the image
        image = requests.get(image)

        # Make manga directory
        if not os.path.exists(title):
            try:
                os.mkdir(title)
            except IOError:
                queue.put("Could not make directory")
                return

        # Make volume directory
        if not os.path.exists(title + "/" + volume):
            try:
                os.mkdir(title + "/" + volume)
            except IOError:
                queue.put("Could not make directory")
                return

            counter = 1

        # Write image to file
        write_image(image, title, volume, counter)
        counter += 1

        # Find next link
        next_link = soup.find('div', {"class": "inner"}).find('a').get('href')
    queue.put("Done")


def on_click(window):
    """Fetches text from entries and calls download manga"""
    start_link = window.start_entry.get()
    end_link = window.end_entry.get()

    if not start_link.strip():
        queue.put("No start link given")
        return

    def callback():
        download_manga(start_link, end_link)

    t = threading.Thread(target=callback)
    t.start()
    display.progress.pack(fill='x')
    display.progress.start(15)


def periodic_call():
    """
    Check every 100 ms if there is something new in the queue.
    """
    display.process_incoming()
    display.root.after(100, periodic_call)


# Create window and bind go button
queue = queue.Queue()
display = Display(queue)
display.go_button.bind("<Button-1>", lambda x: on_click(display))
periodic_call()
display.root.mainloop()
os._exit(1)
