#!/usr/bin/python3
# PyPy supports Python3 now! Yay!

# Python imports
import sys
import urllib.request as urllib2
import json
import pprint
import logging
import argparse
# External imports
from bs4 import BeautifulSoup as BowlShit
# Internal imports
from mycamp_lib import acronyms as acros
from lib.TableParser import TableParser
from lib.PostData import PostData

class CourseScraper:
	def __init__(self):
		pass
	def test_parser(self):
		url_base = "https://ssbp.mycampus.ca"
		url_action = "/prod/bwckschd.p_get_crse_unsec"
		# Setup a page loader
		pl = CoursePageLoader(url_base,url_action)
		pl.set_term("fall","2015")
		pl.set_subj("SOFE")
		# Setup a page parser & parse the page
		try:
			pp = CoursePageParser(pl.get_page())
			pp.parse_page()
		except urllib2.HTTPError as e:
			print("HTTP Error "+str(e.code))
			print("| "+e.reason)
			print("Request details:")
			pprint.PrettyPrinter(indent=4).pprint(pl.get_request_details())
			return

		# get the parsed page data
		obj = pp.get_parsed_object()
		print(json.dumps(obj))

class CoursePageParser:
	def __init__(self, pageData):
		# parameters
		self.pageData = pageData
		self.pageSoup = BowlShit(pageData, "html.parser")

		# initializers
		self.parsedData = []
		self.curr_course = None
		self.curr_class = None
	def get_parsed_object(self):
		return self.parsedData
	def parse_page(self):
		# implicit args
		pageSoup = self.pageSoup

		# create a parser for the main table
		tableParser = TableParser()

		tableParser.on_parse_header(self.parse_section_header)
		tableParser.on_parse_cell(self.parse_section_datum)

		# Parses all the course information in the course table
		# i.e. afaik this for loop only goes through a single table
		for course_table in pageSoup.find_all('table', {'class': "datadisplaytable", 'summary': 
									"This layout table is used to present the sections found"}):
			tableParser.parse_with(course_table)

			""" Old cluttery parsing code
			self.curr_course = None # holds current course object (dict) being edited
			self.curr_class = None # holds current class object (dict) being edited
			print("A")
			for tElem in course_table.children:
				print("B: "+str(tElem.name))
				if tElem.name == "th":
					self.parse_section_header(tElem)
				elif tElem.name == "tr":
					# Look through every table cell in this row
					for td in tElem.children:
						if td.name == "td":
							# Look through every child in every table cell of this row
							for datum in td.children:
								self.parse_section_datum(datum)
			"""


	def parse_section_header(self, tElem):
		"""Parses a header identifying a particular CRN

		TODO: rewrite this docstring so it's more accurate/informative

		Arguments:
			tElem -> BeautifulSoup object to parse (TH element from page)
			course_data -> object to enter new course data into
			curr_course -> object to modify with new course information
			curr_class -> object to modify with new class information
		"""
		parsedData = self.parsedData
		logging.debug("data:section_header:" + tElem.get_text())

		txtParts = tElem.get_text().split(' - ')

		# Fix for potential dash in class name:
		# Take CRN value as first numeric value
		# Done by calling int(val) until ValueError not thrown
		howMany = 0 # will rep how many parts belong to course name
		while True:
			try:
				testInt = int(txtParts[howMany])
				txtParts[howMany] = testInt
				break
			except ValueError:
				pass
			howMany += 1
		cname = ' - '.join(txtParts[0:howMany])
		crn   =            txtParts[howMany+0] # converted to int by above loop
		ccode =            txtParts[howMany+1]
		secNo =            txtParts[howMany+2]

		# Select the relavent course
		for course in parsedData:
			if course['ccode'] == ccode:
				self.curr_course = course
				break
		# If loop did not break (we didn't find the course)
		else:
			# create a new course
			self.curr_course = {'ccode': ccode, 'cname': cname, 'classes': []}
			# split up the course code
			program_code, course_code = self.curr_course['ccode'].split(' ')
			self.curr_course['program_code'] = program_code
			self.curr_course['course_code'] = course_code
			# push new course onto course_data list
			parsedData.append(self.curr_course)

		self.curr_class = {'crn': crn, 'section': secNo, 'times': []}
		self.curr_course['classes'].append(self.curr_class)

	def parse_section_datum(self, datum):
		for element in datum.children:
			logging.debug("data:section_datum_elem:" + str(element.name))
			if element.name == "table":
				logging.debug("data:element_table:" + element.caption.get_text())
				if element.caption.get_text() == "Scheduled Meeting Times":
					self.parse_section_timetable(element)
				elif element.caption.get_text() == "Registration Availability":
					self.parse_section_avail(element)
			if element.name == "span":
				name = element.get_text().encode('ascii', 'ignore').strip()
				val = element.next_sibling.encode('ascii', 'ignore').strip()
				name_and_key_associations = {
					"Associated Term:": 'term',
					"Levels:": 'level',
					"": 'campus'
				}

				for nameToTest in name_and_key_associations:
					if name == nameToTest:
						key = name_and_key_associations[nameToTest]
						self.curr_class[key] = val;
	def parse_section_timetable(self, table):
		logging.debug("Parsing timetable")
		for row in table.children:
			logging.debug(row.name)
			if row.name == "tbody":
				self.parse_section_timetable(row)
			elif row.name == "tr": # in case of inconsistancies
				rowData = []
				# Collect row data by storing each TD value
				for cell in row.children:
					if cell.name == "td":
						rowData.append(cell)
				# Set data to corresponding variable
				week     = rowData[0].get_text().encode('ascii', 'ignore').strip()
				times     = rowData[2].get_text().encode('ascii', 'ignore').strip()
				day     = rowData[3].get_text().encode('ascii', 'ignore').strip()
				room     = rowData[4].get_text().encode('ascii', 'ignore').strip()
				dates     = rowData[5].get_text().encode('ascii', 'ignore').strip()
				ctype     = rowData[6].get_text().encode('ascii', 'ignore').strip()
				profs     = rowData[7].get_text().encode('ascii', 'ignore').strip()


				# === PROBLEM ===

				# It never gets these... but why?

				if week == '':
					week = "ALL"

				# Make sure this is an actual contents row
				if week == "Week" or times == "Time":
					# This means this is just the row of headings
					continue # Go to next iteration
				if (times == "TBA"):
					startTime = None
					endTime = None
				else:
					startTime, endTime = times.split(' - ')
					startTime = time.strptime(startTime, "%I:%M %p")
					endTime = time.strptime(endTime, "%I:%M %p")

				if (dates == "TBA"):
					startDate = None
					endDate = None
				else:
					startDate, endDate = dates.split(' - ')
					startDate = time.strptime(startDate, "%b %d, %Y")
					endDate = time.strptime(endDate, "%b %d, %Y")

				self.curr_class['times'].append({
						'week': week,
						'start_time': startTime,
						'finish_time': endTime,
						'start_date': startDate,
						'finish_date': endDate,
						'room': room,
						'profs': profs,
						'type': ctype,
						'day': day
					})
	def parse_section_avail(self, table):
		for row in table.children:
			logging.debug(row.name)
			if row.name == "tbody":
				self.parse_section_avail(row)
			elif row.name == "tr": # in case of inconsistancies
				rowData = []
				# Collect row data by storing each TD value
				for cell in row.children:
					if cell.name == "td":
						rowData.append(cell)
				# Set data to corresponding variable
				capacity     = rowData[1].get_text().encode('ascii', 'ignore').strip()
				actual         = rowData[2].get_text().encode('ascii', 'ignore').strip()
				remaining     = rowData[3].get_text().encode('ascii', 'ignore').strip()


				# Make sure this is an actual contents row
				if capacity == "Capacity" or actual == "Actual":
					# This means this is just the row of headings
					continue # Go to next iteration

				self.curr_class['capacity'] = int(capacity)
				self.curr_class['actual'] = int(actual)
				self.curr_class['remaining'] = int(remaining)


