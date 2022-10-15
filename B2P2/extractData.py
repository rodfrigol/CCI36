import xml.etree.ElementTree as ET
# https://www.geeksforgeeks.org/xml-parsing-python/
import xmltodict
# https://docs.python-guide.org/scenarios/xml/

PATH = "C:/Users/alexa/Desktop/"
FILEPATH = PATH + "cci36lab2.dae"


# turn xml from file to dict
with open(FILEPATH) as fd:
    doc = xmltodict.parse(fd.read())
