#!/usr/lib/ python3
from asyncore import write
from distutils.file_util import move_file
from email import generator
from time import sleep
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import col, date_format
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path 
from configparser import ConfigParser
import logging
import os
import re
import pandas as pd
import requests
import re
import urllib.request
import lzma
import shutil
import pathlib
import sys
import getopt


class MTA_Bus_Route_Analysis_Persistor:
	
	def __init__(self) -> None:
		self.source_path = '/mnt/data-files'
		self.log_file = os.path.join(self.source_path, 'log')
		self.processed_dir = os.path.join(self.source_path, 'processed')
		self.port = None
		self.help = ''
		

	def write_to_database(self):
		sql = SparkSession.builder\
            .appName("database-app")\
            .config("spark.jars", "/opt/spark-apps/postgresql-42.2.22.jar")\
            .config("spark.sql.execution.arrow.pyspark.enabled", "true")\
            .getOrCreate()
			
		sc = sql.sparkContext
		
		for file in [os.path.join(self.source_path, f) for f in os.listdir(self.source_path) if f.endswith('.txt')]:   
			
			logging.info(f'{str(datetime.now())[:23]} | Reading file...')
			df = sql.read.option("header", "true") \
				.option("delimiter", "\t") \
				.option("inferSchema", "true") \
				.csv(file) \
				.withColumn("report_hour", date_format(col("time_received"), "yyyy-MM-dd HH:00:00")) \
				.withColumn("report_date", date_format(col("time_received"), "yyyy-MM-dd")) \

			logging.info(f'{str(datetime.now())[:23]} | {df.count()} records read.')

			rows_read = df.count()
			file_name = file.split('/')[-1]
			run_date = datetime.now()
			logging.info(f'{str(run_date)[:23]} | Processing file \'{file_name}\'...')

			# ###################################################################
			# ####   Write file processing metrics                           ####
			# ###################################################################
			try:
				rows = {'run_date': [run_date, run_date], 'file_name': [file_name, file_name],
						'metric': ['record_count', 'started_writing_to_database'],
						'value': [str(rows_read), str(datetime.now())]}
				meta_df = sql.createDataFrame(pd.DataFrame(rows))

				print(f'\ndb_url={db_url}\n')

				meta_df.write.jdbc(url=db_url, table="file_processing_metrics", mode='append', properties=properties)

			except Exception as e:
				self.handle_exception(e)
			
			# ###################################################################
			# ####   Write file data                                         ####
			# ###################################################################

			self.write(df)

			# ###################################################################
			# ####   Get unique written record count                         ####
			# ###################################################################
			from_date = datetime.strptime(file_name.split(".")[0], '%Y-%m-%d') + timedelta(hours=4)

			to_date = from_date + timedelta(hours=24)

			query = f'''(select count(1) 
			from mta_reports 
			where 
			report_hour >= \'{from_date}\' 
			and report_hour < \'{to_date}\') as query'''

			#logging.info(f'{query}')

			written_df = sql.read.jdbc(url=db_url, table=query, properties=properties)

			rows_written = written_df.collect()[0]['count']

			# # ###################################################################
			# # ####   Write file processing metrics                           ####
			# # ###################################################################
			try:
				rows = {'run_date': [run_date, run_date], 'file_name': [file_name, file_name],
						'metric': ['processed_record_count', 'finished_writing_to_database'],
						'value': [str(rows_written), str(datetime.now())]}
				meta_df = sql.createDataFrame(pd.DataFrame(rows))
				meta_df.write \
					.jdbc(url=db_url, table="file_processing_metrics", mode='append', properties=properties)
			except Exception as e:
				self.handle_exception(e)

			if(rows_written == rows_read):
				shutil.move(file, self.processed_dir)
	
	
	def write(self, df):
		try:
			df.write.jdbc(url=db_url, table='mta_reports', mode='append', properties=properties)
		except Exception as e:
			self.handle_exception(e)

	def check_params(self, argv):
		try:
			app.help = '{0} -p <port>'.format(argv[0])
			opts, args = getopt.getopt(argv[1:], 'hp:', ['help', 'port='])	
		except Exception as e:
			self.handle_exception(e)

		for opt, arg in opts:
			if opt in ("-h", "--help"):
				self.handle_exception(Exception('Error - --help option passed to module!'))
			elif opt in ("-p", "--port"):
				self.port = int(arg)
			else:
				self.handle_exception(Exception('Error - invalid option passed to module!'))


	def handle_exception(self, e):
		pattern = '.*(?=Detail: Key .time_received, vehicle_id.=)(?=.*already exists.).*'
		if (re.match(pattern, repr(f'''{e}''')) == None):
			for i in range(2):
				logging.error(
					f'{str(datetime.now())[:23]} | !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
			message = f'''{str(datetime.now())[:23]} | Unhandled exception: {e}'''
			logging.error(message)
			for i in range(2):
				logging.error(
					f'{str(datetime.now())[:23]} | !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
			raise Exception(e)



	def db_init(self, filename='/opt/spark-apps/database.ini', section='postgresql'):
		parser = ConfigParser()
		parser.read(filename)

		db={}

		if parser.has_section(section):
			params=parser.items(section)
			for param in params:
				db[param[0]] = param[1]
		else:
			raise Exception('Section {0} not found in the {1}'.format(section, filename))

		return db

def main(argv):
	global db_url, properties, app
	app = MTA_Bus_Route_Analysis_Persistor()
	app.check_params(argv)
	params = app.db_init()
	db_url = 'jdbc:postgresql://host.minikube.internal:{0}/{1}'.format(app.port, params['database'])

	print(f'\n{db_url}\n')

	properties = {
		"user": params['user'],
		"password": params['password'],
		"driver": params['driver']
	}
	
	logging.basicConfig(level=logging.INFO, filename=app.log_file,
                        format='%(levelname)s |  DATABASE  | %(message)s')

	# Create processed directory
	if(not os.path.exists(app.processed_dir)):
		os.mkdir(app.processed_dir)

	total_delta = timedelta(0)
    
	start = datetime.now()
    
	logging.info(f'{str(start)[:23]} | Started writing to database...')
	loops = 5
	for loop in range(loops):
		if([os.path.join(app.source_path, f) for f in os.listdir(app.source_path) if f.endswith('.txt')]):
			app.write_to_database()
			logging.info(f'{str(datetime.now())[:23]} | Write to database completed, checking for more files...')
		else:
			logging.info(f'{str(datetime.now())[:23]} | Wait 60 seconds for files to arrive ({loop+1}/{loops})...')
			sleep(60)
	 
	end = datetime.now()
	logging.info(f'{str(end)[:23]} | Finished writing to database.')
	total_delta = end-start
	logging.info(f'{str(end)[:23]} | Total write time: {total_delta}')


if __name__ == '__main__':
    main(sys.argv)
