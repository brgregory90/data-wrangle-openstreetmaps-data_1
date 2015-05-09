import xml.etree.ElementTree as ET
import re
import codecs
import json


CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


#this function is for cases where address has been broken down into parts. In those cases,
#there will be two colons in the string and the string 'street.' 
def is_second_colon(string):
    values = string.split(":")
    if len(values) > 2 and values[1] == "street":
        return True
    return False

#this returns true when there are problem characters in the given
#string. When used in shape_element, this causes node to be returned
#without any addition.
def prob_chars(elem):
    return re.search(problemchars, elem)

#This function is responsible for shaping the ultimate json file.
def shape_element(elem):
    node = {}
    #define an empty dictionary called node that everything will go into
    if elem.tag == "node" or elem.tag == "way" :
        node['type'] = elem.tag
        for attrib in elem.attrib:
            #look for attributes in the CREATED list and add them to a new
            #created dictionary that will be included in the node dictionary
            if attrib in CREATED:
                if "created" not in node:
                    node["created"] = {}
                node["created"][attrib] = elem.attrib[attrib]
                continue
            #put the geo coordinates into a 'pos' list
            if "pos" not in node:
                node["pos"] = []
            if attrib == 'lat': #put lat in 'pos'
                node['pos'].append(float(elem.attrib['lat']))
                continue
            if attrib == 'lon': #put lon in 'pos'
                node['pos'].append(float(elem.attrib['lon']))
                continue
            node[attrib] = elem.attrib[attrib]
        #the following loop searches for either node_references or tags
        for tags in elem.getiterator():
            #node_references are identified in 'nd' tags and appended to
            #a node_refs list
            if tags.tag == 'nd':
                ref_value = tags.attrib['ref']
                if "node_refs" in node:
                    node["node_refs"].append(ref_value)
                else:
                    node["node_refs"] = [ref_value]
            #tags with 'tag' label are added to node dictionary with the
            #k attribute as the dictionary key
            if tags.tag == 'tag':
                kval = tags.attrib['k']
                #if there is a second colon with 'address', simply return the
                #node without addition
                if is_second_colon(kval):
                    return node
                elif prob_chars(kval):
                    return node
                #if the k attribute is an address attribute, it is added to
                #the address dictionary within 'node.' The part after the ':'
                #is added to the dictionary as the value
                elif kval.startswith("addr:"):
                    if "address" not in node:
                        node["address"] = {}
                    values = kval.split(":")
                    key = values[1]
                    node["address"][key] = tags.attrib['v']
                else:
                    node[kval] = tags.attrib['v']
        return node
    else:
        return None

#this function is the core of the script. It calls shape_element which
#formats the file into json and then it exports the json to a new file
def process_map(file_in, pretty = False):
    filed = open(file_in)
    file_out = "nashville_mongo.json".format(filed)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

if __name__ == "__main__":
    process_map(nashville, pretty = False)


