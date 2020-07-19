from flask import Flask,request
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route('/chapter_image_links')
def get_chapter_image_links():
    url = request.args.get('url')
    session = requests.Session()
    jar = requests.cookies.RequestsCookieJar()
    jar.set('content_server','server2')
    session.cookies = jar
    image_links = []
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}
    res = session.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')
    
    images_div = soup.find_all('div', {'class': 'container-chapter-reader'})
    image_tags = images_div[0].find_all('img')
    for image_tag in image_tags:
        image_links.append(image_tag['src'])
    result = {'image_links':image_links}
    return result

@app.route('/')
def get_main_page():
    mangas = []
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}
    url = 'https://manganelo.com/'
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')

    content_divs = soup.find_all('div', {'class': 'content-homepage-item'})

    for div in content_divs[0:20]:
        manga_url = div.find('a')['href'].strip()
        title = div.find('img')['alt'].strip()
        image = div.find('img')['src'].strip()
        latest_chapter_para_tag = div.find('p', {'class': 'a-h item-chapter'})
        latest_chapter_link = latest_chapter_para_tag.find('a')['href'].strip()
        latest_chapter = latest_chapter_link.split('_')[-1]

        manga = {'title': title, 'image': image, 'latest_chapter': latest_chapter,
                 'latest_chapter_link': latest_chapter_link, 'manga_url': manga_url}
        mangas.append(manga)

    result = {'result':mangas}
    return result

@app.route('/get_total_search_result_pages')
def get_total_search_result_pages():
    result = {}
    query = request.args.get('query')
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}
    url = f'https://manganelo.com/search/story/{query}'
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')

    max_pages_div = soup.find('div', {'class': 'group-page'})
    if (max_pages_div != None):
        max_pages_anchor_tag = max_pages_div.find_all('a')[-1]  # last anchor tag containing last page number
        max_pages = max_pages_anchor_tag['href'].split('=')[-1]  # extract number from link
    else:
        panel_search_story_div = soup.find('div',{'class':'panel-search-story'})
        if panel_search_story_div == None:
            max_pages = '0'
        else:
            max_pages = '1'
    result['maxpages'] = max_pages
    return result

@app.route('/get_search_results_for_page')
def get_search_results_for_page():
    search_result = {}
    argument = request.args.get('arg')
    query,page_no = argument.split(',')
    url = f'https://manganelo.com/search/story/{query}?page={page_no}'
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')

    search_panel_div = soup.find('div', {'class': 'panel-search-story'})
    results = []
    if search_panel_div != None:
        manga_items_div = search_panel_div.find_all('div', {'class': 'search-story-item'})
        for manga_div in manga_items_div:
            manga_img = manga_div.find('img')['src']
            manga_title = manga_div.find('a')['title']
            latest_chapter_div = manga_div.find('div', {'class': 'item-right'})
            latest_chapter_link = latest_chapter_div.find('a',{'class':'item-chapter a-h text-nowrap'})['href']
            latest_chapter = latest_chapter_link.split('_')[-1]
            manga_url = manga_div.find('a')['href']
            manga = {'manga_img': manga_img, 'manga_title': manga_title, 'manga_url': manga_url, 'latest_chapter':latest_chapter, 'latest_chapter_link':latest_chapter_link}
            results.append(manga)
    search_result['result'] = results
    return search_result


@app.route('/get_manga_info')
def get_manga_info():
    url = request.args.get('url')
    authors = []
    genres = []
    chapters = []
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')

    manga_info_div = soup.find_all('div', {'class': 'story-info-right'})[0]
    manga_name = manga_info_div.find('h1').text
    manga_image_div = soup.find('div', {'class': 'story-info-left'})
    manga_image = manga_image_div.find('img')['src']

    li = soup.findAll('li', {'class': 'a-h'})
    for item in li:
        anchor_tag = item.find('a')
        chapters.append(anchor_tag['href'])

    author_status_genre = manga_info_div.find_all('tr')

    if len(author_status_genre)==4:
    	i = 1
    else:
    	i = 0

    author_anchor_tags = author_status_genre[i].find_all('a')
    for tag in author_anchor_tags:
        authors.append(tag.text)
    i+=1
    status = author_status_genre[i].find('td',{'class':'table-value'}).text
    i+=1
    genre_anchor_tags = author_status_genre[i].find_all('a')
    for tag in genre_anchor_tags:
        genres.append(tag.text)

    manga_info = {'manga_name':manga_name,'manga_image':manga_image,'authors':authors,'status':status,'genres':genres,'chapters':chapters}
    return manga_info
