"""
Configuration file.
"""

# User can update db user name
USER = "root"
# User can update db hostname
HOST = '127.0.0.1'
# User can update db password
PASSWORD = "admin"
# User can update db port number
DATABASE_PORT = '3306'
# User can update db database name
DATABASE_NAME = "moneycontrol"

# URL to fetch list of companies
QUOTE_URL = 'http://www.moneycontrol.com/india/stockpricequote'

# Query to create schema if not exists
SCHEMA_CREATE_QUERY = "create schema if not exists `{schema}` default character set utf8"

# Query to create table schema in database
TABLE_CREATE_QUERY = """
    create table if not exists `{schema}`.`company_data` (
    `company_name` varchar(200) not null,
    `company_title` varchar(200) not null primary key,
    `company_sector` varchar(200) null,
    `company_url` varchar(2000) null,
    `pe_bucket` varchar(2000) null,
    `market_cap_rs_cr` float(6) null,
    `pe` float(6) null,
    `book_value_rs` float(6) null,
    `eps_ttm` float(6) null,
    `face_value_rs` float(6) null,
    `industry_pe` float(6) null,
    `pc` float(6) null,
    `pricebook` float(6) null,
    `updated_on` datetime null
    ) engine = innodb default character set = utf8"""

# Query to drop and re create trigger if already exists.
DROP_TRIGGER_QUERY = """DROP TRIGGER IF EXISTS {schema}.company_data_before_insert;"""

# Query to create trigger, to make sure companies outside predefined list
# should not get inserted to database before insert
TRIGGER_CREATE_QUERY = """
    CREATE DEFINER = CURRENT_USER TRIGGER
    `{schema}`.`company_data_before_insert` BEFORE INSERT ON `{schema}`.`company_data` FOR EACH ROW
    BEGIN
        declare msg varchar(128);
        if new.company_name not in {company_list} then
            set msg = 'You are trying to insert a value which is out of defined list.';
            signal sqlstate '45000' set message_text = msg;
        end if;
    END
    """

# Query to fetch companies list from table
GET_COMPANY_LIST = """select company_url from `{}`.`company_data`"""

# Query to load companies in database
INSERT_UPDATE_COMPANY_LIST = """
    insert into `{schema}`.`company_data` (company_name, company_title, company_sector, company_url)
    values {company_insert} on duplicate key update
    company_sector=values(company_sector),
    company_url=values(company_url)
    """

# Query to update company records in database
UPDATE_COMPANY_DATA = """
    update `{schema}`.`company_data`
    set
    pe_bucket='{pe_bucket}',
    market_cap_rs_cr={market_cap_rs_cr},
    pe={pe},
    book_value_rs={book_value_rs},
    eps_ttm={eps_ttm},
    face_value_rs={face_value_rs},
    industry_pe={industry_pe},
    pc={pc},
    pricebook={pricebook},
    updated_on='{updated_on}'
    where company_name = '{company_name}'
    """

# Query to get nth or highest values from database.
GET_NTOP = (3, 4)
GET_NTH_HIGHEST = """
    SELECT * FROM(SELECT @row_number := @row_number + 1 row_number,
    company_sub_query.company_sector, company_sub_query.market_cap_rs_cr
    FROM (SELECT company_sector, sum(market_cap_rs_cr) as market_cap_rs_cr FROM
    `{schema}`.`company_data` GROUP BY company_sector) company_sub_query,
    (SELECT @row_number := 0) B ORDER BY
    company_sub_query.market_cap_rs_cr DESC) result_query
    WHERE result_query.row_number IN {n_top}
    """
# Query to get PE_RATION DATA
PE_RATIO = """SELECT company_title, pe_bucket FROM `{schema}`.`company_data`"""

# List of companies for which we should be able to insert data
COMPANY_LIST = ('3mindia', '8kmilessoftwareservices', 'aartiindustries', 'abanoffshore', 'abbindia', 'abbottindia', 'acc', 'adanienterprises', 'adaniportsspecialeconomiczone', 'adanipower', 'adanitransmission', 'adityabirlafashionretail', 'advancedenzymetechnologies', 'aegislogistics', 'aiaengineering', 'ajantapharma', 'akzonobelindia', 'alembicpharmaceuticals', 'alkemlaboratories', 'allahabadbank', 'allcargologistics', 'amararajabatteries', 'ambujacements', 'andhrabank', 'aparindustries', 'aplapollotubes', 'apollohospitalsenterprises', 'apollotyres', 'arvind', 'asahiindiaglass', 'ashokleyland', 'ashokabuildcon', 'asianpaints', 'astramicrowaveproducts', 'astralpolytechnik', 'astrazenecapharma', 'atul', 'aurobindopharma', 'avantifeeds', 'avenuesupermarts', 'axisbank', 'bajajauto', 'bajajcorp', 'bajajelectricals', 'bajajfinance', 'bajajfinserv', 'bajajhindusthan', 'bajajholdingsinvestment', 'balkrishnaindustries', 'balmerlawriecompany')
