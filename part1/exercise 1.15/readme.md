# Exercise 15

For my own dockerized project I will submit a fork of the New York Times ingredients
tagger. I made many improvements to the original code and made it much easier to use.


## DockerHub Repo
https://hub.docker.com/repository/docker/shivan2418/cdownloader

## Github Repo
https://github.com/shivan2418/ingredient-phrase-tagger


### Below is a copy of the Github repository's readme.md, it contains all instructions need to run and pull the image.

# Plug and play phrase-tagger


## About
This is an improvement of the [CRF Ingredient Phrase Tagger](https://github.com/mtlynch/ingredient-phrase-tagger) by [Michael Lynch](https://github.com/mtlynch)

While Michael made several improvements over the original [NY Times ingredient-phrase-tagger](https://github.com/NYTimes/ingredient-phrase-tagger)
it was still far from plug and play.

## Improvements
* Comes with a model pre-trained and included.
* Can read from files which is much more useful than piping input through bash.



The app reads and converts every file in the input folder and places the parsed copy in the output folder.
All the included presents (see below) will use `input` and `ouput` folders in the current directory unless other arguments are passed. The image will create thes folders if they do not exist.


## Running the image
The image is avilable at `pull shivan2418/cdownloader:tagname`

You can run the image in 3 ways:

##### Docker-compose
If you just want to parse some files you can run

* ```docker-compose run --rm parser```

This pulls the image from my docker repo, run with default settings: directories named `input` and `output` in the same directory.

##### Docker-run
Run the image directly from docker hub, you do not even need to download this github repo for this work. 
The below command will again use `input` and `output` folder in the current directory. Change the paths to adjust the input and output folderss.
* `docker run --rm -v "$(pwd)"/output:/app/output -v "$(pwd)"/input:/app/input shivan2418/main_repo:iparser`

##### Build locally and run
If you want maximum control you can build the image locally and then run it.  
* ```docker build -t iparser .```

* ```docker run --rm -v "$(pwd)"/output:/app/output -v "$(pwd)"/input:/app/input iparser```


#### Known issues
On Linux, all the files that you create will be owned by the root. You should run `sudo chown -R -c youruser:youruser output` after running the image to get ownership of the files. 
 
#### Ingredient format
Each input must be a json file in the form of a list of strings as if you `json.dump` as list of strings in python.

sample_recipe.json
    
`["1 (8 ounce) package cream cheese, softened", "3 cups salsa, divided", "4 green onions, chopped, divided", "2 ½ cups Cheddar cheese, divided", "2 ½ cups shredded Monterey Jack cheese, divided", "12 (8 inch) flour tortillas", "1 cup peanut butter", "1 cup white sugar", "1 egg", "1 cup butter flavored shortening", "¾ cup white sugar", "¾ cup brown sugar", "2 eggs", "2 teaspoons Mexican vanilla extract", "2 ¼ cups all-purpose flour", "1 teaspoon baking soda", "1 teaspoon salt", "2 cups milk chocolate chips", "3 tablespoons apricot preserves", "1 teaspoon fresh ginger paste (such as Gourmet Garden™)", "½ teaspoon minced fresh rosemary", "2 (8 ounce) boneless, skinless chicken breasts", "1 teaspoon vegetable oil", "salt and ground black pepper to taste", "½ cup mayonnaise", "2 tablespoons Sriracha sauce", "1 pound bay scallops (about 36 small scallops)", "1 pinch coarse salt", "1 pinch freshly cracked black pepper", "12 slices bacon, cut into thirds", "1  serving olive oil cooking spray", "2 large russet potatoes, scrubbed", "1 tablespoon peanut oil", "½ teaspoon coarse sea salt", "cooking spray", "½ cup all-purpose flour", "¼ cup white sugar", "⅛ cup water", "1 large egg, separated", "1 ½ teaspoons melted butter", "½ teaspoon baking powder", "½ teaspoon vanilla extract", "1 pinch salt", "2 tablespoons confectioners' sugar, or to taste", "1 red grapefruit, refrigerated", "1 tablespoon softened butter", "1 tablespoon brown sugar", "2 teaspoons brown sugar", "aluminum foil", "½ teaspoon ground cinnamon", "2 tablespoons coarsely chopped pecans", "1 tablespoon brown sugar", "1 teaspoon all-purpose flour", "¼ teaspoon apple pie spice", "2 medium apples, cored and cut into wedges", "1 tablespoon butter, melted"]`




