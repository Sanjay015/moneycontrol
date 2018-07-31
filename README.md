#### Moneycontrol Application:
This is an application to pull data from [moneycontrol](https://www.moneycontrol.com/india/stockpricequote/) and put the data into database(MySQL). This application is purely written in `python`. Built on top of `tornado` web server. Making a `Async` web request in order to pull data for multiple companies in parallel.
##### About:
- To run this application you must have to connected to `internet`.
- There is a predefined list of companies (please see `COMPANY_LIST` in `config.py`) only feor them data can be pushed to database.
- It will connect [moneycontrol](https://www.moneycontrol.com/india/stockpricequote/) and get the list of companies available there and pull the data only for predefined companies in `config.py`.
- In very first run of application will fetch the list of companies along with relavant URL and push them to database. In this step it will be able to get comapny name, company sector and ompany URL which holds the actual stats for the company.
- Then it will iterate over URL for each company to fetch the stats and will update other relavant stats columns in database like `pe`, `pc`, `market_cap_ce` etc.
- In case if company URL is already available in DB then it will get relavant stats from the company URL and will update the records.
 ##### Requirements:
   - MySQL database to store data
   - `mysql+mysqldb` sqlalchemy database driver
     ###### Python(3.6.3) required packages:
     - Pandas - 0.20.3
     - Numpy - 1.13.3
     - Tornado - 4.5.2
     - requests - 2.18.4
     - bs4 - 4.6.0
     - sqlalchemy - 1.1.13
     - json
     - datetime
     - re - 2.2.1
     ###### JavaScript and CSS required pachages are already pushed to this repo:
     - Bootstrap - 3.3.7
     - UnderscoreJS - 1.9.1
     - jQuery - 3.3.1
 

  ##### How to use:-
  - Clone this repo and make sure all prerequested packages are installed.
  - This application is build on python 3.6.3
  - Change username, password, databasename, database host and database port in `config.py`.
  - Open command promt/terminal and navigate to your cloned repo.
  - Run `python server.py --port=8888` `--port` is an optional command line argument to run application on a specific port, by default it will be `8888`.
  - Application's are logs will be stored in `output/output-log.log`.
    - Available URL patterns:
      - `/` - Home page/landing page.
      - `/crawl/` - REST API call to pull data from the source for each company. It will also do the initial database setup if required and then it will clean and put the data to database. All the `http requests` are be non blocking (`Async`).  
      - `/main/` - To see the output of tabular format of analysed data as per requirement.
      - `/insight/` - To get the analysed result as per requirement as a REST API call in JSON format. It will connect to the database and return the result ap per requirement in JSON format.
  - Open `http://127.0.0.1:8888` where `8888` is the port number given by command line argument in browser.
  - After navigating to `http://127.0.0.1:8888` please follow the instructions available on the web page.
