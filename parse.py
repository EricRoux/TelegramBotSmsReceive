from bs4 import BeautifulSoup
import urllib.request
from re import sub


def get_html(url):
    response = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(response, features="lxml")
    return soup


def search_phone(url):
    table = get_html(url).find('div', class_='row text-center channel')
    rows = table.find_all('div', class_='col-sm col-sm-4')
    phones = {}
    for i in rows:
        phone_status = i.find('h3').text
        phone_number = i.find("b").text
        phone_href = i.find('a').get('href')
        phone_received = sub(r'\D', '', i.find_all('p')[-1].text)
        if phone_status == "Online":
            phones[phone_number] = [phone_href, phone_received]
    return phones


def search_country(url):
    table = get_html(url).find('div', class_='row text-center channel')
    rows = table.find_all('div', class_='col-sm')[:-1]
    countries = {}
    for i in rows:
        Country = i.find('a').text
        href = i.find('a').get('href')
        Numbers = sub(r'\D', '', i.find('p').text)
        if int(Numbers) > 0:
            countries[Country] = [href, Numbers]
    return countries


def search_image(url):
    soup = get_html(url)
    img = soup.find_all('div', class_='my-3 p-3 bg-white rounded shadow-sm')[-1].find('img').get('src')
    return img
