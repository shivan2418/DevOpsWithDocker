import os
import threading
from queue import Queue
import logging
import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
from page_urls import get_page_links,get_number_of_pages
from constants import all_movies_by_year,header
import re
import json
params = {'year_selected':2018, 'sort':'desc'}
import time
import random
from threading import Lock,Thread

logging.basicConfig(format='%(asctime)s -%(funcName)s - %(levelname)s - %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S',
                            level=logging.INFO, filename="log_file.log")

extract_year_from_url = re.compile('year_selected=(\d{4})')

def get_year(url):
    return extract_year_from_url.findall(url)[0]

def get_links_for_all_movies_by_year(year):
    '''gets the links to all movies in a given year'''

    params =  {'year_selected':year, 'sort':'desc'}

    num_pages = get_number_of_pages(f'{all_movies_by_year}/filtered?year_selected={year}')

    if num_pages == '0':
        return [f'{all_movies_by_year}/filtered?year_selected={year}&sort=desc&page={0}']
    else:
        links = [f'{all_movies_by_year}/filtered?year_selected={year}&sort=desc&page={i}' for i in range(0,int(num_pages))]

    return links

def get_links_to_all_movies_on_page(page_url):
    '''takes the url of a to a page with movies as input, returns a list of with urls to all the movies that appear in the page'''
    try:
        page = requests.get(page_url,headers=header)
    except ConnectionError:
        print('Connection error, trying again in 10')
        time.sleep(10)
        return get_links_to_all_movies_on_page(page_url)

    except Exception as e:
        logging.error(e)


    soup = BeautifulSoup(page.content,features="html.parser")

    movie_tags = soup.select('span.title.numbered + a.title')
    movie_links = [link.attrs['href'] for link in movie_tags]
    movie_links = [f'https://www.metacritic.com/movie{link}' for link in movie_links]

    return movie_links



def get_link_for_all_movies_in_single_year(task_queue, write_queue):
    '''takes a list of urls as input, find all the movies in those urls and puts that result (a dict) on queue'''
    tmp_dict = {}

    while not task_queue.empty():
        url = task_queue.get()
        year = get_year(url[0])

        for link in url:


            print(f' ({year}) Getting url {link}')
            time.sleep(random.uniform(0.5,1))

            completed = False

            while not completed:
                try:
                    page = requests.get(link,headers=header)
                    soup = BeautifulSoup(page.content, features="html.parser")
                    movie_titles = [title.text for title in soup.select('span.title.numbered + a h3')]
                    movie_tags = soup.select('span.title.numbered + a.title')
                    movie_links = [link.attrs['href'] for link in movie_tags]
                    movie_name_and_link = {name: f'https://www.metacritic.com{link}' for name, link in
                                           zip(movie_titles, movie_links)}
                    tmp_dict.update({year:movie_name_and_link})
                    time.sleep(random.uniform(1, 2))
                    completed = True

                except ConnectionError:
                    print('Connection error, retrying in 10 seconds')
                    time.sleep(10)

                except Exception as e:
                    logging.error(f'Was unable to download {link}, ({e})')
                    break
        task_queue.task_done()

        write_queue.put(tmp_dict)
        tmp_dict = {}

    print(f'{threading.currentThread().name}: Stopping due to empty queue')

def make_dict_of_links_to_all_movies_by_year(num_workers):
    '''Use workers to get all the movies and save it to a dict that links the movie name to the url to that movie'''
    task_queue = Queue()
    write_queue = Queue()
    write_queue.downloads_complete = False

    # get all the links to all the movies
    with open('links_for_all_movies_by_year.txt', 'r') as file:
        content = file.read()
        content = content.split('\n')

    # put urls for all the different pages in all years into the task queue
    unique_years = list(set([get_year(link) for link in content]))
    for year in unique_years:
        task_queue.put([item for item in content if get_year(item) == year])


    # make a writer queue thread
    writer_thread = Thread(target=write_dict_of_links_to_file,args=[write_queue])
    writer_thread.start()
    # iterate over each link
    for i in range(num_workers):
        workers = [threading.Thread(name=str(i),target=get_link_for_all_movies_in_single_year,args=[task_queue,write_queue]) for i in range(num_workers)]
        for w in workers:
            w.start()
        for w in workers:
            w.join()

    write_queue.downloads_complete = True