class CoursePageLoader:
	def __init__(self,url_base,url_action):
		self.actionURL = url_base + url_action
		self.req = None
		
	def set_term(self,semester,year):
		self.term_in = str(year) + str(acros.semester[semester])
	def set_subj(self,subj):
		self.subj = subj

	def get_page(self):
		url, data = self.gen_url_and_data()

		self.req = urllib2.Request(url, data=data)
		print(url)
		self.req.add_header('Referer', "https://ssbp.mycampus.ca/prod/bwckgens.p_proc_term_date")
		"""
		print("=== Headers ===")
		print(req.headers)
		print("=== Data ===")
		print(req.data)
		"""
		response = urllib2.urlopen(self.req)
		pageContents = response.read().decode('utf-8')

		try:
			with open('./log/last_source.log.html','w') as f:
				f.write(pageContents)
		except IOError:
			print("Warning: PageLoader couldn't write to ./log/last_source.log.html")

		return pageContents
	def gen_url_and_data(self):
		url = self.actionURL

		term_in = self.term_in
		subj = self.subj

		vals = PostData()
		vals.add_item('TRM'             , "U")
		vals.add_item('term_in'         , term_in)        # OVER HERE
		vals.add_item('sel_subj'        , "dummy")
		vals.add_item('sel_day'         , "dummy")
		vals.add_item('sel_schd'        , "dummy")
		vals.add_item('sel_insm'        , "dummy")
		vals.add_item('sel_camp'        , "dummy")
		vals.add_item('sel_levl'        , "dummy")
		vals.add_item('sel_sess'        , "dummy")
		vals.add_item('sel_instr'       , "dummy")
		vals.add_item('sel_ptrm'        , "dummy")
		vals.add_item('sel_attr'        , "dummy")
		vals.add_item('sel_subj'        , subj)        # OVER HERE
		vals.add_item('sel_crse'        , "")
		vals.add_item('sel_title'       , "")
		vals.add_item('sel_schd'        , "%")
		vals.add_item('sel_insm'        , "%")
		vals.add_item('sel_from_cred'   , "")
		vals.add_item('sel_to_cred'     , "")
		vals.add_item('sel_camp'        , "%")
		vals.add_item('begin_hh'        , "0")
		vals.add_item('begin_mi'        , "0")
		vals.add_item('begin_ap'        , "a")
		vals.add_item('end_hh'          , "0")
		vals.add_item('end_mi'          , "0")
		vals.add_item('end_ap'          , "a")

		data = vals.get_bytes()

		return (url,data)
	def get_request_details(self):
		details = {}
		details['method'] = self.req.get_method()
		details['data'] = self.req.data
		details['headers'] = self.req.header_items()
		return details



if __name__ == "__main__":
	p = argparse.ArgumentParser(description="Scraper for UOIT courses on MyCampus. Communicates to MyCampus over HTTP, parses data, and generates a JSON file with course information.")
	p.add_argument('-l', '--logging', help="Set logging level", default="info")
	args = p.parse_args()

	loggerLevel = logging.INFO
	if (args.logging == "info"):
		loggerLevel = logging.INFO
	elif (args.logging == "debug"):
		loggerLevel = logging.DEBUG
	logging.basicConfig(level=loggerLevel)

	cs = CourseScraper();
	cs.test_parser()
