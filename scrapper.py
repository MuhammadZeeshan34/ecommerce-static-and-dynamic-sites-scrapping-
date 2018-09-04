import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import urllib
import math
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located)
from selenium.webdriver.support.wait import WebDriverWait

def isproperprice(value):
	m = re.search(r'[a-z]',str(value))
	if m:
		return False
	return True

def Scrapper(url):
	"""
	Scrapper class to parse data from given url
	"""
	if 'aminoz' in url:

		driver = webdriver.Chrome(r"/Users/zeeshannawaz/Downloads/chromedriver")

		project_dir = "/Users/zeeshannawaz/UpWork/Scrapping/~01f6cd53dbb163a72a - Data Collection from EComerece Stores/aminoz/"
		excel_file = open(os.path.join(project_dir, 'data.csv'), 'a')

		total_items = 2607
		page_limit = 64

		pages = math.ceil(total_items / 64)
		start_page = 23
		for page_count in range(start_page,24):

			sub_url = os.path.join(url,'products.html','?limit='+str(page_limit)+'&p='+str(page_count))
			print(sub_url)
			response = requests.get(sub_url)
			soup = BeautifulSoup(response.text, 'html.parser')

			# Check total number of products and divide total number by 64 and add ?limit=64 and for each page add
			# &p=1 2 3 4 5
			# With every product add ?limit=64 and if products = 64 then add &p=2
			count = 1
			selector = 'div > h3 > a'
			prod_tags = soup.select(selector)
			#prod_tags = soup.find_all('div',"wrapper-hover")

			for prod_tag in prod_tags:
				print(count)
				count += 1
				if count < 54:
					continue
				#title = prod_tag.text
				#print("Title : ", title)

				#if len(prod_tag.find_all('a')) > 0:
				if 0==0:
					#prod_url = prod_tag.find_all('a')[0]['href']
					prod_url = prod_tag['href']
					# Open the product url and get the response and url
					response = requests.get(prod_url)
					if not 'This product is currently unavailable' in response.text:
						soup = BeautifulSoup(response.text,'html.parser')
						title = str(soup.text).lstrip('\n').split('\n')[0]
						size_and_price = ''
						category = ''
					#	print("Title : ",title)
						# Get the categories (Top level and second level)


						cat_tags = soup.find_all('div','breadcrumbs')
						for cat_tag in cat_tags: # Just get the first one and break
							sub_cat_tags = cat_tag.find_all('ul')
							if len(sub_cat_tags) > 0:
							#	category = str(sub_cat_tags[-1].text.split('\n\n\n')[3].lstrip()).strip() + ' - ' + str(sub_cat_tags[-1].text.split('\n\n\n')[5].lstrip()).strip()
								category = [x for x in sub_cat_tags[-1].text.split('\n') if x != '' and x != ' > ']
								if len(category) > 3:
									category = str(category[1]).strip(' ') + ' - ' + str(category[2]).strip(' ')
								else:
									category = str(category[0]).strip(' ')



						#	print("Category: " ,category)
							break

						description = ''
						desc_tags = soup.find_all('div','std')
						if len(desc_tags) > 0:
							description = str(desc_tags[0].text).lstrip('\n').replace(',',' ').strip()



						driver.get(prod_url)

						average_price = 0
						sizes = []
						prices = []
						pic_urls = []
						if len(soup.find_all('span', 'regular-price')) > 0:
							average_price = soup.find_all('span', 'regular-price')[0].text[1:].lstrip('\n').strip('\n').strip(' ').strip('$')
						else:
							average_price = 0
						average_price = float(average_price)

					#	m = re.search(r'Standard Price\n.\d\d.\d\d\n', str(product_id.text))
				#		if m:
			#				average_price = float(m.group(0).strip('\n').split('\n')[1][1:])
						#el = driver.find_element_by_id('product-price-'+product_id)
					#	average_price = float(el.text[1:-1])

						#average_price = product_id.text.split('\n')[8][1:-1]

						#if isproperprice(average_price):
						#	average_price = float(average_price)
						el = driver.find_elements_by_id('attribute206')
						if len(el) < 1: # Single size available
							size_and_price = 'Average size - ' + str(average_price) + ' AUD :'
						else:
							for option in el[0].find_elements_by_tag_name('option'):

								if 'option' not in str(option.text) and 'Option' not in str(option.text):
									if len(option.text.split(' ')) == 1:
										sizes.append(option.text)
										prices.append(average_price)
									else:
										price_value = option.text.split(' ')
										if len(price_value) == 3:
											size_and_price = 'Average size - ' + str(average_price) + ' AUD :'
											break
										if isproperprice(price_value):
											sizes.append(option.text.split(' ')[0])
											if option.text.split(' ')[1][0] == '+':
												prices.append(float(average_price) + float(option.text.split(' ')[1][2:-1]))
											else:
												prices.append(abs(float(option.text.split(' ')[1][2:-1]) - float(average_price)))

							for (size,price) in zip(sizes,prices):
								size_and_price = size_and_price + str(size) + ' - ' + str(price) + ' AUD' + ' : '

							if size_and_price == '':
								size_and_price = str(average_price)

					#	print("Size and Price: ", size_and_price)

						pic_tags = soup.find_all('a','cloud-zoom-gallery')
						for pic_tag in pic_tags:
							pic_urls.append(pic_tag['data-image'])

						#count = 0
						for pic_url in set(pic_urls):
							if 'http' in pic_url:
								#count += 1
								req = Request(pic_url,
									headers={'User-Agent': 'Mozilla/5.0'})
								#filedata = Request(pic_url,)
								try:
									datatowrite = urlopen(req).read()
									prod_url = os.path.join(project_dir, title)
									if not os.path.exists(prod_url):
										os.makedirs(prod_url)
									with open(os.path.join(prod_url, 'pic' + str(count) + '.jpg'), 'wb') as f:
										f.write(datatowrite)
								except:
									break

						data = str(title) + ',' + str(description.replace('\n', ' ')) + ',' + str(
							category) + ',' + str(size_and_price) + '\n'
						excel_file.write(str(data))







	if 'adrenalinehq' in url:

		dict_ = {}

		project_dir = "/Users/zeeshannawaz/UpWork/Scrapping/~01f6cd53dbb163a72a - Data Collection from EComerece Stores/adrenalinehq/"
		excel_file = open(os.path.join(project_dir, 'data.csv'), 'w')

		response = requests.get(url)
		soup = BeautifulSoup(response.text, 'html.parser')
		cat_tags = soup.find_all('ul', 'mega-stack')
		for cat in cat_tags:
			tagss = cat.find_all('a')
			for tag in tagss:
				sub_url = url + tag['href']
				category = sub_url.split('/')[-1]
				# print(category)
				# print(sub_url)
				response = requests.get(sub_url)
				soup = BeautifulSoup(response.text, 'html.parser')
				#        print(soup.prettify())
				a_tags = soup.find_all('a')  # All links of categories
				for a_tag in set(a_tags):
					project_dir = "/Users/zeeshannawaz/UpWork/Scrapping/~01f6cd53dbb163a72a - Data Collection from EComerece Stores/adrenalinehq/"
					if 'products' in str(a_tag) and 'collections' in str(
							a_tag):  # Check all products in specific category


						description = ''
						price_and_size = ''
						product_url = url + a_tag['href']
						pic_urls = []
						# print(product_url)
						response = requests.get(product_url)  # Opening html page of actual product
						soup = BeautifulSoup(response.text, 'html.parser')

						# if len(soup.find_all('h2')) > 1:
						# 	title = soup.find_all('h2')[0].text
						# 	if len(soup.find_all('h1')) > 1:
						# 		title = soup.find_all('h2')[0].text + ' ' + soup.find_all('h1')[0].text
						# else:
						# 	if len(soup.find_all('h1')) > 1:
						# 		title = soup.find_all('h1')[0].text

						title = soup.title.text.strip().strip('Adrenaline HQ')[:-2]

						if title not in dict_.keys():
							dict_[title] = 0

							# Get desciption
							desc_tags = soup.find_all('div', 'rte')
							for desc_tag in desc_tags:
								description = max(desc_tag.text.split('\n'), key=len)
								break

							size_and_price = ''
							size_and_price_tags = soup.find_all('select')
							for size_and_price_tag in size_and_price_tags:
								sizes = size_and_price_tag.text.split('\n')
								sizes = [size for size in sizes if len(size) > 3]
								price_and_size = str(sizes).replace(',', ':').strip('\\')
								break

							if len(str(price_and_size)) < 5:
								single_price = soup.find('meta', property="og:price:amount")
								if single_price:
									price_and_size = single_price["content"]

							pic_tags = soup.find_all('img')
							for pic_tag in pic_tags:
								if '1496554830' not in str(pic_tag) and '1520348175' not in str(pic_tag) and \
												len(str(pic_tag)) > 2 and 'product' in str(pic_tag):  # Exclude common photos
									# print(pic_tag['src'])
									pic_urls.append(pic_tag['src'].lstrip('//'))
							count = 0
							for pic_url in set(pic_urls):
								count += 1
								if 'cdn.shopify' in pic_url:
									filedata = urllib.request.urlopen('https://' + pic_url)
									datatowrite = filedata.read()
									prod_url = os.path.join(project_dir, title)
									if not os.path.exists(prod_url):
										os.makedirs(prod_url)
									with open(os.path.join(prod_url, 'pic' + str(count) + '.jpg'), 'wb') as f:
										f.write(datatowrite)

							data = str(title) + ',' + str(description.replace(',', ' ').replace('\n', ' ')) + ',' + str(
								category) + ',' + str(price_and_size).replace(',', ':') + '\n'
							excel_file.write(str(data))




	if 'elitesupps' in url:


		project_dir = "/Users/zeeshannawaz/UpWork/Scrapping/~01f6cd53dbb163a72a - Data Collection from EComerece Stores/elitesupps/"
		excel_file = open(os.path.join(project_dir, 'data.csv'), 'w')
		df = pd.DataFrame(columns=['Name', 'Description', 'Size & Price', 'Category', 'Image URL'])

	# This url will list all categories, get the category url from xml and open it and all products links
		count = 1						# are given there, open them and get the required information.
		url_new = url + '/pages/categories'
		response = requests.get(url_new)
		soup = BeautifulSoup(response.text, 'html.parser')
		tags = soup.find_all('a')
		tag_count_check = -1
		for tag in tags:
			tag_count_check += 1
			if tag_count_check >= 8 and tag_count_check <= 32:
				tag_count_check += 1
				response = requests.get(url + tag['href'])
				soup = BeautifulSoup(response.text, 'html.parser')
				category = soup.title.string.strip().split('\n')[0]
				items_on_one_page = 21
				total_items = int(
					soup.find_all('div', 'grid__item two-thirds medium-down--text-right')[0].text.split(' ')[0])
				total_pages = math.ceil(total_items / items_on_one_page)
				for index in range(1, total_pages + 1):
					response = requests.get(url + tag['href'] + '?page=' + str(index))
					soup = BeautifulSoup(response.text, 'html.parser')
					product_tags = soup.find_all('div', 'grid__item wide--one-fifth one-third tablet-down--one-half eq_height')
					for s_tag in product_tags:
						s_tag = s_tag.find_all('a')[0]['href']

						response = requests.get(url + s_tag)
						soup = BeautifulSoup(response.text, 'html.parser')
						title = soup.title.string.split('\n')[5].strip()
						price = 0
						desc = ''
						size_and_price = ''
						pic_url = ''

					#	product_tags = soup.find_all('span')
					#	for p_tags in product_tags:
					#		if 'ProductPrice' in str(p_tags):
					#			price = p_tags['content']
					#			break
						product_tags = soup.find_all('div','short-description')
						for d_tags in product_tags:
							ss = d_tags.find_all('p')
							for s in ss:
								desc = s.text
								break


						product_tags = soup.find_all('span')  # General size
						for p_tags in product_tags:
							if 'ProductPrice' in str(p_tags):
								price = p_tags['content']
								break
						print(count)
						count += 1
						# Specified size
						size_tags = soup.find_all('div',' grid__item one-half small--one-whole options ')
						if len(size_tags) > 0:
							size_and_price = size_tags[0].text.strip().split('\n')
							size_and_price = [size_and_pric.strip() for size_and_pric in size_and_price if len(size_and_pric.strip()) > 5]
							new_size_and_prize = []
							for prod in size_and_price:
								if 'Sold' in prod:
									# Check for same sizes
									prod = str(prod).replace('Sold Out',price)
									new_size_and_prize.append(prod)
									size_and_price = new_size_and_prize




						pic_tags = soup.find_all('img',{'id' : 'ProductPhotoImg'})
						if len(pic_tags) > 0:
							pic_url = str(pic_tags[0]['src']).lstrip('//')




					#	print("Title", title)
				#		print("Description :", desc)
				#		print("Size and Price :", size_and_price)
				#		print("Price :", price)
				#		print("Picture :", pic_url)

						if len(str(size_and_price)) < 4:
							size_and_price = price

						temp_df = pd.DataFrame([title,desc,size_and_price,pic_url])
						df.append(temp_df)


						if 'cdn.shopify.com' in pic_url:
							filedata = urllib.request.urlopen('https://' + pic_url)
							datatowrite = filedata.read()


						prod_url = os.path.join(project_dir,title)
						if not os.path.exists(prod_url):
							os.makedirs(prod_url)


						with open(os.path.join(prod_url,'pic.jpg'),'wb') as f:
							f.write(datatowrite)

						data = str(title) + ',' + str(desc.replace(',',' ').replace('\n',' ')) + ',' +  str(category)   + ',' + str(size_and_price).replace(',',':') + '\n'
						excel_file.write(data)






					#print(soup.prettify())
				#print(url + tag['href'])
				#print(soup.prettify())
		#print(soup.prettify())
		
			

	print("Done")



def SaveDF(df, path):
	"""
	Saving specified dataframe in csv file given
	"""

	print("Done")

def get_sites_urls():
	urls = []
	urls.append('https://www.elitesupps.com.au')
	#urls.append('https://adrenalinehq.com.au/')
	#urls.append('https://www.aminoz.com.au/')
	return urls



if __name__ == "__main__":
	urls = get_sites_urls()

	dfs =  [Scrapper(url) for url in urls]
	filename = "./"
	[ SaveDF(df,filename) for df in dfs ]	
