#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
import os
import re
import sys
import uuid
import time
import string
import tweepy
import requests
import datetime
import unicodedata
import configparser
import pandas as pd
import paramiko
from neo4j import GraphDatabase
from bs4 import BeautifulSoup
from mailjet_rest import Client
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import app.helper.logger as log


LOCATION = "production"


def get_project_uri():
	"""
	Function to get the project uri.
	"""
	return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))


def get_path_file_data(elements):
	"""
	Function to get the file path.
	"""
	return "/".join([get_project_uri(), "data"] + elements)


def get_file_data(elements, dtype=str):
	"""
	Function to get the file.
	"""
	return pd.read_csv(filepath_or_buffer=get_path_file_data(elements), header=[0], encoding='utf-8', dtype=dtype)


def get_conf_file():
	"""
	Function to get the configuration file.
	"""
	conf = configparser.ConfigParser()
	conf.read(get_project_uri()+"/app/app.ini")
	return conf


def create_folder(directory):
	"""
	Function to check if a folder exists and otherwise create it.
	"""
	# Check if the folder exists
	if not os.path.exists(directory):
		# Create the folder
		os.makedirs(directory)


def get_logger(log_file_type="task"):
	"""
	Function to get the logger.
	"""
	create_folder("log")
	if log_file_type == "api":
		return log.get_logger("/".join([get_project_uri(), "log", "api.log"]))
	else:
		return log.get_logger("/".join([get_project_uri(), "log", "task.log"]))


def get_graph_database_driver(logger):
    """
    Connect to Neo4j using credentials stored
    in environment variables.
    """
    try:
        uri = os.environ["NEO4J_URI"]
        user = os.environ["NEO4J_USER"]
        password = os.environ["NEO4J_PASSWORD"]

        return GraphDatabase.driver(
            uri,
            auth=(
                user,
                password,
            ),
        )

    except Exception as e:
        logger.critical(
            "%s :: %s :: GET_GRAPH_DATABASE_DRIVER :: %s",
            os.path.basename(__file__),
            os.getpid(),
            e,
        )
        sys.exit(1)


def get_twitter_client(logger):
	"""
	Function that initializes the connection to the socials.
	"""
	client = None
	try:
		client = tweepy.Client(bearer_token="AAAAAAAAAAAAAAAAAAAAAJ0rngEAAAAABKfAO2VmiC85O05P2CuwmvQScmg%3D4HhCXYRxIEAQ1FXv6q3tbrf4B1amZ62bqPGiTWFfZZu4yoiZjS")
	except Exception as e:
		logger.critical("%s :: %s :: GET_TWITTER_CLIENT :: %s", os.path.basename(__file__), os.getpid(), e)
	finally:
		return client


def request(logger, url, output, request_type="GET", params=None, headers=None, timeout=None, stream=None):
	"""
	Function to send a request (GET (default) or POST).
	"""
	result = None
	try:
		request_type = str(request_type).upper()
		# Get the response
		if request_type == "POST":
			r = requests.post(url=url, data=params, headers=headers, timeout=timeout, stream=stream)
		else:
			r = requests.get(url=url, params=params, headers=headers, timeout=timeout, stream=stream)
		output = str(output).upper()
		# Convert the response
		if output == "SOUP":
			result = BeautifulSoup(markup=r.content, features="html.parser")
		elif output == "IMAGE":
			if r.status_code == 200:
				# Set decode_content value to True, otherwise the downloaded image file's size will be zero.
				r.raw.decode_content = True
				result = r.raw
		else:
			result = r.json()
	except Exception as e:
		logger.critical("%s :: %s :: REQUEST :: %s :: %s", os.path.basename(__file__), os.getpid(), url, e)
		result = None
	finally:
		return result


def get_page_content_soup(logger, url, html=None):
	"""
	Function to get the page content soup.
	"""
	soup = BeautifulSoup(markup="", features="html.parser")
	try:
		if html is None:
			# Get the HTML content from the given URL
			headers = {'User-Agent': 'Mozilla/5.0'}
			# Wait 4 seconds before making the request to avoid blocking
			time.sleep(4)
			html = requests.get(url=url, timeout=10, headers=headers).content
		# Make the soup
		soup = BeautifulSoup(markup=html, features="html.parser")
	except Exception as e:
		logger.critical("%s :: %s :: GET_PAGE_CONTENT_SOUP :: %s", os.path.basename(__file__), os.getpid(), e)
	finally:
		return soup


def notify(logger, header, message_text, message_html, email=None, pseudo=None):
	"""
	Function to send an email.
	"""
	conf = get_conf_file()
	email = conf.get("email", "from") if email is None else email
	pseudo = "Viziball" if pseudo is None else pseudo
	mailjet = Client(auth=(conf.get("email", "api_key"), conf.get("email", "api_secret")), version='v3.1')
	data = {
		'Messages': [
			{
				"From": {
					"Email": conf.get("email", "from"),
					"Name": "Viziball"
				},
				"To": [
					{
						"Email": str(email),
						"Name": str(pseudo)
					}
				],
				"Subject": str(header),
				"TextPart": message_text,
				"HTMLPart": message_html,
				"CustomID": str(uuid.uuid4())
			}
		]
	}
	result = mailjet.send.create(data=data)
	if result.status_code == 200:
		logger.info("%s :: %s :: NOTIFY -> SUCCESS", os.path.basename(__file__), os.getpid())
	else:
		logger.critical("%s :: %s :: NOTIFY :: EMAIL_NOT_SENT", os.path.basename(__file__), os.getpid())


