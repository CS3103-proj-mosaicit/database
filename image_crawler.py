#!/usr/bin/python3

import requests
from requests.exceptions import Timeout # for request timeout
import re # for url extraction
from time import sleep # for request delay
from multiprocessing import cpu_count, Pool, TimeoutError # for parallel processing

import ImageDB

def init():
  db = ImageDB.db()
  db.init()
  db.close_connection()

# ignore warnings
import warnings
warnings.filterwarnings("ignore")

# number of processes for multiprocessing (using the number of CPUs in the system)
no_processes = cpu_count()


# function to convert keyword (e.g. red flower) to urls
def to_pixabay_url(keyword):

	base_url = "https://pixabay.com/images/search/"
	keyword = keyword.replace(' ', '%20')
	return base_url + keyword

def to_unsplash_url(keyword):

	base_url = "https://unsplash.com/s/photos/"
	keyword = keyword.replace(' ', '-')
	return base_url + keyword

def to_pexels_url(keyword):

	base_url = "https://www.pexels.com/search/"
	keyword = keyword.replace(' ', '%20')
	return base_url + keyword

# function to scrap image urls from pixabay
def scrape_pixabay(keyword):

	pattern = r'src="https://cdn.pixabay.com\S*"'
	url = to_pixabay_url(keyword)
	
	try:
		response = requests.get(url, timeout=(4, 5), verify=False)

	except Exception:
		print('The request time out or invalid url: ' + url)
		return []

	if response.status_code != 200:
		print("No result")
		return []

	content = response.content.decode('latin-1')
	
	urls = [match[5:-1] for match in re.findall(pattern, content)]

	return urls

# function to scrap image urls from unsplash
def scrape_unsplash(keyword):

	pattern = r'src="https://images.unsplash.com/photo\S*"'
	url = to_unsplash_url(keyword)
	
	try:
		response = requests.get(url, timeout=(4, 5), verify=False)

	except Exception:
		print('The request time out or invalid url: ' + url)
		return []

	if response.status_code != 200:
		print("No result")
		return []

	content = response.content.decode('latin-1')
	
	urls = [match[5:-1] for match in re.findall(pattern, content)]

	return urls

# function to scrap image urls from pexels
def scrape_pexels(keyword):

	pattern = r' src="https://images.pexels.com/photos\S*"'
	url = to_pexels_url(keyword)

	try:
		response = requests.get(url, timeout=(4, 5), verify=False)

	except Exception:
		print('The request time out or invalid url: ' + url)
		return []

	if response.status_code != 200:
		print("No result")
		return []

	content = response.content.decode('latin-1')
	
	urls = [match[6:-1] for match in re.findall(pattern, content)]

	return urls

#** function to retrieve all image urls
def get_image_urls(keyword):

	urls = list()
	urls += scrape_pixabay(keyword) + scrape_unsplash(keyword) + scrape_pexels(keyword)
	
	# remove any duplicated urls
	urls = list(set(urls))

	return urls

# function to return image as raw format
def raw_image(image_url):

	try:
		response = requests.get(image_url, timeout=(4, 5), verify=False)

	except Exception:
		print("Failed to save the image from url")
		print('The request time out or invalid url: ' + url)
		return None

	if response.status_code != 200:
		print("Invalid image url: " + image_url)
		return None

	return response.content

# function to save image from url as file_name
def save_image(file_name, image_url):

	data = raw_image(image_url)

	if data is None:
		return

	f = open(file_name,'wb')
	f.write(data)
	f.close()

'''
This function is to be updated.
function to store all images
Multiprocessing has been implemented.
Please add the command to store or preprocess raw image data below 'ToDo' tag
'''
def store_raw_images(keyword):

	# retrieve relevant image urls
	image_urls = get_image_urls(keyword)

	multiple_responses = []

	with Pool(processes=no_processes) as pool:
		for image_url in image_urls:
			# get raw_image
			multiple_responses.append(pool.apply_async(raw_image, (image_url, )))

			# sleep in case of dos
			sleep(0.5)

		for res in multiple_responses:
			try:
				data = res.get(timeout=5)
				if data is None:
					pass
				else:
					# print(len(data))
					db = ImageDB.db()
					db.connect()
					db.insert_img(data)
					db.close_connection()
				# ToDo: store or process raw image data here MySQL 
				# data is raw image data
				#print(data)

			except TimeoutError:
				print("Timeout: " + image_url)
