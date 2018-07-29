"""
Crawler module for money control.
"""
import os
import urllib
import requests
import tornado.web
import pandas as pd
import tornado.ioloop
from bs4 import BeautifulSoup
from tornado import httpclient
from tornado.concurrent import Future


class AsyncContextManager(object):
    def __enter__(self):
        self.http_client = httpclient.AsyncHTTPClient()
        return self.http_client

    def __exit__(self, type, value, traceback):
        self.http_client.close()


class CrawlHandler(tornado.web.RequestHandler):

    def abs_path(self):
        return os.path.dirname(os.path.abspath(__file__))

    def check_dir(self, folder_path):
        if not os.path.exists():
            os.path.mkdir(folder_path)

    def get_company_list(self):
        url = 'http://www.moneycontrol.com/india/stockpricequote'
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        table = soup.find('table', {'class':'pcq_tbl MT10'})
        rows = table.find_all('td')
        data_row = []
        for row in rows:
            row = row.find('a')
            company_url, company_name = row['href'], row.get_text()
            if company_name:
                data_row.append([company_name, company_url.replace(url, '').split('/')[1], company_url])
        data = pd.DataFrame(columns=['company_name', 'sector', 'url'], data=data_row)
        data.to_csv(os.path.join(self.abs_path(), 'result', 'companies-list.csv'), encoding='utf-8', index=False)


    def get_company_pe(self, url):
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        divs = soup.find('div', {'id': 'mktdet_1'}).find_all('div', {'class': 'PA7 brdb'})
        row = {}
        for div in divs:
            name = div.find('div', {'class': 'FL gL_10 UC'})
            value = div.find('div', {'class': 'FR gD_12'})
            if name and value:
                row[name.get_text().lower().replace(' ', '_')] = value.get_text().replace(',', '').replace('%', '')
        data = pd.DataFrame(data=[row])
        data.to_csv(os.path.join(self.abs_path(), 'result', 'companies-list.csv'), encoding='utf-8', index=False)


    def get_soup(self, response):
        if response.code == 200:
            return BeautifulSoup(response.body, 'html.parser')

    def get(self):
        with AsyncContextManager() as http_client:
            for url in ['https://gramener.com', 'www.google.com', 'www.youtube.com', 'www.facebook.com']:
                http_client.fetch(url, callback=self.get_soup)
        self.write("Fetching results for: {}\n".format(url))


def make_app():
    return tornado.web.Application([
        (r"/", CrawlHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print('Listening at port 8888.')
    tornado.ioloop.IOLoop.current().start()
