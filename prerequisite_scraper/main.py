import requests
from bs4 import BeautifulSoup

data = requests.get('https://www.oxy.edu/academics/faculty/faculty-index')

soup = BeautifulSoup(data.text, 'lxml')

for i in soup.findAll('strong'):
    print(i)