def write_dict_of_links_to_file(queue):
    '''Takes a queue as input and continuelesly updates the .json files'''
    FILENAME = 'all_movies_with_titles_and_links_by_year.json'


    if not os.path.isfile(FILENAME):
        with open(FILENAME,'w+') as file:
            pass

    while True and not queue.downloads_complete:
        if queue.empty():
            time.sleep(0.5)
        else:
            output = queue.get()
            with open(FILENAME, 'r+') as file:
                content = file.read()
                if content == '':
                    json_dict = output
                    file.write(json.dumps(json_dict))
                else:
                    try:
                        json_dict = json.loads(content)
                        json_dict.update(output)
                        with open(FILENAME, 'w+') as file2:
                            print(f'Updated dict with {output}')
                            file2.write(json.dumps(json_dict))

                    except json.JSONDecodeError as e:
                        print(e)

    print('Stopping writer queue thread')




def get_link_of_failed_download(task_queue,write_queue):

    while not task_queue.empty():
        time.sleep(random.uniform(0.5,1))
        failed_url = task_queue.get()
        print(f'Trying to fix {failed_url}')
        try:
            page = requests.get(failed_url, headers=header, allow_redirects=True)
            print(f'{failed_url} ::   {page.status_code}')

            # check if the page was moved
            if 301 in [item.status_code for item in page.history]:
                print(f'{failed_url} has moved')
                real_url = page.url.split('movie_title=')[-1]
                real_url = f'https://www.metacritic.com/movie/{real_url}'
                time.sleep(random.uniform(0.5, 1))
                real_page = requests.get(real_url, headers=header, allow_redirects=True)
                if real_page.status_code == 200:
                    soup = BeautifulSoup(real_page.content, features="html.parser")
                    product_title = soup.select('.product_page_title h1')[0].text.strip()
                    year = soup.select('h1 + .release_year')[0].text.strip()

                    # send the answer to the write queue
                    write_queue.put( (year,product_title,real_page.url)   )
                    print(f'Fix {product_title}s url to {real_page.url}')

                else:
                    print(f'Failed to get {real_url} ({real_page.status_code})')

            else:
                print(f'{failed_url} has not moved {page.status_code}')


        except Exception as e:
            print(f'Could not access {failed_url}: {e}')

    print('Stopping due to empty task queue')

def write_fixed_links(task_queue,write_queue):


    while task_queue.done is False:

        while not write_queue.empty():
            year,product_title,fixed_link = write_queue.get()

            # open up the json links file and read into memory
            with open('all_movies_with_titles_and_links_by_year.json', 'r') as jsonfile:
                all_movies_dict = json.loads(jsonfile.read())
                all_movies_dict[year][product_title] = fixed_link

            # overwrite the file
            with open('all_movies_with_titles_and_links_by_year.json', 'w') as jsonfile:
                jsonfile.write(json.dumps(all_movies_dict))

        print('No fixed urls to write, sleeping for 5 secs')
        time.sleep(5)

    print('All tasks done, shutting down write queue')


def get_real_links_of_failed_downloads(num_workers):

    write_queue = Queue()
    task_queue = Queue()
    task_queue.done = False

    # all the tasks to the  task queue
    with open('failed_raw_downloads.txt','r') as file:
        for line in file:
            link,error = line.split(',')
            task_queue.put(link)

    # start the workers
    workers = []
    for i in range(num_workers):
        workers.append(threading.Thread(target=get_link_of_failed_download,args=[task_queue,write_queue]))

    for w in workers:
        w.start()
    for w in workers:
        w.join()


    print('All workers finished their jobs')
    task_queue.done = True


if __name__ == '__main__':

    get_real_links_of_failed_downloads(5)

    #make_dict_of_links_to_all_movies_by_year(num_workers=20)
