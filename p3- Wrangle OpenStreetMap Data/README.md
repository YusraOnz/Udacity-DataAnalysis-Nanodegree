
# OpenStreetMap Data Case Study

### Map Area:
Riyadh, Saudi Arabia

- <a href="https://www.openstreetmap.org/node/315358390">OpenStreetMap</a> <br>
- <a href="https://mapzen.com/data/metro-extracts/metro/riyadh_saudi-arabia/">MapZenL</a>

Riyadh is the capital of Saudi Arabia. It's located at the center of the Arabian Peninsula. It is close to my homeland and a city that i often visit. The spoken languange in Riyadh is Arabic which is my first language. Hence, I was interested to learn more about it and use my culture and domain knowledge to contribute to this area.

<hr>

### Data Inspection
audit.py


I started with reading the OSM file to get a feeling of how data is structured and where to look for problems. I used `tagcount()` function to discover what are the tags expected in this file and check weather the tag names need any wrangling. The following is the output of `tagcount()`:

```
{'bounds': 1,
 'member': 352,
 'nd': 488657,
 'node': 342933,
 'osm': 1,
 'relation': 131,
 'tag': 144543,
 'way': 77699}
```

I used OSM wiki to learn the meaning of each tag name. The tags names seemed to be error-free. I wrote another function `tagNameByLevel()` in order to differentiate the tags by their level.

```
{'node': {'tag'}, 
'way': {'nd', 'tag'}, 
'relation': {'member', 'tag'}}
```

Then, I wrote the `groupTagAttrib()` function to help me audit data by grouping values by their keys. I used the two supporting fucntions , `attribSize()` and `uniqTagValues()`, to facilitate the auditing process. The `attribSize()` helped me audit the size of the keys and gave me a hint of what attriutes are more frequent or important. While the `uniqTagValues()` removes duplicated values to reduce the size of the grouped attribute and make it readible during the data inspection step.


1) Output Sample of attribSize():
```
'created_by': 1, 
'highway': 10, 
'railway': 7, 
'ref': 1, 
'power': 66
```


2) Output Sample of uniqTagValues():
```
'created_by': {'JOSM'}, 
'highway': {'street_lamp', 'mini_roundabout', 'motorway_junction', 'traffic_signals', 'rest_area', 'turning_circle', 'services'}, 
'railway': {'crossing', 'level_crossing', 'switch', 'station'}, 
'ref': {'8'}, 
'power': {'pole', 'tower'}
```

<hr>

## Detected Problems 
The map turned out to be full of inconsistencies. The following are some of the detected problems: 


### Inaccurate names in (name:ar) and (name:en) key attribute:
Both `name:ar` and `name:en` have a semantic meaning of being associated with a specific single language. In this map, the values coresponding to these attributes are in two languages which is semantically wrong. 

##### Arabic Names
```
'name:ar': {'السفارة المصرية','tamimi king abdulla', 'الصحابة', 'شارع غبيرة العام', 'الدائري الحنوبي', 'طريق الامام سعود','Riyadh chambers of commerce and industry king abdullah','Al Yaman'}
```
##### English Names
```
'name:en': {'Al Mughaydir', 'home center',  'مستوصف الممتاز الطبيAl-Momtaz Medical Clinic', 'Mishash al Uqlah'}
```


### Inconsistent and Invalid phone numbers:
One big reason behind phone number inconsitencies is that Saudi Arabia expanded both country code and phone numbers with one digit number. For example: country code used to be 2-digits with this format (0X), but it's changed to 3-digits following this format (01X). Another reason for phone numbers inconsistencies is the flexibility writing the country codes in different formats( 966, +966, 00966) or not writing it at all. The same situation applies to area code where it's optional to write it. The following are the six categories of phone number inconsistencies and exapmles of each: 

- Space Inconsistency
```
'+966 92 002 5678'
'+966112377711' 
```

- Inconsistent Country Code (+966 or 966 or 00966)
` '966114778144' `

- Missing Country Code (+966)
```
'0114455544'
'0503336099'
```

- Invalid Numbers
```
'90000002'
'92000702'
```

- Old Are Codea (01 or +9661 for Riyadh)
```
'+96614196677' 
'+966 1 279 5100' 
```

