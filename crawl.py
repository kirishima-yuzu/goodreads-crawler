import requests
from bs4 import BeautifulSoup
import re
import time, random
import os
import csv


def getTitle(soup):
    data = soup.select('#bookTitle')

    tit = data[0].get_text().strip()
    return tit

def getAuthor(soup):
    data = soup.select('#bookAuthors > span:nth-child(2) > div > a > span')
    if data == []:
        return None
    else:
        author = data[0].get_text().strip()
        data1 = soup.select('#bookAuthors > span:nth-child(2) > div:nth-child(2) > a > span')
        if data1 != []:
            author += " ," + data1[0].get_text().strip()
            data2 = soup.select('#bookAuthors > span:nth-child(2) > div:nth-child(3) > a > span')
            if data2 != []:
                author += " ," + data2[0].get_text().strip()
        return author

def getImagelink(soup):
    data = soup.select('#coverImage')
    if data==[]:
        link = 'https://s.gr-assets.com/assets/nophoto/book/blank-133x176-8b769f39ba6687a82d2eef30bdf46977.jpg'
    else:
        link = data[0].get('src')
    return link

def getRating(soup):
    data = soup.select('#bookMeta > span:nth-child(2)')

    rating = data[0].get_text().strip()
    return rating

def getDescription(soup):
    data = soup.select('#description')

    if data != []:
        pattern = re.compile('freeText([0-9]+)')
        pattern1 = re.compile('freeTextContainer([0-9]+)')
        textserch = re.search(pattern, str(data), flags=0)
        if textserch:
            textposi = textserch.span()
        else:
            textserch = re.search(pattern1, str(data), flags=0)
            textposi = textserch.span()
        text = str(data)[textposi[0]:textposi[1]]
        data = soup.select('#' + text)
        for item in data:
            description = item.get_text()
        return description
    else:
        return " "

def getISBN(soup):
    data = soup.select('#bookDataBox > div:nth-child(2) > div.infoBoxRowItem')
    if data == []:
        return 0, 0
    else:
        if not bool(re.search(r'\d', str(data))):
            return None, None
        ISBN = data[0].get_text().strip()

        if str(ISBN)[0].isdigit():

            isbnlist = ISBN.split()
            if len(isbnlist) == 1:
                if len(isbnlist[0]) == 13:
                    return None, isbnlist[0]
                else: return isbnlist[0],None
            else:
                isbn = isbnlist[0]
                ISBN13 = (ISBN.split())[2][:-1]
                return isbn, ISBN13
        else:
            return None, None

def getReview(soup):
    data = soup.select('#bookReviews')
    if len(str(data)) > 2:
        reviewpattern = re.compile('freeText([0-9]+)')
        count = 0
        review = []
        reviewserch = re.search(reviewpattern, str(data), flags=0)
        while(reviewserch):
            reviewposi = reviewserch.span()
            reviewtag = str(data)[reviewposi[0]:reviewposi[1]]
            data1 = soup.select('#' + reviewtag)
            for item in data1:
                temp = item.get_text()
            if bool(re.search('[a-z]', temp)):
                review.append(temp)
                count += 1
            data = str(data)[reviewposi[1]:]
            reviewserch = re.search(reviewpattern, str(data), flags=0)
            if count == 10:
                break
        return review
    else:
        return ""





def getPublish(soup):
    data = soup.select('#details > div:nth-child(2)')
    if data == []:
        return None
    else:
        for item in data:
            publish = item.get_text().strip()
        publish = publish[9:]

        publish = publish.replace('\n', '')
        return ' '.join(publish.split())

def downloadImage(url, id):
    r = requests.get(url)
    with open('./image/'+id+'.png', 'wb') as f:
        f.write(r.content)

def create_csv():
    path = "newbooks8.csv"
    with open(path, 'w+') as f:
        csv_write = csv.writer(f)
        csv_head = ["Id", "Title", "Author", "Description", "Rating", "ISBN", "ISBN13", "Publish", "URL", "Review1", "Review2", "Review3", "Review4", "Review5", "Review6", "Review7", "Review8", "Review9", "Review10"]
        csv_write.writerow(csv_head)


def write_csv(data):
    path = "newbooks8.csv"
    with open(path, 'a+') as f:
        csv_write = csv.writer(f)
        csv_write.writerow(data)


if __name__ == '__main__':
    create_csv()
    count = 0
    for i in range(80000, 140000):

        if count >= 2:
            time.sleep(530)
        # proxies = {
        #     "http": 'http://47.243.135.104:8080',
        #     "https": 'http://47.243.135.104:8080'
        # }
        bookid = i
        print(bookid)
        url = 'https://www.goodreads.com/book/show/'+str(bookid)
        print(url)
        strhtml = requests.get(url)
        soup = BeautifulSoup(strhtml.text, 'lxml')

        page = soup.select('head > title')

        if page != []:
            pagename = page[0].get_text().strip()
            if pagename == "Page not found":
                continue

        data = soup.select('#bookTitle')
        if data == []:
            time.sleep(10)
            url = 'https://www.goodreads.com/book/show/' + str(bookid)
            strhtml = requests.get(url)
            soup = BeautifulSoup(strhtml.text, 'lxml')
            data1 = soup.select('#bookTitle')
            if data1 == []:
                count += 1
                continue


        title = getTitle(soup)
        if not bool(re.search('[a-z]', title)):
            print(title+"skip")
            continue
        author = getAuthor(soup)
        url = getImagelink(soup)
        rating = getRating(soup)
        des = getDescription(soup)
        ISBN, ISBN13 = getISBN(soup)

        if ISBN == 0:
            continue
        print(title, des)
        publish = getPublish(soup)
        review = getReview(soup)

        writedata = [bookid, title, author, des, rating, ISBN, ISBN13, publish, url]
        if review != "":
            for r in review:
                writedata.append(r)

        write_csv(writedata)
        count = 0
        time.sleep(3)

