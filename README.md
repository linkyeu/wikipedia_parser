# Parser for wikiperdia.org 
__Currently this version supports only russian languge wikipedia.__
I wrote this parser as part of my Career Guidence pet-project to collect open source data (wikipedia.org in this particular case).
This parser designed in way that anyone be able to extend it functionality by redefining `parse_func` method. More detailes in the following description. </br>

Parser works with wikipedia categories pages. If you interseted in data about `famous teachers` you are googling `wiki science teachers category` after that google will return you a link to this [category](https://en.wikipedia.org/wiki/Category:Science_teachers). Usually it contains alphabetic list of all profiles of persons within this category. Using this parser tou can parse any data you need from these profiles.

### Use case - parsing birth days of serial killers
1) Get url for category page with structure `https://en.wikipedia.org/wiki/Category:x...x`. </br>
Such urls means that page contains profiles with persons from some category. To get this url you can just google something like `вики категория серийные убийцы` and google gives you `https://en.wikipedia.org/wiki/Category:Serial_killers`. 
2) Define a `parse_func`. This is a empty method in base parser class which should be defined by user. It is defines what data should be parsed from a single personal profile. _TODO: pre-define several default `parse_func` so user can use them by default._
Here is an example of such function for parsing birth days from a person profile. Parser uses multiprocessing so it is important that types of outputs from a function should be defined directly in the function. 

```
def parse_bday(x: tuple):
    """Returns name and birth day of a person derived from wiki's preson profile page.
    
    Args:
        x (str): url to personal profile of a person on wikipedia
    """
    name, url = x  # unpack tuple
    html = BeautifulSoup(urllib.request.urlopen(url), 'lxml')
    try:
        bday = html.find_all('span', {'class' : 'bday'})
        bday = BeautifulSoup(str(bday), 'lxml')
        bday = bday.span.string
    # handle case when bday is unavailable
    except AttributeError: 
        bday = None
    # for multiprocessing is very important to directly define type of output vars
    return str(name), str(bday) 
```
__Explanation:__ As you can see the function takes a tuple with predefined structure as input argument. The tuple has a following structure `('Иван Иванов', 'url to his wikipedia profile')`. The purpose of this function is to define how to parse required by user data from personal page. 

3) Run parser. Parser will take defined `parse_func` and using multiprocessing will parse data from each profile in category and save resulting csv file 
Google phrase - `вики категория актеры` and get `url` for this category. 




