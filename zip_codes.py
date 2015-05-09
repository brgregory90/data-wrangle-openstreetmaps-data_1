import xml.etree.cElementTree as ET
import csv
from collections import defaultdict
import re

Nashville = open("nashville.osm", "r")

def is_zip(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "tiger:zip_left")

#The following function writes the zip codes to a separate csv for inspection
def print_sorted_dict(d): 
    keys = d.keys()
    writer = csv.writer(open('zip_codes.csv', 'wb'))
    keys = sorted(keys, key = lambda s: s.lower())
    for k in keys:
        v = d[k]
        writer.writerow([k,v])  

#this function parses the OSM file and cycles through elements #with ‘way’ tags. 
#If these way tags have a zip_code (see #is_zip), it either adds that zip to a 
#dictionary or adds one to an existing zip code.

def zip(filename):
	zip_code = {}
	for event, elem in ET.iterparse(filename):
		if elem.tag == 'way':
			for tags in elem.iter("tag"):
				if is_zip(tags):
					zips = tags.attrib['v']
					if zips in zip_code:
					#if zipcode exists in dictionary add one
						zip_code[zips] += 1
					else:
					#if not, add zipcode to dictionary
						zip_code[zips] = 1
	print_sorted_dict(zip_code)

if __name__ == '__main__':
    zip(Nashville)