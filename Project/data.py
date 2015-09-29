from collections import defaultdict , Counter
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from datetime import datetime


DATA_FILE = 'data/seattle_washington.osm'

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons", "West","East","North","South", "Southwest", "Northwest",
            "Southeast", "Northeast", "Way", "Terrace", "Rise", "Ridge", "Loop", "Highway", "Heights",
            "Crescent","Green", "Gardens", "Circle", "Alley", "Close"]

mapping = {"west": "West",
           "way": "Way",
           "street": "Street",
           "st.": "Street",
           "st": "Street",
           "southwest": "Southwest",
           "south": "South",
           "se": "Southeast",
           "ne": "Northeast",
           "n": "North",
           "boulevard": "Boulevard",
           "avenue": "Avenue",
           "ave": "Avenue",
           "av.": "Avenue",
           "W.": "West",
           "W": "West",
           "Steet": "Street",
           "St.": "Street",
           "St": "Street",
           "Sq": "Square",
           "Se": "Southeast",
           "SW": "Southwest",
           "ST": "Street",
           "SOUTHWEST": "Southwest",
           "SE": "Southeast",
           "S.E.": "Southeast",
           "S.": "South",
           "S": "South",
           "Rd.": "Road",
           "Rd": "Road",
           "ROAD": "Road",
           "Pl": "Place",
           "Pkwy": "Parkway",
           "PL": "Place",
           "NW": "Northwest",
           "NE": "Northeast",
           "N.E.": "Northeast",
           "N.": "North",
           "N": "North",
           "Ln.": "Lane",
           "Hwy": "Highway",
           "E.": "East",
           "E": "East",
           "Dr": "Drive",
           "Ct": "Court",
           "CT": "Court",
           "Blvd": "Boulevard",
           "Blvd.": "Boulevard",
           "Ave.": "Avenue",
           "Ave": "Avenue",
           "Av.": "Avenue",
           "AVENUE": "Avenue",
           "AVE": "Avenue"
           }

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def count_tags(filename):
    tags = {}
    with open(filename, 'rb') as f:
        for event,element in ET.iterparse(f):
            if element.tag in tags:
                tags[element.tag] += 1
            else:
                tags[element.tag] = 1
    return tags


def re_search(text, re_list):
    for re in re_list:
        m = re.search(text)
        if m.group():
            return True
    return False


def key_type(element, keys):
    if element.tag == "tag":
        k = element.attrib['k']
        if lower.search(k):
            keys['lower'] += 1
        elif lower_colon.search(k):
            keys['lower_colon'] += 1
        elif problemchars.search(k):
            keys['problemchars'] += 1
        else:
            keys['other'] += 1
    return keys


def identify_key_issues(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys


def is_street_name(elem):
    return elem.attrib['k'] == "addr:street"


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    return street_types


def process_name(name, mapping):
    # takes name and if it matches the re and is in the mapping
    # returns the better name, else returns original name
    st = street_type_re.search(name)
    if st:
        st = st.group()
    else:
        return name
    if st in mapping:
        return name.replace(st, mapping[st])
    else:
        return name


def process_map(file_in, pretty = False):

    file_out = "{0}.json".format(file_in)
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


def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        node['type'] = element.tag
        for prop, value in element.attrib.iteritems():
            if prop == 'lon':
                # handle longitude case
                if not node.get('pos', False):
                    node['pos'] = [0.0]*2
                node['pos'][1] = float(value)
            elif prop == 'lat':
                # handle latitude case
                if not node.get('pos', False):
                    node['pos'] = [0.0]*2
                node['pos'][0] = float(value)
            elif prop in CREATED:
                # if the property is in the list to be added under created
                if not node.get('created', False):
                    node['created'] = {}
                node['created'][prop] = value
            else:
                # not matched, add it like normal
                node[prop] = value
        for child in element:
            #look for children tags under the current tag
            if child.tag == 'tag':
                if child.attrib['v'] in ['suburb', 'cuisine']:
                    pass
                key_attribute = child.attrib['k']
                value_attribute = child.attrib['v']
                if match_re(key_attribute, [problemchars]):
                    # there was a match with the re, so don't process this child tag
                    continue
                elif key_attribute[:5] == 'addr:':
                    #if the k attrib starts with "addr:"
                    k_split = key_attribute.split(':')
                    if len(k_split) == 2:
                        # contains only 1 ":" character in the text
                        if not node.get('address', False):
                            node['address'] = {}
                        if k_split[1] == "street":
                            # This is the street name so pass the name through the process_name function
                            value_attribute = process_name(value_attribute, mapping)
                        node['address'][k_split[1]] = value_attribute
                else:
                    #default tag case
                    node[key_attribute] = child.attrib['v']
            elif child.tag == 'nd':
                # create a node_refs key and list, and add the ref to the list
                if not node.get('node_refs', False):
                    node['node_refs'] = []
                node['node_refs'].append(child.attrib['ref'])
            else:
                # not to be processed
                pass
        return node
    else:
        return None

def process_tag_count(file):
    tag_list = defaultdict(set)
    tag_frequency = Counter()
    for _, element in ET.iterparse(file):
        if element.tag == "tag":
            tag_list[element.attrib['k']].add(element.attrib['v'])
            tag_frequency[element.attrib['k']] += 1
    return {"taglist": tag_list, "tagfrequency": tag_frequency}

def match_re(text, re_list):
    # take a list of compile regular expression and searches for matches in text
    # If matches are found in any re return True
    # else return false
    for reg in re_list:
        if reg.search(text):
            return True
    return False

if __name__ == "__main__":
    startTime = datetime.now()
    print startTime
    #process_map(DATA_FILE,pretty=False)
    tag_counts = process_tag_count(DATA_FILE)

    endTime = datetime.now()
    print endTime
    print "Elapsed Time {}".format(endTime-startTime)