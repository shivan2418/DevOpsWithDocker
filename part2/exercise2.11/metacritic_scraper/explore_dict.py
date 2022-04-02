import json


with open('all_movies_with_titles_and_links_by_year.json','r') as file:
    content = file.read()

    dct = json.loads(content)


    print(dct)