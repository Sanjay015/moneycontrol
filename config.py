"""
Configuration file.
"""


USER = "root"
HOST = '127.0.0.1'
PASSWORD = "admin"
DATABASE_PORT = '3306'
DATABASE_NAME = "moneycontrol"

SCHEMA_CREATE_QUERY = "create schema if not exists `{schema}` default character set utf8"

TABLE_CREATE_QUERY = """
    create table if not exists `{schema}`.`company_data` (
    `company_name` varchar(200) not null primary key,
    `company_sector` varchar(200) null,
    `company_url` varchar(2000) null,
    `market_cap_(rs_cr)` decimal null,
    `p/e` decimal null,
    `book_value_(rs)` decimal null,
    `eps_(ttm)` decimal null,
    `face_value_(rs)` decimal null,
    `industry_p/e` decimal null,
    `p/c` decimal null,
    `price/book` decimal null,
    `updated_on` datetime null
    ) engine = innodb default character set = utf8"""

DROP_TRIGGER_QUERY = """DROP TRIGGER IF EXISTS {schema}.company_data_before_insert;"""

TRIGGER_CREATE_QUERY = """
    CREATE DEFINER = CURRENT_USER TRIGGER
    `{schema}`.`company_data_before_insert` BEFORE INSERT ON `{schema}`.`company_data` FOR EACH ROW
    BEGIN
        declare msg varchar(128);
        if new.company_name not in {company_list} then
            set msg = 'you are trying to insert a value which is out of defined list.';
            signal sqlstate '45000' set message_text = msg;
        end if;
    END
    """

IS_EMPTY_TABLE = """select exists (select company_name from `moneycontrol`.`company_data`) as data_exists"""

INSERT_UPDATE_COMPANY_LIST = """
    insert into `{schema}`.`company_data` (company_name, company_sector, company_url)
    values {company_insert} on duplicate key update
    company_sector=values(company_sector),
    company_url=values(company_url)
    """

INSERT_UPDATE_COMPANY_DATA = """
    insert into `{schema}`.`company_data`
    (company_name, market_cap_(rs_cr), p/e, book_value_(rs), eps_(ttm), face_value_(rs), industry_p/e, p/c, price/book)
    values ({data_insert})
    on duplicate key update
    market_cap_(rs_cr)=values(market_cap_(rs_cr)),
    p/e=values(p/e),
    book_value_(rs)=values(book_value_(rs)),
    eps_(ttm)=values(eps_(ttm)),
    face_value_(rs)=values(face_value_(rs)),
    industry_p/e=values(industry_p/e),
    p/c=values(p/c),
    price/book=values(price/book),
    updated_on=values(updated_on)
    """

