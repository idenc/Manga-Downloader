import requests
import os
import re
from bs4 import BeautifulSoup


def download_manga(start_link, end_link=""):
    """given a start link and end link from twistedhelscans.com, downloads all manga images"""
    next_link = start_link
    counter = 1

    # Deal with end link being first page
    if end_link.endswith('1'):
        end_link = end_link[:-6]

    page = requests.post(start_link, data=dict(adult="true"))
    soup = BeautifulSoup(page.text, 'lxml')

    title = soup.find('h1', {"class": "hb dnone"}).find('a').get('title')

    # Search for invalid characters and remove them.
    title = re.sub('[^A-Za-z0-9 ]+', '', title)

    while next_link != end_link:
        # Open initial page
        page = requests.post(next_link, data=dict(adult="true"))

        # check if end link is first page redirect
        if page.url == end_link:
            break

        print(page.url)
        soup = BeautifulSoup(page.text, 'lxml')

        # Find image link and vol. num
        try:
            volume = soup.find('h1', {"class": "hb dnone"}).findAll('a')
            volume = volume[1].get('title')

            # Grab first number in title
            temp = re.findall('\d+', volume)
            volume = "Volume " + temp[0]
            image = soup.find('div', {"class": "inner"}).find('img').get('src')
        except:
            print("Could not find image link. Website is not Twisted Hel Scan page?")
            return

        # Download the image
        image = requests.get(image)

        # Make manga directory
        if not os.path.exists(title):
            os.mkdir(title)

        # Make chapter directory
        if not os.path.exists(title + "/" + volume):
            os.mkdir(title + "/" + volume)

        # Write the image to a file in chapter directory
        imagefile = open(title + "/" + volume + "/" + str(counter) + ".png", 'wb')
        imagefile.write(image.content)
        imagefile.close()
        counter += 1

        # Find next link
        next_link = soup.find('div', {"class": "inner"}).find('a').get('href')


download_manga("http://twistedhelscans.com/read/tokyo_ghoul_re/en/5/47/page/1")
