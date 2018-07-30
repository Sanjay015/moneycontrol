"""
Crawler module for money control.
"""
import os
import re
import sys
import config
import logging
import requests
import argparse
import sqlalchemy
import tornado.web
import numpy as np
import pandas as pd
import tornado.ioloop
from datetime import datetime
from bs4 import BeautifulSoup
from tornado import httpclient



class DBManagement(object):
    """
    Context manager for DB operations.
    This will help to connect to db and execute the query.
    """

    def execute(self, query):
        """
        Execute database queries.
        """
        return self.conn.execute(query).execution_options(autocommit=True)

    def __enter__(self):
        self.conn_str = 'mysql+mysqldb://{user}:{password}@{host}:{port}'
        self.conn_config = {'user': config.USER, 'host': config.HOST,
                            'password': config.PASSWORD,
                            'port': config.DATABASE_PORT,
                            'schema': config.DATABASE_NAME,
                            'company_list': config.COMPANY_LIST}
        self.conn_str = self.conn_str.format(**self.conn_config)
        self.engine = sqlalchemy.create_engine(self.conn_str)
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
        logger = logging.getLogger('MONEYCONTROLAPP')
        with DBManagement() as dbmanager:
            for query in [config.SCHEMA_CREATE_QUERY, config.TABLE_CREATE_QUERY,
                          config.DROP_TRIGGER_QUERY, config.TRIGGER_CREATE_QUERY]:
                query = query.format(**dbmanager.conn_config)
                try:
                    dbmanager.conn.execute(query)
                except Exception as ex:
                    logger.error('Failed to execute query {} due to {}'.format(query.replace('\n', ' '), ex.args))

    def parse_number(self, strnum):
        """
        Method to Parse numbers from string as float.
        """
        pattern = "[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?"
        regex = re.findall(pattern, strnum)
        return float(regex[0].replace(',', '')) if regex else 'null'

    def get_bucket(self, value):
        """
        Method to put data into relavant bucket.
        Classify P/E Ratio in bucket.
        """
        if value in ['null', 'NULL', '', None]:
            return 'null'
        if value < 0:
            return '<0'
        if value > 100:
            return '100+'
        number_of_bins = 20
        bins = np.linspace(0, 100, number_of_bins + 1)
        pos = np.digitize(value, bins).item()
        return "{}-{}".format(int(bins[pos - 1]), int(bins[pos]))

    def get_company_url(self, dbmanager):
        """
        Get the lists of companies and push them to database table.
        This is a one time job.
        """
        url = config.QUOTE_URL
        logger = logging.getLogger('MONEYCONTROLAPP')
        response = requests.get(url)
        if response.status_code == 200:
            # Parsing html content.
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'class':'pcq_tbl MT10'})
            rows = table.find_all('td')
            row_count = 0
            for row in rows:
                row = row.find('a')
                # Extracting company's url and company name.
                company_url, company_title = row['href'], row.get_text()
                if company_title:
                    company_sector = company_url.split('/')[-3].strip()
                    company_name = company_url.split('/')[-2].strip()
                    # Constructing query
                    dbmanager.conn_config['company_insert'] = (company_name, company_title, company_sector, company_url)
                    # Pushing companies to database table
                    query = config.INSERT_UPDATE_COMPANY_LIST.format(**dbmanager.conn_config)
                    try:
                        dbmanager.conn.execute(query)
                        row_count += 1
                    except sqlalchemy.exc.OperationalError as ex:
                        logger.error('Failed to execute query {} due to {}'.format(query.replace('\n', ' '), ex.args))
                    except Exception as ex:
                        logger.error('Failed to execute query {} due to {}'.format(query.replace('\n', ' '), ex.args))
            logger.debug('Inserted total {} rows(company list) to database.'.format(row_count))
        else:
            logger.debug('Unable to connect to {}, due to {} error code and {} reason.'.format(
                url, response.status_code, response.reason))

    def get_company_stats(self, content, company_name):
        """
        Get all required data for a company as per requirement.
        Push the database to DB.
        """
        logger = logging.getLogger('MONEYCONTROLAPP')
        # Parsing html content.
        soup = BeautifulSoup(content, 'html.parser')
        # Get div which contains company's stats.
        div = soup.find('div', {'id': 'mktdet_1'})
        # In some cases 'id': 'mktdet_1' is hidden and in some cases.
        # 'id': 'mktdet_2' is hidden. Making sure that we are
        # fetching data from correct id.
        divstyle = div.get('style') or ''
        if 'display:none;' in divstyle.replace(' ', ''):
            div = soup.find('div', {'id': 'mktdet_2'})
        # Find all relevant tags.
        divs = div.find_all('div', {'class': 'PA7 brdb'})
        row = {}
        # List of required columns which should pushed to DB.
        requiered_columns = ['book_value_rs', 'eps_ttm', 'face_value_rs', 'industry_pe',
                             'market_cap_rs_cr', 'pc', 'pe', 'pricebook']
        # Parsing statistics of company.
        for div in divs:
            name = div.find('div', {'class': 'FL gL_10 UC'})
            value = div.find('div', {'class': 'FR gD_12'})
            if name and value:
                name = name.get_text().lower().strip()
                name = name.replace('(', '').replace(')', '')
                name = name.replace(' ', '_').replace('%', '').replace('/', '')
                # Add only required columns.
                if name in requiered_columns:
                    value = self.parse_number(value.get_text())
                    if name == 'pe':
                        row['pe_bucket'] = self.get_bucket(value)
                    row[name] = value
        # Maintaining dict to format the query
        row['updated_on'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row['company_name'] = company_name
        row['schema'] = config.DATABASE_NAME
        # Connect to db and update the records
        with DBManagement() as dbmanager:
            # Updating stats for company in table.
            query = config.UPDATE_COMPANY_DATA.format(**row)
            try:
                dbmanager.conn.execute(query)
            except Exception as ex:
                logger.error('Failed to execute query {} due to {}'.format(query.replace('\n', ' '), ex.args))

    def get_data(self, response):
        """
        Callback method for async http call.
        """
        logger = logging.getLogger('MONEYCONTROLAPP')
        company_url = response.effective_url
        company_name = company_url.split('/')[-2].strip()
        # If any error in response logging it
        if response.error:
            logger.error('Content no longer available for company "{}" url: {}, error {}'.format(
                company_name, company_url, response.error))
        else:
            logger.debug('Updating records for company "{}" from url: {}'.format(company_name, company_url))
            # Parsing the company data.
            self.get_company_stats(response.body, company_name)

    def get(self):
        logger = logging.getLogger('MONEYCONTROLAPP')
        logger.debug('Running initial DB setup if required.')
        # Initial database setup.
        self.setup()

        with DBManagement() as dbmanager:
            # Checking if company list exists or not.
            query = config.GET_COMPANY_LIST.format(config.DATABASE_NAME)
            company_list = pd.read_sql(query, dbmanager.conn_str)
            # If list exists we will simply go and look for companies stats.
            # Otherwise will fetch the list of companies.
            if len(company_list) > 0:
                logger.warn('Company list already exists. Skip to fetch company list.')
            else:
                logger.warn('Company list not avalable. Started fetching company list.')
                # Get companies list.
                self.get_company_url(dbmanager)
                company_list = pd.read_sql(query, dbmanager.conn_str)

        # Making async http call to fetch companies stats without http request block.
        http_client = httpclient.AsyncHTTPClient()
        # ['http://www.moneycontrol.com/india/stockpricequote/financeinvestments/bajajfinserv/BF04']
        for url in company_list['company_url'].dropna().unique().tolist():
            logger.debug('Navigating to {}'.format(url))
            # Connecting to company's url.
            http_client.fetch(url, self.get_data)
        self.write("Fetching results for: {}\n".format(url))


class InsightHandler(tornado.web.RequestHandler):
    """InsightHandler to get insight as per requirement."""

    def nth_highest_company(self):
        """
        Get nth highest company from database.
        """
        pass

    def pe_ratio_interval(self):
        """
        Get company list in against each `bucket`.
        """
        pass

    def get(self):
        """
        Write data to page.
        """
        with DBManagement() as dbmanager:
            query = config.GET_COMPANY_LIST.format(config.DATABASE_NAME)
            company_list = pd.read_sql(query, dbmanager.conn_str)
            self.write(company_list.to_html())

def setup_logger():
    """
    A method to setup logger
    """
    # Creating log directory
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    log_file = os.path.join(log_dir, 'output-log.log')
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    # Setting up logger
    logger = logging.getLogger('MONEYCONTROLAPP')
    logger.setLevel(logging.DEBUG)
    logger_fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # Setting stream handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logger_fmt)
    logger.addHandler(stream_handler)
    # Setting file handler
    file_handler = logging.handlers.RotatingFileHandler(log_file, backupCount=7)
    file_handler.setFormatter(logger_fmt)
    logger.addHandler(file_handler)


def run_app():
    """
    Start crawler app.
    """
    return tornado.web.Application([
        (r"/", CrawlHandler),
        (r"/insight/", InsightHandler),
    ])

if __name__ == "__main__":
    setup_logger()
    # Get app port number from command line argument
    parser = argparse.ArgumentParser(description='Process argument parsers.')
    parser.add_argument('-p', '--port', default='8888', help='Enter port number.')
    args = parser.parse_args()
    app = run_app()
    app.listen(int(args.port))
    logger = logging.getLogger('MONEYCONTROLAPP')
    logger.info('Started running moneycontrol crawler app at port {}. Press Ctrl+C to close the server.'.format(args.port))
    tornado.ioloop.IOLoop.current().start()
