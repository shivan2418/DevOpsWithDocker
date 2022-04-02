import requests
from requests.exceptions import ConnectionError
import time
import logging
from bs4 import BeautifulSoup
from utility_funcs import get_request
from constants import all_games_by_date,all_movies_by_date,all_games_base_url
from constants import header
from constants import params as imported_params
def make_url(url, page_num):
    return f'{url}?page={page_num}'

def get_number_of_pages_from_soup(soup):
       # check if there is even a navbar, if not there is only one page
    if soup.select('.page_nav') == []:
        return '0'
    else:
        # select the number of the last page
        last_page_num = soup.select('ul li.page.last_page a')[0].text
        return last_page_num

def get_number_of_pages(url):
    completed = False

    while not completed:
        try:
            page = requests.get(url, headers=header)
            completed=True
        except ConnectionError:
            time.sleep(5)
            print('Connection error, sleeping for 5')
        except Exception as e:
            logging.error(e)
            print(e)

    soup = BeautifulSoup(page.content, features="html.parser")

 # check if there is even a navbar, if not there is only one page
    if soup.select('.page_nav') == []:
        return '0'
    else:
        # select the number of the last page
        last_page_num = soup.select('ul li.page.last_page a')[0].text
        return last_page_num

def get_page_links(url,params=None):
    '''takes the url of a base url as input and returns a list of all the links'''
    # example https://www.metacritic.com/movie/star-wars-episode-viii---the-last-jedi/user-reviews?sort-by=date&num_items=100&page=0

    # get the page, this may return an error
    page = get_request(url)


    # if it is not an error
    if not isinstance(page,Exception):
        soup = BeautifulSoup(page.content,features="html.parser")

        # set the url to the url we acutally landed on
        url = page.url

        # check if there is even a navbar, if not there is only one page
        if soup.select('.page_nav') == []:
            return [url]
        else:
            # select the number of the last page
            last_page_num = soup.select('ul li.page.last_page a')[0].text
            urls = [make_url(url, page) for page in range(0, int(last_page_num))]

        return urls

    elif isinstance(page,Exception):
        logging.error(f'{url}: {page}')
        return page


if __name__ == '__main__':
    a=get_page_links('https://www.metacritic.com/movie/star-wars-episode-viii---the-last-jedi/user-reviews',params=imported_params)
    print(a)