- Missing Area Code (011 or +96611 for Riyadh)
`'4811111' `


###  Inconsistent and Invalid postcodes:
The standard length of postal codes in Riyadh is five digits. Some post codes in this dataset are less than five which is inaccurate. Also, most postal codes are written using English numbers but others are written in Arabic numbers which make the data inconsistent.

`١١٤٩١, 7069, 0000`

### Inconsistent street names in terms of language used and street type suffix:
auditStreetTypes()... extract and count the street types

##### Language inconsistencies:

-Arabic names:
`'طريق الملك عبدالعزيز', 'فالح بن صغير'`
-English names:
`'Rawdah Park', 'Omar Ibn Al Khattab Rd', 'Abdullah Bin Hazafa As-Shami Road'`

##### Street type inconsistencies:

- Rd, Rd., Road and road
`'Omar Ibn Al Khattab Rd','Khurais Road`

- St, St.,Street and street
`"Al Ma'ather Street", 'Unaiza St.'`

- Missing type
`'Ar Rabi' , 'Ad Diwan', 'Prince Ahmad Bin Salmam Bin Abdul Aziz','ابن ابي التائب'`


### Unnecessarily redundant or possibly erroneous keys:
The following three keys can be combined under single key:
```
'name:ar'
'name:ar1'
'name:arz'
```


<hr>

### Data Cleaning and Transformation
In this section, I worked on three of the detected inconsistensies which are the phone numbers format, street names case and street types. The `cleanStreetName()` function is used to handle street names while `cleanPhoneNumber()` funtion is used handle phone numbers. After cleaning the data, I used `xml_to_csv.py` script to transform the data from a tree format (XML) to a tabular format (CSV) to easily insert it to a database.


### Handling Phone Numbers 
Knowing that phone numbers have structured format, I used regular expression to clean it. Two numbers are found to be exceptionally short. I used the information provided by the map and the internet to find the correct phone numbers.

```
    # mapping of erroneous street types
    mapping = {"90000002": "+966920000002", "92000702": "+966920000702"}
    
    #standard numbers formats in Saudi Arabia
    homeNum_re = re.compile(r'^(00966|\+966|966)?0?1?1?([\d]{7})', re.IGNORECASE)
    mobileNum_re = re.compile(r'^(00966|\+966|966)?0?(5[\d]{8})', re.IGNORECASE)
    uniNum_re = re.compile(r'^(00966|\+966|966)?(9200[\d]{5})', re.IGNORECASE)
    tollFreeNum_re = re.compile(r'^(00966|\+966|966)?(800[\d]{7})', re.IGNORECASE)


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

```

### Handling Street Names
As mentioned earlier, street names are both in English and Arabic. I worked only on cleaning the english names, where i filtered out arabic names using regular expression. 

``` 
arabicText = re.compile(r'^[\u0600-\u06ff\s\u0031-\u0039]+')
if not arabicText.search(streetName):

```
To unify the names case, i used title() function to convert the name's case.

```
for word in streetName:

    # check if the word is not an abbreviation to fix its case
    if not word.isupper():
        streetName[streetName.index(word)] = word.title()
```

To fix the street types, I used a mapping of expected variations of a type and the standard type.

```
mapping = {"St": "Street",
           "St.": "Street",
           "Rd": "Road",
           "Rd.": "Road"}


# return the last item in the list which possibly represent the type
streetType = streetName[-1]

if streetType in mapping:
    # replace the old type with the new one
    streetName[-1] = mapping[streetType]

streetName = ' '.join(streetName)
```


<hr>

## Database Creation and Data Overview

In this step, a database is created programatically from the extrcated CSV files. I queried this database to extract some statistics and get an overview of the data. The `csv_to_db.py` contains the code used to accomplish this step. The following are the information and statistical overview extracted from the databas.

### size of the file


```
OSM files:
riyadh_saudi-arabia.osm (76.6 MB)
riyadh_sample.osm (1.54 MB)
 
The Database:
RiyadhMapDB.db (56.8 MB)

CSV files:
ways.csv (4.50 MB) 
ways_tags.csv (4.45 MB) 
ways_nodes.csv (11.6 MB)
nodes.csv (27.5 MB)
nodes_tags.csv (715 KB)
```

