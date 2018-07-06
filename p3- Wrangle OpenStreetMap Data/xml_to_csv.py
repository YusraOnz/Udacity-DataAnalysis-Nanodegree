# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""This script is used both for data cleaning then form conversion"""


import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import io

import cerberus

import schema

OSM_PATH = "riyadh_saudi-arabia.osm"
#OSM_PATH = "riyadh_sample.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,

                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}

    way_attribs = {}

    way_nodes = []

    tags = []  # Handle secondary tags the same way for both node and way elements

    tagType = []

    tagKey = []

    if element.tag == 'node':

        node_attribs['id'] = element.attrib['id']

        node_attribs['user'] = element.attrib['user']

        node_attribs['uid'] = element.attrib['uid']

        node_attribs['version'] = element.attrib['version']

        node_attribs['lat'] = element.attrib['lat']

        node_attribs['lon'] = element.attrib['lon']

        node_attribs['timestamp'] = element.attrib['timestamp']

        node_attribs['changeset'] = element.attrib['changeset']

        for tag in element.iter("tag"):

            if not PROBLEMCHARS.search(tag.attrib['k']):  # if it has prob chars then ignore


                if LOWER_COLON.search(tag.attrib['k']):

                    tagKey = tag.attrib['k'].split(':', 1)[1]  # only split once

                    tagType = tag.attrib['k'].split(':')[0]



                else:

                    tagKey = tag.attrib['k']

                    tagType = 'regular'

                tags.append({'id': node_attribs['id'], 'key': tagKey, 'value': tag.attrib['v'], 'type': tagType})

        return {'node': node_attribs, 'node_tags': tags}


    elif element.tag == 'way':

        way_attribs['id'] = element.attrib['id']

        way_attribs['user'] = element.attrib['user']

        way_attribs['uid'] = element.attrib['uid']

        way_attribs['version'] = element.attrib['version']

        way_attribs['timestamp'] = element.attrib['timestamp']

        way_attribs['changeset'] = element.attrib['changeset']

        # tags = []

        for tag in element.iter('tag'):

            if not PROBLEMCHARS.search(tag.attrib['k']):

                tag_colon = LOWER_COLON.search(tag.attrib['k'])

                if tag_colon:

                    tagKey = tag.attrib['k'].split(':', 1)[1]

                    tagType = tag.attrib['k'].split(':')[0]



                else:

                    tagKey = tag.attrib['k']

                    tagType = 'regular'

                tags.append({'id': way_attribs['id'], 'key': tagKey, 'value': tag.attrib['v'], 'type': tagType})

    pos = 0

    for nd in element.iter('nd'):
        way_nodes.append({'id': way_attribs['id'], 'node_id': nd.attrib['ref'], 'position': pos})

        pos += 1

    return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
                                                    k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in
                                                    row.iteritems()
                                                    })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
            codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
            codecs.open(WAYS_PATH, 'w') as ways_file, \
            codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
            codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


# ================================================== #
#               Cleaning Function                    #
# ================================================== #
def clean(tag):

    tagValue=tag.attrib['v']
    if tag.attrib['k']=='addr:street':
        tagValue=cleanStreetName(tagValue)
    elif tag.attrib['k']=='phone':
        tagValue=cleanPhoneNumber(tagValue)
    return tagValue




    # fixing the case for english names
def cleanStreetName(streetName):
    """This function takes a string of street name and clean it in terms of case used and street type"""

    arabicText = re.compile(r'^[\u0600-\u06ff\s\u0031-\u0039]+$')


    mapping = {"St": "Street",
                "St.": "Street",
                "Rd": "Road",
                "Rd.": "Road"}

    # only clean english text
    if not arabicText.search(streetName):
        # removing starting and ending whitespace
        streetName = streetName.strip().split()

        for word in streetName:

            # check if the word is not an abbreviation to fix its case
            if not word.isupper():
                streetName[streetName.index(word)] = word.title()

        # return the last item in the list which possibly represent the type
        streetType = streetName[-1]

        if streetType in mapping:
            # replace the old type with the new one
            streetName[-1] = mapping[streetType]

        streetName = ' '.join(streetName)

    return streetName

def cleanPhoneNumber(phone):
    """This function take a string phone number and reformat it."""

    # mapping of erroneous street types
    mapping = {"90000002": "+966920000002", "92000702": "+966920000702"}

    #standard numbers formats in Saudi Arabia
    homeNum_re = re.compile(r'^(00966|\+966|966)?0?1?1?([\d]{7})$', re.IGNORECASE)
    mobileNum_re = re.compile(r'^(00966|\+966|966)?0?(5[\d]{8})$', re.IGNORECASE)
    uniNum_re = re.compile(r'^(00966|\+966|966)?(9200[\d]{5})$', re.IGNORECASE)
    tollFreeNum_re = re.compile(r'^(00966|\+966|966)?(800[\d]{7})$', re.IGNORECASE)


    if ";" in phone:
        phone = phone.split(';')[0]

    if tollFreeNum_re.match(phone):

        # toll free numbers
        phone = tollFreeNum_re.sub(r'+966\2', phone)

    elif uniNum_re.match(phone):

        # universal access numbers
        phone = uniNum_re.sub(r'+966\2', phone)


    elif mobileNum_re.match(phone):

        # mobile numbers
        phone = mobileNum_re.sub(r'+966\2', phone)


    elif homeNum_re.match(phone):

        # home numbers
        phone = homeNum_re.sub(r'+96611\2', phone)

    else:
        # invalid numbers
        phone = mapping[phone]

    return phone


if __name__ == '__main__':
    process_map(OSM_PATH, validate=True)