COMPANY_LIST = ('3M India', '8K Miles Soft', 'Aarti Ind', 'Aban Offshore', 'ABB India', 'Abbott India', 'ACC', 'Adani Enterpris', 'Adani Ports', 'Adani Power', 'Adani Trans', 'Aditya Birla F', 'Advanced Enzyme', 'Aegis Logistics', 'AIA Engineering', 'Ajanta Pharma', 'Akzo Nobel', 'Alembic Pharma', 'Alkem Lab', 'Allahabad Bank', 'Allcargo', 'Amara Raja Batt', 'Ambuja Cements', 'Andhra Bank', 'Apar Ind', 'APL Apollo', 'Apollo Hospital', 'Apollo Tyres', 'Arvind', 'Asahi India', 'Ashok Leyland', 'Ashoka Buildcon', 'Asian Paints', 'Astra Microwave', 'Astral Poly Tec', 'AstraZeneca', 'Atul', 'Aurobindo Pharm', 'Avanti Feeds', 'Avenue Supermar', 'Axis Bank', 'Bajaj Auto', 'Bajaj Corp', 'Bajaj Electric', 'Bajaj Finance', 'Bajaj Finserv', 'Bajaj Hind', 'Bajaj Holdings', 'Balkrishna Ind', 'Balmer Lawrie', 'Balrampur Chini', 'Bank of Baroda', 'Bank of India', 'Bank of Mah', 'BASF', 'Bata India', 'Bayer CropScien', 'BEML', 'Berger Paints', 'BF Utilities', 'Bharat Elec', 'Bharat Fin', 'Bharat Forge', 'Bharti Airtel', 'Bharti Infratel', 'BHEL', 'Biocon', 'Birla Corp', 'Bliss GVS', 'Blue Dart', 'Blue Star', 'Bombay Burmah', 'Bombay Dyeing', 'Bosch', 'BPCL', 'Britannia', 'Cadila Health', 'Can Fin Homes', 'Canara Bank', 'Capital First', 'Caplin Labs', 'Carborundum', 'CARE', 'Castrol', 'CCL Products', 'Ceat', 'Central Bank', 'Century', 'CenturyPlyboard', 'Cera Sanitary', 'CESC', 'CG Consumer', 'CG Power', 'Chambal Fert', 'Chennai Petro', 'Cholamandalam', 'Cipla', 'City Union Bank', 'Coal India', 'Coffee Day', 'Colgate', 'Container Corp', 'Coromandel Int', 'Corporation Bk', 'Cox & Kings', 'CRISIL', 'Cummins', 'Cyient', 'Dabur India', 'Dalmia Bharat', 'DB Corp', 'DCB Bank', 'DCM Shriram', 'Deepak Fert', 'Delta Corp', 'Den Networks', 'Dena Bank', 'Dewan Housing', 'Dhanuka Agritec', 'Dilip Buildcon', 'Dish TV', 'Divis Labs', 'DLF', 'Dr Lal PathLab', 'Dr Reddys Labs', 'eClerx Services', 'Edelweiss', 'Eicher Motors', 'EID Parry', 'EIH', 'Elgi Equipments', 'Emami', 'Endurance Techn', 'EngineersInd', 'Ent Network Ind', 'Equitas Holding', 'Eros Intl', 'Escorts', 'Essel Propack', 'Eveready Ind', 'Exide Ind', 'FDC', 'Federal Bank', 'Finolex Cables', 'Finolex Ind', 'Firstsource Sol', 'Force Motors', 'Fortis Health', 'Future Consumer', 'Future Life', 'Future Retail', 'GAIL', 'Gateway Distri', 'Gati', 'Gayatri Project', 'GE Power India', 'GE Shipping', 'GE T&D; India', 'GIC Housing Fin', 'Gillette India', 'GlaxoSmith Con', 'GlaxoSmithKline', 'Glenmark', 'GMR Infra', 'GNFC', 'Godfrey Phillip', 'Godrej Consumer', 'Godrej Ind', 'Godrej Prop', 'Granules India', 'Grasim', 'Greaves Cotton', 'Greenply Ind', 'Grindwell Norto', 'GRUH Finance', 'GSFC', 'Guj Alkali', 'Guj Flourochem', 'Guj Heavy Chem', 'Guj Mineral', 'Guj State Petro', 'Gujarat Gas', 'Gujarat Pipavav', 'Gulf Oil Lubric', 'Hathway Cable', 'Hatsun Agro', 'Havells India', 'HCL Info', 'HCL Tech', 'HDFC', 'HDFC Bank', 'HDIL', 'Heidelberg Cem', 'Heritage Foods', 'Hero Motocorp', 'Hexaware Tech', 'HFCL', 'Himatsingka Sei', 'Hind Constr', 'Hind Copper', 'Hind Zinc', 'Hindalco', 'Honeywell Autom', 'HPCL', 'HSIL', 'HUL', 'ICICI Bank', 'ICICI Prudentia', 'ICRA', 'IDBI Bank', 'Idea Cellular', 'IDFC', 'IDFC Bank', 'IFCI', 'IGL', 'IIFL Holdings', 'ILandFS Trans', 'India Cements', 'Indiabulls Hsg', 'Indiabulls Real', 'Indiabulls Vent', 'Indian Bank', 'Indian Hotels', 'Indo Count', 'Indoco Remedies', 'IndusInd Bank', 'Infibeam Incorp', 'Info Edge', 'Infosys', 'Ingersoll Rand', 'INOX Leisure', 'Inox Wind', 'Intellect Desig', 'Interglobe Avi', 'IOB', 'IOC', 'Ipca Labs', 'IRB Infra', 'ISGEC Heavy Eng', 'ITC', 'ITD Cementation', 'J Kumar Infra', 'J. K. Cement', 'JagranPrakashan', 'Jai Corp', 'Jain Irrigation', 'Jaiprakash Asso', 'JB Chemicals', 'JBF Industries', 'Jet Airways', 'Jindal (Hisar)', 'Jindal PolyFilm', 'Jindal Saw', 'Jindal Steel', 'JK Bank', 'JK Lakshmi Cem', 'JK Tyre & Ind', 'JM Financial', 'Johnson Control', 'JSW Energy', 'JSW Steel', 'Jubilant Food', 'Jubilant Life', 'Just Dial', 'Jyothy Labs', 'Kajaria Ceramic', 'Kalpataru Power', 'Kansai Nerolac', 'Karnataka Bank', 'Kaveri Seed', 'KEC Intl', 'Kesoram', 'Kirloskar Oil', 'Kitex Garments', 'Kotak Mahindra', 'KPIT Tech', 'KPR Mill', 'KRBL', 'Kwality', 'L&T; Finance', 'L&T; Infotech', 'L&T; Technology', 'La Opala RG', 'Lakshmi Machine', 'Lakshmi Vilas', 'Larsen', 'Laurus Labs', 'LIC Housing Fin', 'Linde India', 'Lupin', 'M&M;', 'M&M; Financial', 'Magma Fincorp', 'Mahanagar Gas', 'Mahindra CIE', 'Mahindra Holida', 'Mahindra Life', 'Manappuram Fin', 'Manpasand Bever', 'Marico', 'Marksans Pharma', 'Maruti Suzuki', 'Max Financial', 'Max India', 'Mcleod', 'MCX India', 'Minda Ind', 'Mindtree', 'MMTC Ltd', 'MOIL', 'Monsanto India', 'Motherson Sumi', 'Motilal Oswal', 'MphasiS', 'MRF', 'MRPL', 'MTNL', 'Muthoot Finance', 'NALCO', 'Narayana Hruda', 'Natco Pharma', 'Nava Bharat Ven', 'Navin Fluorine', 'Navkar Corp', 'Navneet', 'NBCC (India)', 'NCC', 'Nestle', 'Network 18', 'NHPC', 'NIIT', 'NIIT Tech', 'Nilkamal', 'NLC India', 'NMDC', 'NTPC', 'Oberoi Realty', 'OCL India', 'Oil India', 'Omaxe', 'ONGC', 'Oracle Fin Serv', 'Orient Cement', 'Oriental Bank', 'P and G', 'Page Industries', 'Parag Milk Food', 'PC Jeweller', 'Persistent', 'Petronet LNG', 'Pfizer', 'Phoenix Mills', 'PI Industries', 'Pidilite Ind', 'Piramal Enter', 'PNB', 'PNB Housing Fin', 'PNC Infratech', 'Polaris Consult', 'Power Finance', 'Power Grid Corp', 'Praj Industries', 'Prestige Estate', 'Prism Cement', 'PTC India', 'PTC India Fin', 'PVR', 'Radico Khaitan', 'Rain Industries', 'Rajesh Exports', 'Rallis India', 'Ramco Cements', 'Rashtriya Chem', 'Ratnamani Metal', 'Rattan Power', 'Raymond', 'RBL Bank', 'REC', 'Redington', 'Rel Capital', 'Relaxo Footwear', 'Reliance', 'Reliance Comm', 'Reliance Infra', 'Reliance Naval', 'Reliance Power', 'Religare Enterp', 'Repco Home', 'Rolta', 'S H Kelkar', 'Sadbhav Engg', 'SAIL', 'Sanofi India', 'SBI', 'Schaeffler Ind', 'Schneider Infra', 'Sequent Scienti', 'Sharda Crop', 'Sheela Foam', 'Shilpa', 'Shipping Corp', 'Shoppers Stop', 'Shree Cements', 'Shree Renuka', 'Shriram City', 'Shriram Trans', 'Siemens', 'Siti Networks', 'SJVN', 'SKF India', 'SML Isuzu', 'Sobha', 'Solar Ind', 'Somany Ceramics', 'Sonata', 'South Ind Bk', 'SpiceJet', 'SREI Infra', 'SRF', 'Sterlite Techno', 'Strides Shasun', 'Sudarshan Chem', 'Sun Pharma', 'Sun Pharma Adv', 'Sun TV Network', 'Sundram', 'Sunteck Realty', 'Supreme Ind', 'Suven Life Sci', 'Suzlon Energy', 'Swan Energy', 'Symphony', 'Syndicate Bank', 'Syngene Intl', 'Take Solutions', 'Tamil Newsprint', 'Tata Chemicals', 'Tata Coffee', 'Tata Comm', 'Tata Elxsi', 'Tata Global Bev', 'Tata Inv Corp', 'Tata Motors', 'Tata Motors (D)', 'Tata Power', 'Tata Sponge', 'Tata Steel', 'TCS', 'Tech Mahindra', 'Techno Electric', 'Texmaco Rail', 'Thermax', 'Thomas Cook', 'Thyrocare Techn', 'TI Financial', 'Timken', 'Titagarh Wagons', 'Titan Company', 'Torrent Pharma', 'Torrent Power', 'Trent', 'Trident', 'Triveni Turbine', 'TTK Prestige', 'TV TodayNetwork', 'TV18 Broadcast', 'TVS Motor', 'TVS Srichakra', 'UCO Bank', 'Uflex', 'Ujjivan Financi', 'UltraTechCement', 'Unichem Labs', 'Union Bank', 'Unitech', 'United Brewerie', 'UPL', 'V-Guard Ind', 'Va Tech Wabag', 'Vakrangee', 'Vardhman Text', 'Varun Beverages', 'Vedanta', 'Videocon Ind', 'Vijaya Bank', 'Vinati Organics', 'VIP Industries', 'Voltas', 'VST', 'WABCO India', 'Welspun Corp', 'Welspun India', 'Westlife Dev', 'Whirlpool', 'Wipro', 'Wockhardt', 'Wonderla', 'Yes Bank', 'Zee Entertain', 'Zensar Tech')
