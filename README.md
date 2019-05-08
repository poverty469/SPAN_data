# SPAN_data
## PayDay_Locations
Webscraped data from the payday lender website and converted the data from a list to a dataframe which contains three different columns:
- Lender name
- Address

## Clean_scraped_data
Remove any data attached to the address like the telephone or was not matched by the regular expression. Then, with the clean address we would be locating the Longitude and Latitude from (gps-coordinates)[https://gps-coordinates.org/]. This process is automated so that the user does not need to find each address's geolocation one by one. 

## Process Tools
Import these packages to webscrape:
- BeautifulSoup
- Pandas
- requests
- Selenium
- Chromium: webdriver for chrome
- time: time delays
- re: regular expressions

## Steps to Automate
1. Install Selenium: <either one>
    - pip install selenium
    - conda install selenium 
2. Install (Chromium)[http://chromedriver.chromium.org/downloads] or if you have (HomeBrew)[https://docs.brew.sh/Installation] use command:
    brew cask install chromedriver

3. Import Selenium to python file and you can start