#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""This script is used to explore and audit the map."""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import io

#mapFile = io.open("riyadh_sample.osm", "r",encoding='utf8')
mapFile = io.open("riyadh_saudi-arabia.osm", "r",encoding='utf8')
tree = ET.parse(mapFile) #parse file into XML tree
root = tree.getroot() #get the root node of the XML tree




def countTags():
    """count the number of unique tags or subtags"""
    mapFile.seek(0)
    tags = defaultdict(int)

    # loop over every XML tag
    for event, elem in ET.iterparse(mapFile):
        # grouping tags and counting its number
        tags[elem.tag] += 1
    return tags

def tagNameByLevel():
    """finds and return the tag names structured by their level in a default dictionary.
    The tag keys represent first level children.
    The values associated with each key represent the child/children of that element.
    It also represent the second level children of the root.
    """
    tagByLevel = defaultdict(set)

    #loop on direct children of root
    for element in root:

        #loop on direct children of element
        for child in list(element):
            tagByLevel[element.tag].add(child.tag)
    return tagByLevel





def groupTagAttrib(tagParentName):
    """
    This function group the <tag> attribute values by their keys.
    Notice that only tags that are children of the passed parameter are used.
    Returns default dictionary where the dictionary keys represents the tag attribute keys and the dictionary values represents the tag attribute values associated with that key.
    """

    mapFile.seek(0)

    tagAttribs = defaultdict(list)

    # loop over only (tagParentName) element which are first level children
    for node in root.findall('./' + tagParentName):

        # loop over only the tag element which are second level children
        for tag in node.findall("tag"):
            tagAttribs[tag.attrib['k']].append(tag.attrib['v'])

    return tagAttribs


def attribSize(groupedAttribDict):
    """
    This function find the size of each key attribute.
    Takes default dictionary of grouped tag attributes.
    Returns the size or the number of values associated with each key.
    """
    attribSize = dict()

    for k, v in groupedAttribDict.items():
        attribSize[k] = len(v)

    return attribSize


def uniqTagValues(groupedAttribDict):
    """
    This function used to remove duplicated tag attrib values.
    Takes default dictionary of grouped tag attributes.
    Returns the same dictionay without duplicated values.
    """
    for k, v in groupedAttribDict.items():
        groupedAttribDict[k] = set(v)

    return groupedAttribDict


def auditStreetTypes():
    """This function returns the possible street types by extracting the last word in a street name"""
    streetTypesDict = defaultdict(int)

    mapFile.seek(0)

    # matches one or more non-space charecter at the end of the string with optional ending dot
    streetType_re = re.compile(r'\S+$', re.IGNORECASE)

    # to loop over the xml element
    for event, elem in ET.iterparse(mapFile):

        # to check if the tag contains a street names
        # street names are the values associted with (addr:street) key attribute
        # example: <tag k="addr:street" v="Khurais Road" />
        if (elem.tag == "tag") and (elem.attrib['k'] == "addr:street"):

            streetName = elem.attrib['v']

            # to extract the street type from street name which is usually the last word in the string
            streetType = streetType_re.search(streetName)

            # if there is a match, then the length of the returned value will be larger than zero (True)
            if streetType:
                # add street type to the dictionary if doesn't exist
                # increment its count
                streetTypesDict[streetType.group()] += 1

    return streetTypesDict



#--------------------------------------------------

print(attribSize(groupTagAttrib("node")))
print(uniqTagValues(groupTagAttrib("node")))

print(attribSize(groupTagAttrib("way")))
print(uniqTagValues(groupTagAttrib("way")))