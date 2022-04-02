import json
import datetime
import logging
import threading
import time
import os
from queue import Queue
from bs4 import BeautifulSoup
import re
import concurrent.futures

from constants import *
from page_urls import get_number_of_pages_from_soup
from utility_funcs import get_request, save_movie_file,save_user_file,make_dir_if_not_exist
from utility_funcs import make_file_name

def download_user(username,url):
    files_to_save = {}

    make_dir_if_not_exist(USER_FOLDER)

    # check if its already there
    if username in os.listdir(USER_FOLDER):
        return (url,True)

    page = get_request(url)
    if isinstance(page, Exception):
        logging.error(f'Error fetching page {url}, {page}')
        return (url, False)
    else:
        soup = BeautifulSoup(page.content,features='html.parser')
        pages = int(get_number_of_pages_from_soup(soup))

        # save the first page
        file_name = make_file_name(username, 0,False,True)
        files_to_save[file_name]=page

        for i in range(pages):
            # save subsequent pages
            params = {"page": str(i + 1)}
            subpage = get_request(url, params)

            if isinstance(subpage, Exception):
                logging.error(f'Error fetching page {url}, {page}')
                return (url, False)
            else:
                file_name = make_file_name(username, i + 1)
                files_to_save[file_name] = subpage

        # save all the files
        for file_name, page in files_to_save.items():
            save_user_file(file_name, username, page)
        return (url,True)

def download_all_users(max_workers=16):
    with open('all_usernames_and_links.json', 'r') as f:
        users = json.load(f)

    users_downloaded = set(os.listdir(USER_FOLDER))
    users_with_url = {user:url for user,url in users.items() if url is not None and user not in users_downloaded}
    downloaded_dict = {url:False for url in users_with_url.values()}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(download_user,username,f"https://www.metacritic.com{url}") for username,url in users_with_url.items()]
        for f in concurrent.futures.as_completed(futures):
            resulturl,result = f.result()
            downloaded_dict[resulturl.replace("https://www.metacritic.com","")] = result
            print(f'{resulturl.replace("https://www.metacritic.com","")}:{result} ({len([item for item in downloaded_dict.values() if item])}/{len(downloaded_dict)})')

    pool.shutdown(wait=True)

def get_users_from_file(filepath):
    '''Finds all the users in the given html file and returns them in the format for {username:link to profile}'''
    users_dict = {}

    with open(filepath, 'r') as page:
        soup = BeautifulSoup(page, features='html.parser')
        users = [user for user in soup.select('.author')]

        for user in users:
            username = user.text
            try:
                link = user.find('a').attrs['href']
            except KeyError:
                link = None
            except AttributeError:
                link = None
            users_dict[username] = link
    return users_dict

def extract_all_users_from_all_reviews(num_workers=20):
    '''Visits all the folder in the movies data folder and finds all the users and their links'''

    folders = os.walk(MOVIES_FOLDER)
    paths_to_check = []
    user_dict = {}

    # get paths for all the paths to check
    for folder,subfolders, files in folders:

        paths = [os.path.join(folder,file) for file in files if 'main_page' not in file]
        paths_to_check.extend(paths)
        print(f'{folder}: {len(paths_to_check)}')
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as pool:
        futures = [pool.submit(get_users_from_file,path) for path in paths_to_check]

        for f in concurrent.futures.as_completed(futures):
            result = f.result()
            user_dict.update(result)
            print(f'{result}, {len(user_dict)}')


    with open('all_usernames_and_links.json','w') as f:
        json.dump(user_dict,f)


    print('Done')

def download_failed(path):
    '''takes the path to a log file as input, extract urls from that log file and downloads all'''
    urls = []
    url_pat = re.compile('(https?:\/\/www\.metacritic\.com\/movie\/[\w\-]+)')
    with open(path,'r') as file:
        for line in file:
            urls.append(  re.findall(url_pat,line)[0]  )

    movie_queue = Queue()

    for u in urls:
        movie_queue.put(u)

    workers = [    threading.Thread(target=save_all_subpages_of_movie,args=[movie_queue]) for _ in range(10)    ]
    for w in workers:
        w.start()

def download_all(movies,log_file_name='main.log',max_workers=20):

    logging.basicConfig(format='%(asctime)s -%(funcName)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S',
                        level=logging.INFO, filename=log_file_name)

    movies = {key:f'https://www.metacritic.com{value}' for key,value in movies.items() if key not in os.listdir(MOVIES_FOLDER)}

    outcomes = {url:False for url in movies.values()}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(save_all_subpages_of_movie,url) for url in movies.values()]
        for f in concurrent.futures.as_completed(futures):
            url,outcome = f.result()
            outcomes[url]=outcome
            print(f'{url}:{outcome} --- {len([val for val in outcomes.values() if val is True])} / {len([val for val in outcomes.keys()])}')

