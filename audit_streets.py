import xml.etree.cElementTree as ET
import csv
from collections import defaultdict
import re
import pprint

nashville = "nashville.osm"

street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)
street_types = defaultdict(int)

#This list is expected endings streets should have.
expected = ["Avenue", "Broadway", "Boulevard", "Circle", "Commons", "Court", "Drive", "Fork", "Heights", "Highway", "Hollow", 
            "Lane", "Loop", "Place", "Parkway", "Pike", "Road", "Street", "Square", "Trace", "Trail", "Terrace", "Way"]

#This dictionary maps possible alternative endings to what they should be, their more formal endings.
mapping = { "Ave" : "Avenue",
            "ave" : "Avenue",
            "avenue" : "Avenue",
            "Blvd" : "Boulevard",
            "Ct" : "Court",
            "Dr" : "Drive",
            "Ln" : "Lane",
            "Pk" : "Pike",
            "pk" : "Pike",
            "pike" : "Pike",
            "Pkwy" : "Parkway",
            "pky" : "Parkway",
            "Pl" : "Place",
            "pl" : "Place",
            "Rd." : "Road",
            "Rd" : "Road",
            "St": "Street",
            "St.": "Street",
            "st" : "Street"
            }

#this function returns true if a street ending is not in the expected list. It is used
#in the audit function to begin the mapping process to correct the endings
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            return True
    return False

#this function checks to see if the sub tags are 1) named 'tag' and 2) have the attribute 'name'
def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")
    #for the Nashville data set, the street names are kept under name; not addr:street


#this is the function that updates the 
def update_name(street, mapping):
    mapped = sorted(mapping.keys(), key = len, reverse = True)
    #mapped sorts the dictionary by length of the keys (longest keys first); this is important
    #because otherwise the keys could map to the wrong values
    #(e.g. pky might map to 'park'y instead of 'parkway')
    for key in mapped:
        if street.find(key) != -1:
            #this if function looks for the key and if it does not fail (i.e. return -1), replaces
            #that key with the correspondings value (i.e. St. to Street)
            street = street.replace(key,mapping[key])
            return street


#The audit function iterates through the tags, looks for a street or 'way', 
#and then looks at it's street type, identifies if it is expected or not, and then
#corrects it if found in the mapping dictionary.
def audit(filename):
    files = open(filename)
    street_types = defaultdict(set)
    tree = ET.parse(files)
    tree_iter = list(tree.iter())
    for elem in tree_iter:
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):            
                if is_street_name(tag):
                    #the below statement takes the street names, looks for them in the expected list,
                    #and if they are in the list, returns False and does nothing. If true, update_name
                    #is called.
                    if audit_street_type(street_types, tag.attrib['v']):
                        if update_name(tag.attrib['v'],mapping) == None:
                            #if update_name doesn't find a match in the mapping dictionary, it leaves it as is
                            #unless it is a zip code. If it is, it sets the value to None.
                            if len(str(street_type_re.search(tag.attrib['v']))) > 4:
                                tag.attrib['v'] = ''
                            else:
                                continue #do nothing if not a zip code nor in the mapping dictionary
                        else:
                            #this updates the street name in the file with the new, corrected value
                            tag.attrib['v'] = str(update_name(tag.attrib['v'],mapping))                       
    #write the audited version to a new file
    tree.write(filename[:filename.find('.osm')]+'_audit.osm')
    return street_types





if __name__ == '__main__':
    audit(nashville)