### Number of unique users:
`SELECT COUNT(*) as total FROM (SELECT user FROM nodes UNION SELECT user FROM ways)`

777 User
 

### Number of Nodes :
```
SELECT COUNT(DISTINCT id) FROM nodes;
```

342933 Node


### Number of Ways:
```
SELECT COUNT(DISTINCT id) FROM ways;
```

77699 Way



### Number of node types:
```
SELECT  value, COUNT(DISTINCT id) as count 
FROM nodes_tags 
WHERE key='amenity'
GROUP BY value 
ORDER BY count DESC ;
```

('place_of_worship', 430),
 ('fuel', 258),
 ('restaurant', 246),
 ('parking', 201),
 ('school', 92),
 ('atm', 80),
 ('embassy', 79),
 ('cafe', 78),
 ('fast_food', 75),
 ('bank', 73),
 ('hospital', 55),
 ('pharmacy', 49),
 ('shelter', 27),
 ('car_rental', 25),
 ('post_office', 22),
 ('clinic', 18),
 ('police', 18),
 ('car_wash', 15),
 ('fountain', 14)
 


<hr>

## Additional Data Exploration 
I used the following function to extract interesting statistics of the map nodes. Moreover,  reading the output of the `groupTagAttrib()` function helped me come up with questions about the map. It also helped me structure several SQL queries that answer these questions.

```
def query(var,top):
    
    if top:
        cur.execute('SELECT  value, COUNT(DISTINCT id) as count FROM nodes_tags WHERE key=\''+var+'\' GROUP BY value ORDER BY count DESC LIMIT 7;')
    else:
        cur.execute(var)

    rows = cur.fetchall(var)
    pprint(rows)
```

### Top land use
`query('cuisine',True)`

('regional', 53),
 ('pizza', 15),
 ('burger', 13),
 ('coffee_shop', 7),
 ('chicken', 6),
 ('sandwich', 5),
 ('italian', 4),
 ('american', 3),
 ('indian', 3),
 ('kebab', 3)

### Top land use
`query('landuse',True)`

('military', 3),
 ('retail', 3),
 ('cemetery', 1),
 ('commercial', 1),
 ('industrial', 1),
 ('village_green', 1)

### Top Manufacturers
`query('manufacturer',True)`

('Lockheed', 2),
 ('Boeing', 1),
 ('Douglas', 1),
 ('McDonnell Douglas', 1),
 ('Panavia', 1)

### Top Religions
`query('religions',True)`

('muslim', 418)

### Top Natural Places
`query('natural')`

('peak', 52),
 ('tree', 22),
 ('spring', 17),
 ('cliff', 10),
 ('cave_entrance', 2),
 ('water', 2),
 ('oilfield', 1)


<hr>

## Conclusion
 

The Riyadh OSM was and still is full of problems possibly due to the fact that the map is created by volunteers. The major problem found in this region was language inconsistencies as both Arabic and English are used alternatively. To meet with the project scope, I worked to solve some of the problems which are street types, names case and phone numbers inconsistencies. One of the challenges I faced is to find easy and programatical ways to clean unstructured problems. For example, Riyadh's street names and places don't have a unified format or structure like some other countries does.Hence, cleaning it programatically is a big challenge. Moreover, there is a huge room of improvement and future work. For example, knowing that OSM attribute names are predefined, errors attribute names can be detected by comparing it to the list of the predefined attributes. This list is actually extracted and published in the internet. A possible difficulty with this solution is to optimize the code in terms of running time since the number of comarision needed is large.  Another possible improvement is to utilize the high accuracy of google translate API in detecting language type, misspeled words and words translation to resolve language inconsistencied. PyEnchant API can also be used to find missplellings while fuzzywuzzy API can be used to correct such word. The issue with this solution is that NLP API's are not 100% accurate and result in errors itself. However, this solution might not eliminate the problem, but it greatly reduces it.

<hr>

## References

- Udacity Data Wrangling Course and Discussion Board
- OpenStreetMap wiki
- Wikipedia: <a href="https://en.wikipedia.org/wiki/Telephone_numbers_in_Saudi_Arabia">Telephone numbers in Saudi Arabia</a>
- Wikipedia: <a href="https://en.wikipedia.org/wiki/Arabic_script_in_Unicode">Arabic script in Unicode</a>