def get_all_movies_urls_for_all_years():

    titles_and_urls= {}

    years= [year for year in range(1915,2020+1)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(get_all_movie_url_for_year,year) for year in years]

        for f in concurrent.futures.as_completed(futures):
            result = f.result()
            print(f'Got:({len(result.keys())}) {result}')
            titles_and_urls.update(result)

    with open('all_movies_with_titles_and_links_by_year.json','w') as f:
        json.dump(titles_and_urls,f)

def get_all_movie_url_for_year(year):

    movie_urls = {}

    url = all_movies_by_year
    params = {'year_selected':year,'sort':'desc'}

    page = get_request(url,params)

    # load the page with all movies in a year
    if not isinstance(page, Exception):
        soup = BeautifulSoup(page.content, features="html.parser")
        num_pages = int(get_number_of_pages_from_soup(soup))

        movie_tags = soup.select('a.title')
        for tag in movie_tags:
            title = tag.text.strip()
            u = tag.attrs['href']
            movie_urls[title]=u
        print(f'Got page {0} for year {year}')
        if num_pages == 0:
            return movie_urls
        else:
            for i in range(num_pages):
                params = {'year_selected':year,'sort':'desc','page':str(i+1)}
                page = get_request(url,params)
                soup = BeautifulSoup(page.content, features="html.parser")
                movie_tags = soup.select('a.title')
                for tag in movie_tags:
                    title = tag.text.strip()
                    u = tag.attrs['href']
                    movie_urls[title] = u
                print(f'Got page {i+1} for year {year}')

        return movie_urls

def crawl_year_page_and_put_movies_on_movie_queue(year_queue, movie_queue):
    '''pulls from the year queue and puts tasks on the movie queue'''
    for year in range(2020,1916,-1):
        get_all_movie_url_for_year(year)

        url = f'https://www.metacritic.com/browse/movies/score/metascore/year/filtered'
        page = get_request(url, params={"year_selected":year})

        # load the page with all movies in a year
        if not isinstance(page,Exception):
            soup = BeautifulSoup(page.content,features="html.parser")
            num_pages = get_number_of_pages_from_soup(soup)

            for i in range(int(num_pages)):
                #  all the ones on the first page no matter what
                movie_urls = soup.select('.title.numbered + a')

                with open('all_movie_urls.txt','a+') as file:
                    for url in movie_urls:
                        u = f"https://www.metacritic.com{url.attrs['href']}"
                        movie_queue.put(u)
                        file.write(u+"\n")
                print(f'Put {len(movie_urls)} urls on movie queue')
                if int(num_pages) == 0:
                    continue
                else:
                    # iterate over each in the year page
                    for year_page in range(1,int(num_pages)):
                        print(f'Accessing {year} page {year_page} Queue size {year_queue.qsize()}')
                        # iterate over each movie
                        url = f'https://www.metacritic.com/browse/movies/score/metascore/year/filtered?year_selected={year}&sort=desc&page={year_page}'
                        page = get_request(url, params=None)

                        if not isinstance(page,Exception):
                            soup = BeautifulSoup(page.content, features="html.parser")

                            movie_urls = soup.select('.title.numbered + a')
                            for url in movie_urls:
                                u = f"https://www.metacritic.com{url.attrs['href']}"
                                movie_queue.put(u)
                            print(f'Put {len(movie_urls)} urls on movie queue')
                        else:
                            logging.error(f'Could not get page {year_page} of {year}')

    print(f'Stopping: Added all movies to queue')

def save_all_subpages_of_movie(url):
    '''Takes the URL to a movies page as input, saves the main page and every subpage of the user review section'''
    # visit the first movie on the page and load it.
    print(f'Accessing url {url}')
    files_to_save = {}
    # get the first page
    page = get_request(url)
    if not isinstance(page,Exception):
        soup = BeautifulSoup(page.content, features='html.parser')
        movie_title = soup.select('.product_page_title h1')[0].text
        file_name = make_file_name(movie_title, '0', True, True)
        actual_url = page.url
        # save main page
        files_to_save[file_name]=page

        usr_review_url = f'{actual_url}/user-reviews'
        # then visit the user-reviews section
        subpage = get_request(usr_review_url, params={"sort-by":"date"})
        if not isinstance(subpage,Exception):
            sub_soup = BeautifulSoup(subpage.content, features='html.parser')

            num_pages = int(get_number_of_pages_from_soup(sub_soup))

            file_name = make_file_name(movie_title, 0)
            # save first review page
            files_to_save[file_name] = subpage

            for i in range(num_pages):
                # save subsequent pages
                params = {"sort-by":"date","page":str(i+1)}
                subpage = get_request(usr_review_url,params)
                file_name = make_file_name(movie_title, i+1)
                files_to_save[file_name] = subpage

            # save all the files
            for file_name,page in files_to_save.items():
                save_movie_file(file_name, movie_title, page)

            return (url,True)
        else:
            logging.error(f'Error fetching page {url}, {page}')
            return (url,False)
    else:
        logging.error(f'Error fetching page {url}, {page}')
        return (url,False)

if __name__ == '__main__':

    pass
    download_all_users()

    # #download_all(movies)