def format_date(date, input_format="%B %d, %Y", output_format="%Y%m%d"):
	"""
	Function to format the date.
	"""
	try:
		return datetime.datetime.strptime(date, input_format).strftime(output_format)
	except Exception:
		return "0"


def get_game_id(date, shn_home_team):
	"""
	Function to create the new game_id.
	"""
	return date.replace('-', '') + "0" + shn_home_team


def remove_accents(input_str):
	"""
	Function to remove accents from a string.
	"""
	nfkd_form = unicodedata.normalize('NFKD', input_str)
	ascii_form = nfkd_form.encode('ASCII', 'ignore')
	return ascii_form.decode("utf-8")


def remove_ponctuations(input_str):
	"""
	Function to remove ponctuation from a string.
	"""
	return input_str.translate(str.maketrans('', '', string.punctuation))


def format_input_string(input_str):
	"""
	Function to format a string.
	"""
	input_str = str(input_str).lower()
	regex = re.compile(r"(\si+)|(\s(\w){2}\.)")
	if regex.search(input_str):
		input_str = input_str.split(" ")[0]
	input_str = remove_ponctuations(input_str)
	input_str = remove_accents(input_str)
	return input_str


def get_duration(start_time, digits=2):
	"""
	Function to get duration.
	"""
	return round(time.time() - start_time, digits)


def set_season_file(sport, championship, name, start=None, end=None, info=None):
	"""
	Function to update the seasons file of championship.
	"""
	try:
		seasons = get_file_data([sport, championship, "seasons.csv"])
	except Exception as e:
		seasons = pd.DataFrame(columns=["season", "name", "start", "end", "info"])
	tmp = seasons[seasons['name'] == name]
	if len(tmp.index) == 0:
		season = int(name[-4:])
		start = int(start) if start is not None else ""
		end = int(end) if end is not None else ""
		info = str(info) if info is not None else ""
		seasons = pd.concat([seasons, pd.DataFrame.from_records([{'season':season, 'name':name, 'start':start, 'end':end, 'info':info}])])
	elif len(tmp.index) == 1:
		if start is not None:
			seasons.loc[seasons['name'] == name, 'start'] = int(start)
		if end is not None:
			seasons.loc[seasons['name'] == name, 'end'] = int(end)
		if info is not None:
			seasons.loc[seasons['name'] == name, 'info'] = str(info)
	seasons.to_csv(path_or_buf=get_path_file_data([sport, championship, "seasons.csv"]), encoding='utf-8', index=False)


def clear_cache(logger):
	"""
	Function to clear the cache of the website.
	"""
	r = requests.post(url="https://api2.datanostra.app/cache", timeout=0.5)
	if r.status_code != 200:
		logger.critical("%s :: %s :: CACHE_CANNOT_BE_RESETED", os.path.basename(__file__), os.getpid())
	else:
		logger.info("%s :: %s :: CACHE_CLEARED", os.path.basename(__file__), os.getpid())


def get_assets_files_name():
	"""
	Function to get the assets files name.
	"""
	# Get configuration
	conf = get_conf_file()
	files_name = []
	for asset in ["path_sitemap", "path_players_seo"]:
		path = get_project_uri() + conf.get("viziball", asset)
		for file_name in os.listdir(path):
			files_name.append(path + file_name)
	return files_name


def send_files_via_sftp(logger, files_name):
	"""
	Function to send a file via SFTP
	"""
	# Get configuration
	conf = get_conf_file()
	# Create a SSH client
	ssh = paramiko.SSHClient()
	# Set policy to use when connecting to servers without a known host key.
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	# Connect to an SSH server and authenticate to it.
	ssh.connect(hostname=conf.get("sftp", "hostname"), username=conf.get("sftp", "username"), password=conf.get("sftp", "password"))
	# Open the SFTP session 
	sftp = ssh.open_sftp()

	for file_name in files_name:
		try:
			file_name_only = file_name.split("/")[-1]
			sftp.put(file_name, conf.get("sftp", "remote_path") + file_name_only)
			logger.info("%s :: %s :: FILE_UPLOADED :: %s", os.path.basename(__file__), os.getpid(), file_name_only)
		except Exception as e:
			logger.critical("%s :: %s :: FILE_CANNOT_BE_UPLOADED :: %s", os.path.basename(__file__), os.getpid(), e)

	# Close the SFTP session
	sftp.close()
	# Close the SSH session
	ssh.close()


def take_page_screenshot(logger, championship, team1, team2, date, element="impactChart"):
	"""
	Function to take the sreenchot of the match element.
	"""
	conf = get_conf_file()
	# Get the geckodriver path.
	path_geckodriver = "/".join([get_project_uri(), "driver",conf.get("viziball", "geckodriver")])
	path_folder_image = get_project_uri() + conf.get("viziball", "path_face")
	# Variables
	team1 = str(team1).lower()
	team2 = str(team2).lower()
	date = str(date)
	# Firefox options
	options = Options()
	# No window
	options.headless = True
	try:
		global driver
		# Set the rigth driver
		driver = webdriver.Firefox(options=options, executable_path=path_geckodriver)
		# Load page to take picture
		driver.get("https://viziball.app/game/"+championship+"/fr/"+team1+"/"+team2+"/"+date+"/true")
		time.sleep(3)
		tmp = driver.find_element(By.ID, element)
		tmp.screenshot(path_folder_image+team1+"_"+team2+"_"+date+".png")
		driver.quit()
	except Exception as e:
		logger.critical("%s :: %s :: TAKE_PAGE_SCREENSHOT :: %s :: %s :: %s :: %s", os.path.basename(__file__), os.getpid(), team1, team2, date, e)
		driver.quit()
		sys.exit(1)
