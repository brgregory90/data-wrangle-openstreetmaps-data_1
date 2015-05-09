#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import csv

osm_file = open("nashville.osm", "r")

street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)
street_types = defaultdict(int)
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


#This function looks for problem characters in the street type
#and returns true if they exist.
def prob_chars(elem):
    return re.search(problemchars, elem)


#This function looks at the street names, extracts out the street type
#and then adds them to a default dictionary that has been created already.
def street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if prob_chars(street_type): #If problem characters, skip that value.
            pass
        elif street_type in street_types:
            street_types[street_type] += 1
            #if street_type is already in dictionary, add one.
        else:
            street_types[street_type] = 1
            #if it does not exist, create it and set to one

#This function prints the dictionary with street ending frequency
#to a separate csv for easier inspection.
def print_sorted_dict(d):
    keys = d.keys()
    writer = csv.writer(open('streets.csv', 'wb'))
    keys = sorted(keys, key = lambda s: s.lower())
    for k in keys:
        v = d[k]
        writer.writerow([k,v])  

#This function checks to see if the subelement has both a 'tag' tag and
#attribute 'addr:street' where the street names are located.
def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")


#This funciton is the core engine of the script. It iterates through the file
#looks for the correct tags, creates a dictionary with street counts, and
#then prints it to a separate csv.
def audit():
    for event, elem in ET.iterparse(osm_file):
        if is_street_name(elem):
            street_type(street_types, elem.attrib['v'])   
    print_sorted_dict(street_types) 


#This begins the script when called.
if __name__ == '__main__':
    audit()