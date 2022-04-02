import requests
from constants import header
from bs4 import BeautifulSoup

print('Getting page')

url1= 'https://www.metacritic.com/movie/vampire'

soup = ''
try:
    page = requests.get(url='https://www.shivan.dk',headers=header,allow_redirects=True)
    print(page.status_code)
    soup = BeautifulSoup(page.content,features='html.parser')

    print(page.history)
    print(page.url)

except Exception as e:
    print(e)


print(soup)