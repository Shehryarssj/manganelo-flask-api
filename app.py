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
    top_weekly = []
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}
    url = 'https://manganelo.com/'
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')

    #Updates
    content_divs = soup.find_all('div', {'class': 'content-homepage-item'})
    for div in content_divs[:25]:
    	manga_url = div.find('a')['href'].strip()
    	title = div.find('img')['alt'].strip()
    	image = div.find('img')['src'].strip()
    	latest_chapter_para_tag = div.find('p', {'class': 'a-h item-chapter'})
    	try:
    		latest_chapter_link = latest_chapter_para_tag.find('a')['href'].strip()
    		latest_chapter = latest_chapter_link.split('_')[-1]
    		manga = {'title': title, 'image': image, 'latest_chapter': latest_chapter,'latest_chapter_link': latest_chapter_link, 'manga_url': manga_url}
    		mangas.append(manga)
    	except:
    		pass

    #Top Weekly
    top_weekly_manga_div = soup.find('div',{'class':'owl-carousel'})
    top_weekly_mnangas = soup.find_all('div',{'class':'item'})
    for div in top_weekly_mnangas:
    	try:
    		image_tag = div.find('img')
    		image = image_tag['src']
    		title = image_tag['alt']
    		anchor_tags = div.find_all('a')
    		manga_url = anchor_tags[0]['href']
    		latest_chapter_link = anchor_tags[1]['href'].strip()
    		latest_chapter = latest_chapter_link.split('_')[-1]
    		manga = {'title': title, 'image': image, 'latest_chapter': latest_chapter,'latest_chapter_link': latest_chapter_link, 'manga_url': manga_url}
    		top_weekly.append(manga)
    	except:
    		pass

    result = {'result':{'updates':mangas, 'top_weekly':top_weekly}}
    return result

@app.route('/get_total_search_result_pages')
def get_total_search_result_pages():
	max_pages = None
	result = {}
	query = request.args.get('query')
	l = query.split(' ')
	seperator = '_'
	query = seperator.join(l)
	headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}
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
    argument = request.args.get('arg')
    query,page_no = argument.split(',')
    l = query.split(' ')
    seperator = '_'
    query = seperator.join(l)
    
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
            try:
            	latest_chapter_div = manga_div.find('div', {'class': 'item-right'})
            	latest_chapter_link = latest_chapter_div.find('a',{'class':'item-chapter a-h text-nowrap'})['href']
            	latest_chapter = latest_chapter_link.split('_')[-1]
            	manga_url = manga_div.find('a')['href']
            	manga = {'manga_img': manga_img, 'manga_title': manga_title, 'manga_url': manga_url, 'latest_chapter':latest_chapter, 'latest_chapter_link':latest_chapter_link}
            	results.append(manga)
            except:
            	pass

    return {'result':results}


@app.route('/get_manga_info')
def get_manga_info():
	url = request.args.get('url')
	authors = []
	genres = []
	chapters = []
	headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}
	res = requests.get(url, headers=headers)
	soup = BeautifulSoup(res.text, 'lxml')

	#getting manga image url and title
	manga_info_div = soup.find_all('div', {'class': 'story-info-right'})[0]
	manga_name = manga_info_div.find('h1').text
	manga_image_div = soup.find('div', {'class': 'story-info-left'})
	manga_image = manga_image_div.find('img')['src']

	li = soup.findAll('li', {'class': 'a-h'})

	#getting latest updated time
	try:
		last_updated = li[0].find('span',{'class':'chapter-time text-nowrap'}).text
		print(last_updated)
	except Exception as e:
		last_updated = ''
		pass

	#getting all chapter urls
	for item in li:
		anchor_tag = item.find('a')
		chapters.append(anchor_tag['href'])

	#div containing author status and genre info
	author_status_genre = manga_info_div.find_all('tr')

	if len(author_status_genre)==4:
		i = 1
	else:
		i = 0

	#getting all author names
	author_anchor_tags = author_status_genre[i].find_all('a')
	for tag in author_anchor_tags:
		authors.append(tag.text)
	i+=1

	#getting manga status
	status = author_status_genre[i].find('td',{'class':'table-value'}).text
	i+=1

	#getting all genres
	genre_anchor_tags = author_status_genre[i].find_all('a')
	for tag in genre_anchor_tags:
		genres.append(tag.text)

	#getting description
	description = soup.find('div',{'class':'panel-story-info-description'}).text.strip()
	description = description.split('\n')
	description = ''.join(description[1:])

	manga_info = {'manga_name':manga_name,'manga_image':manga_image,'authors':authors,'status':status,'genres':genres,'chapters':chapters,'description':description,'last_updated':last_updated}
	return manga_info

@app.route('/get_total_genre_search_result_pages')
def get_total_genre_search_result_pages():
	argument = request.args.get('arg')
	selected,excluded = argument.split(',')

	result = {}
	selected_query = ''
	excluded_query = ''
	max_pages = None
	if len(selected) != 0:
		selected_query = '&g_i=' + selected
	if len(excluded) != 0:
		excluded_query = '&g_e=' + excluded
	url = "https://manganelo.com/advanced_search?s=all" + selected_query + excluded_query + "&orby=topview"
	headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}
	res = requests.get(url, headers=headers)
	soup = BeautifulSoup(res.text, 'lxml')

	try:
		page_buttons_div = soup.find('div',{'class':'group-page'})
		anchor_tags = page_buttons_div.find_all('a')
		last_page_text = anchor_tags[-1].text
		max_pages = last_page_text[5:].strip(')')
	except:
		manga_panel_div = soup.find('div',{'class':'panel-content-genres'})
		if manga_panel_div != None:
			max_pages = '1'
		else:
			max_pages = '0'
		pass

	result['max_pages'] = max_pages
	return result

@app.route('/get_genre_search_results')
def get_genre_search_results():
	argument = request.args.get('arg')
	selected,excluded, page_no = argument.split(',')

	result = {}
	mangas = []
	selected_query = ''
	excluded_query = ''
	if len(selected) != 0:
		selected_query = '&g_i=' + selected
	if len(excluded) != 0:
		excluded_query = '&g_e=' + excluded
	url = "https://manganelo.com/advanced_search?s=all" + selected_query + excluded_query + "&orby=topview" + "&page=" + page_no
	headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'}
	res = requests.get(url, headers=headers)
	soup = BeautifulSoup(res.text, 'lxml')

	manga_panel_div = soup.find('div',{'class':'panel-content-genres'})
	manga_divs = manga_panel_div.find_all('div',{'class':'content-genres-item'})

	for div in manga_divs:
		try:
			manga_url = div.find('a',{'class':'genres-item-img'})['href']
			image_div = div.find('img')
			image_url = image_div['src']
			title = image_div['alt']
			latest_chapter_div = div.find('a',{'class':'genres-item-chap text-nowrap a-h'})
			latest_chapter_url = latest_chapter_div['href']
			latest_chapter = latest_chapter_url.split('_')[-1]
			manga = {'title': title, 'image': image_url, 'latest_chapter': latest_chapter,'latest_chapter_link': latest_chapter_url, 'manga_url': manga_url}
			mangas.append(manga)

		except:
			pass

	result['mangas'] = mangas
	return result
