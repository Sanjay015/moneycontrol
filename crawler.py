"""
Crawler module for money control.
"""
import re
import config
import requests
import tornado.web
import pandas as pd
import tornado.ioloop
from bs4 import BeautifulSoup
from tornado import httpclient
from sqlalchemy import create_engine


class AsyncContextManager(object):
    """
    Context manager to perform asyn http call.
    Created context manager to close async http call even if there is exception.
    """

    def __enter__(self):
        self.http_client = httpclient.AsyncHTTPClient()
        return self.http_client

    def __exit__(self, errortype, value, traceback):
        self.http_client.close()


class DBManagement(object):
    """
    Context manager for DB operations.
    This will help to connect to db and execute the query.
    """

    def execute(self, query):
        return self.conn.execute(query).execution_options(autocommit=True)

    def __enter__(self):
        self.conn_str = 'mysql+mysqldb://{user}:{password}@{host}:{port}'
        self.conn_config = {'user': config.USER, 'host': config.HOST,
                            'password': config.PASSWORD,
                            'port': config.DATABASE_PORT,
                            'schema': config.DATABASE_NAME,
                            'company_list': config.COMPANY_LIST}
        self.conn_str = self.conn_str.format(**self.conn_config)
        self.engine = create_engine(self.conn_str)
        self.conn = self.engine.connect()
        return self


    def __exit__(self, errortype, value, traceback):
        self.conn.close()


class CrawlHandler(tornado.web.RequestHandler):
    """
    A class module to crawl data from money control.
    """

    def setup(self):
        """
        Setup method responsible to create initial DB setups.
        Like create schema/table/triggers.
        DB config and queries are stored in `config.py`.
        """
        with DBManagement() as dbmanager:
            for query in [config.SCHEMA_CREATE_QUERY, config.TABLE_CREATE_QUERY,
                          config.DROP_TRIGGER_QUERY, config.TRIGGER_CREATE_QUERY]:
                dbmanager.conn.execute(query.format(**dbmanager.conn_config))

    def parse_number(self, strnum):
        """
        Method to Parse numbers from string as float.
        """
        pattern = "[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?"
        regex = re.findall(pattern, strnum)
        return float(regex[0]) if regex else None

    def get_company_list(self):
        """
        Get the lists of companies and push them to database table.
        This is a one time job.
        """
        url = 'http://www.moneycontrol.com/india/stockpricequote'
        response = requests.get(url)
        with DBManagement() as dbmanager:
            # Checking if company list exists or not.
            df = pd.read_sql(config.IS_EMPTY_TABLE, dbmanager.conn_str)
            if len(df) > 0 and df['data_exists'].tolist()[0] == 1:
                print('Company list already exists. Skip to fetch company list.')
                return
            print('Company list not avalable. Started fetching company list.')
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                table = soup.find('table', {'class':'pcq_tbl MT10'})
                rows = table.find_all('td')
                for row in rows:
                    row = row.find('a')
                    company_url, company_name = row['href'], row.get_text()
                    if company_name:
                        company_sector = company_url.replace(url, '').split('/')[1].strip()
                        dbmanager.conn_config['company_insert'] = (company_name, company_sector, company_url)
                        dbmanager.conn.execute(config.INSERT_UPDATE_COMPANY_LIST.format(**dbmanager.conn_config))

    def get_company_data(self, content):
        """
        Get all required data for a company as per requirement.
        Push the database to DB.
        """
        soup = BeautifulSoup(content, 'html.parser')
        divs = soup.find('div', {'id': 'mktdet_1'})
        divs = divs.find_all('div', {'class': 'PA7 brdb'})
        row = {}
        requiered_columns = ['book_value_(rs)', 'eps_(ttm)',
                             'face_value_(rs)', 'industry_p/e',
                             'market_cap_(rs_cr)', 'p/c', 'p/e',
                             'price/book']
        for div in divs:
            name = div.find('div', {'class': 'FL gL_10 UC'})
            value = div.find('div', {'class': 'FR gD_12'})
            if name and value:
                name = name.get_text().lower().replace(' ', '_')
                if name in requiered_columns:
                    row[name] = self.parse_number(value.get_text())

    def get_soup(self, response):
        """
        Callback method for async http call.
        """
        if response.code == 200:
            self.get_company_data(self, response.body)

    def get(self):
        self.setup()
        self.get_company_list()
        # Yet to implement company
        # with AsyncContextManager() as http_client:
        #     for url in ['https://www.google.com', 'https://www.youtube.com']:
        #         http_client.fetch(url, callback=self.get_soup)
        # self.write("Fetching results for: {}\n".format(url))


def run_app():
    """
    Start crawler app.
    """
    return tornado.web.Application([
        (r"/", CrawlHandler),
    ])

if __name__ == "__main__":
    app = run_app()
    app.listen(8888)
    print('Listening at port 8888. Press Ctrl+C to close the server.')
    tornado.ioloop.IOLoop.current().start()
