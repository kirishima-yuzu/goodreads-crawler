import requests
from bs4 import BeautifulSoup
import re
import time, random
import os
import csv

def create_csv():
    path = "newbooks.csv"
    with open(path, 'w+') as f:
        csv_write = csv.writer(f)
        csv_head = ["Id", "Title", "Author", "Description", "Rating", "ISBN", "ISBN13", "Publish", "URL", "Review1", "Review2", "Review3", "Review4", "Review5", "Review6", "Review7", "Review8", "Review9", "Review10"]
        csv_write.writerow(csv_head)

def write_csv(data):
    path = "newbooks.csv"
    with open(path, 'a+') as f:
        csv_write = csv.writer(f)
        csv_write.writerow(data)

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
        print("review: " + count)
        return review
    else:
        return ""

with open('books.csv') as f:
    create_csv()
    f_csv = csv.reader(f)
    headers = next(f_csv)

    books = []
    for row in f_csv:
        if int(row[0]) >= 0:
            print(row[0])
            if not bool(re.search('[a-z]', row[1])):
                print(row[0] + row[1] + "skip")
                continue
            writedata = row
            if row[3] != " ":
                review = ""
                wait = 0
                while (review == ""):
                    url = 'https://www.goodreads.com/book/show/' + str(row[0])

                    strhtml = requests.get(url)
                    soup = BeautifulSoup(strhtml.text, 'lxml')
                    review = getReview(soup)
                    time.sleep(3)
                    wait += 1
                    if wait == 4:
                        time.sleep(500)

                if review != "":
                    for r in review:
                        writedata.append(r)
            writedata[2] = getAuthor(soup)
            write_csv(writedata)
            time.sleep(1)

