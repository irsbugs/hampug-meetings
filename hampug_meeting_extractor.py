#!/usr/bin/env python3
#
# hampug_meeting_extractor.py
#
# This uses lxml. Another option is to use Beautiful Soup
# 
# Get the text of the README.md files on github.com/hampug/meetings/
# The text is in the "<article class"
# Get a selection of fields of text from Hampug meetup.com 
#
# Provides enumerated output. More suitable for entering into a database?
#
# NOTE: From time to time need to added date updates to meeting_list and 
# meetup_list
# Ian Stewart - 2019-08-13
# v 0.1
# TODO: Add try/except on reading from the network. Link might drop out?
# TODO: Add a 0 to the menu to allow sys.exit().

import sys
if sys.version_info[0] < 3:
    sys.exit("Use python version 3 or higher.")
if not sys.platform == 'linux':
    sys.exit("Use the Linux operating system.")

import json
import datetime
from urllib.request import urlopen

try:
    import lxml.etree
except:
    sys.exit("Please install python3-lxml.")
import lxml.html

FILENAME = "hampug_meetings_as_text.txt"

HEADING = "\nHamPUG - Meetings README.md and Meetup data extractor."

# Meeting Readme list. Each url has unique date. E.g
# https://github.com/HamPUG/meetings/blob/master/2014/2014-02-24/README.md
meeting_list = [
"2014-02-24", "2014-03-10", "2014-04-14", "2014-05-12", "2014-06-09", 
"2014-07-14", "2014-08-18", "2014-09-08", "2014-10-13", "2014-11-10", 
"2014-12-08", "2015-02-09", "2015-03-09", "2015-04-13", "2015-05-11", 
"2015-06-08", "2015-07-13", "2015-08-10", "2015-09-14", "2015-10-12", 
"2015-11-09", "2015-12-14", "2016-02-08", "2016-03-14", "2016-04-11", 
"2016-05-09", "2016-06-13", "2016-07-11", "2016-08-08", "2016-09-12", 
"2016-10-10", "2016-11-14", "2016-12-13", "2017-02-13", "2017-03-13", 
"2017-04-10", "2017-05-08", "2017-06-12", "2017-07-10", "2017-08-10", 
"2017-09-11", "2017-10-09", "2017-11-13", "2017-12-11", "2018-02-12", 
"2018-03-12", "2018-04-09", "2018-05-14", "2018-06-11", "2018-07-09", 
"2018-08-13", "2018-09-10", "2018-10-08", "2018-11-12", "2018-12-10", 
"2019-02-11", "2019-03-11", "2019-04-08", "2019-05-13", "2019-06-10", 
"2019-07-08", "2019-08-12",
]
# Dates for future 2019 meetings:
# "2019-09-09", "2019-10-14", "2019-11-11", "2019-12-09"

# Meetup list. Each url has unique 9 digit numbers. E.g.
# "https://www.meetup.com/NZPUG-Hamilton/events/257167804/"
meetup_list = [
None,        None,        None,        None,        "184039822", 
"188129822", "191060772", "205610462", "207445012", "217865632", 
"219010290", "219969265", "219969369", "221555770", "221556439", 
"222463877", "222854991", "223956800", "225102434", "225527752", 
"226406966", "227301648", "228357979", "228716393", "230234718", 
"230891995", "231705578", "232069960", "232669230", "233693633", 
"234493057", "234493069", "234493075", "236199923", "236199979", 
"236199988", "236200009", "236200052", "236200062", "236200072", 
"236200087", "236200140", "236200286", "236200332", "246856247", 
"246856414", "246856479", "246856525", "246856547", "246856561", 
"246856596", "246856780", "246856789", "246856804", "246856818", 
"257167593", "257167776", "257167787", "257167798", "257167804", 
"257167871", "257167812",
]

help_text = """
Usage: hampug_meeting_extractor [OPTIONS]
 
Displays the github.com/meetings/ README.md as text
Also displays meetup.com details as text

[OPTIONS]
    -h --help   Display this help menu
    -m --menu   Menu to select a single meeting 
    -o --output [FILENAME]
"""

def query_user_menu(menu_list, prompt=None, default=1):
    # User selects from a list. Return an index into the list
    if len(menu_list) == 0:
        return -1
    print()
    for index, item in enumerate(menu_list):
        print("{:>3}. {}".format(index + 1, item))
    if prompt == None:
        prompt = ("\nEnter the number of the item [{}]: "
                .format(default))
    else:
        prompt = ("\n{} [{}]: ".format(prompt, default))

    while True:     
        response = input(prompt)
        if response == "": response = default
        try:
            response = int(response)
            if response < 1 or response > len(menu_list):
                print("Invalid.  Requires a value between {} and {}"
                    .format(1, len(menu_list)))
                continue
            else:
                return response - 1
        except ValueError as e:
            print("Value Error. Requires a value between {} and {}"
                    .format(1, len(menu_list)))
            continue


def get_meetup_text(url):
    """
    Using the meetup.com url get selected fields of text data
    scripts = root.xpath('//script') is a list of about 14 items
    script = scripts[2] Item with index of 2 has desired content.
    E.g. of meetup url:
    "https://www.meetup.com/NZPUG-Hamilton/events/257167804/"
    """
    html = urlopen(url).read()
    root = lxml.html.fromstring(html)  
    scripts = root.xpath('//script')

    # Script with index of 2 (out of 14) has desired content.
    script = scripts[2] #.text_content()
    #print(script) # <Element script at 0x7f71b699ca48>
    #print("type(script): ", type(script)) 
    # type(script):  <class 'lxml.html.HtmlElement'>

    # convert json to a dictionary
    content_dict = json.loads(script.text_content())

    s = "{}\n".format(content_dict["name"])
    s += "{}\n".format(content_dict["location"]["name"])
    # Convert date to format: 2019-07-08 7PM 
    meetup_date = content_dict["startDate"].split("+")[0]
    dt = datetime.datetime.strptime(meetup_date, "%Y-%m-%dT%H:%M")
    #dt = dt.strftime("%Y-%m-%d %H:%M")
    #print(dt.strftime("%Y-%m-%d %-I%p")) # 2019-07-08 7PM  
    s += "{}\n".format(dt.strftime("%Y-%m-%d %-I%p"))
    s += "{}\n".format(content_dict["description"])

    #print("Description:\n{}".format(d["description"]))
    #print(content_dict["name"])
    #print(content_dict["location"]["name"]) # MS4.G.02
    #print(content_dict["startDate"])
    #dt = dt.strftime("%Y-%m-%d %H:%M")
    #print(dt.strftime("%Y-%m-%d %-I%p")) # 2019-07-08 7PM
    #print(dt) # 2019-07-08 7PM
    #print(content_dict["description"])
    return s


def get_readme_text(url):
    """
    Extract the text of the meetings README.md which is in the <article class
    E.g. articles = root.xpath('//article')
    Example of url:
    # https://github.com/HamPUG/meetings/blob/master/2014/2014-02-24/README.md
    """
    html = urlopen(url).read()  
    root = lxml.html.fromstring(html) 
    articles = root.xpath('//article')
    article = articles[0]

    s = ""
    for index, item in enumerate(article):
        #print(type(item))  # Each one is <class 'lxml.html.HtmlElement'>
        #print(len(item))  # 1, 1, 1, 0
        #print("\n\n")
        #print(dir(item))
        # Prints the 4 x elements of text...
        #print("{}. {}".format(index, item.text_content())) 
        s += "{}. {}\n".format(index, item.text_content())

    return s


def get_url_list(): 
    """
    Based on the meeting_list create the url's for extracting the README.md
    Return list of urls.
    Examples:
    https://github.com/HamPUG/meetings/blob/master/2014/2014-02-24/README.md
    https://github.com/HamPUG/meetings/blob/master/2019/2019-07-08/README.md
    """
    s1 = "https://github.com/HamPUG/meetings/blob/master/"
    s2 = "/README.md"

    meeting_url_list = []
    for date in meeting_list:
        year = date.split("-")[0]
        url = "{}{}/{}{}".format(s1, year, date, s2)
        #print(url)
        meeting_url_list.append(url)       

    """
    For meetup the urls are of the format:
    "https://www.meetup.com/NZPUG-Hamilton/events/257167804/"
    Note that for 2014 Feb to May (4 x meetings) there is no meetup.
    """
    s1 = "https://www.meetup.com/NZPUG-Hamilton/events/"
          
    meetup_url_list = []
    for value in meetup_list:
        url = "{}{}/".format(s1, value)
        #print(url)
        meetup_url_list.append(url)

    return meeting_url_list,  meetup_url_list    


def help():
    print(help_text)


def menu():
    """
    Make a call to query_user_menu() function is used to select a specific 
    date of one meeting. Output is only to console
    """
    print("Selection of a meeting via a menu\n")
    prompt = "Select date of meeting"
    index = query_user_menu(meeting_list, prompt)
    # Meeting README.md is retrieved
    meeting_url_list,  meetup_url_list = get_url_list()
    meeting_text = get_readme_text(meeting_url_list[index]) 
    print("\n***** Meeting: {} *****\n\n{}"
                    .format(index + 1, meeting_text))
    # Meetup details retrieved
    if meetup_list[index] != None:
        url_meetup = meetup_url_list[index]
        meetup_text = get_meetup_text(url_meetup)
        print("\n***** Meetup: {} *****\n\nurl ID: {}\n{}"
            .format(index + 1, meetup_list[index], meetup_text))
    else:
        meetup_text = "No meetup data for this meeting"
        print("\n***** Meetup: {} *****\n\n{}\n"
            .format(index + 1, meetup_text))   
    sys.exit()


def output_to_console():
    """
    Get the full url's for the README.md files
    Poll github and for each meeting extract the README.md text 
    """
    print("Meeting list is from {} to {}, a total of {} meetings.".
            format(meeting_list[0],  meeting_list[-1], len(meeting_list)))

    # Get the list with the full url's for the README.md files.
    meeting_url_list,  meetup_url_list = get_url_list()

    for index, url in enumerate(meeting_url_list):
        meeting_text = get_readme_text(url) 
        print("\n***** Meeting: {} *****\n\n{}"
                .format(index + 1, meeting_text))

        # Compensate for initial 4 x meetings not having meetup
        #print(meetup_list[0]) # <-- None
        if meetup_list[index] != None:

            url_meetup = meetup_url_list[index]
            #print(url_meetup)
            meetup_text = get_meetup_text(url_meetup)
            print("\n***** Meetup: {} *****\n\nurl ID: {}\n{}"
                .format(index + 1, meetup_list[index], meetup_text))
        else:
            meetup_text = "No meetup data for this meeting"
            print("\n***** Meetup: {} *****\n\n{}\n"
                .format(index + 1, meetup_text))                

        print("=" * 80)


def output_to_file(filename=FILENAME):
    """
    Write output to a text file
    If user doesn't supply filename then use default FILENAME
    """
    print("Meeting list is from {} to {}, a total of {} meetings.".
            format(meeting_list[0],  meeting_list[-1], len(meeting_list)))
    # Get the list with the full url's for the README.md files.
    meeting_url_list,  meetup_url_list = get_url_list()
    print("Writing text of all meetings to the file: {}".format(filename))
    with open(filename, "w") as fout:
        for index, url in enumerate(meeting_url_list):
            meeting_text = get_readme_text(url)
            print("Progress: {} of {}"
                    .format(index + 1, len(meeting_url_list)))
            fout.write("\n***** Meeting: {} *****\n\n{}"
                    .format(index + 1, meeting_text))

            # Compensate for initial 4 x meetings not having meetup
            #print(meetup_list[0]) # <-- None
            if meetup_list[index] != None:

                url_meetup = meetup_url_list[index]
                #print(url_meetup)
                meetup_text = get_meetup_text(url_meetup)
                fout.write("\n***** Meetup: {} *****\n\nurl ID: {}\n{}"
                        .format(index + 1, meetup_list[index], meetup_text))
            else:
                meetup_text = "No meetup data for this meeting"
                fout.write("\n***** Meetup: {} *****\n\n{}\n"
                        .format(index + 1, meetup_text))                

            fout.write("\n" + "=" * 80 + "\n")

    print("Review text of all meetings in the  file: {}".format(filename))


def main():
    """ 
    Call function based on input from command line.
    """
    # pop(0) - Remove program name:
    sys.argv.pop(0)

    if len(sys.argv) == 0:
        output_to_console()

    if len(sys.argv) == 1:
        if sys.argv[0] == "-o" or sys.argv[0] == "--output":
            output_to_file()

        if sys.argv[0] == "-m" or sys.argv[0] == "--menu":
            menu()

        if sys.argv[0] == "-h" or sys.argv[0] == "--help":
            help()

    if len(sys.argv) == 2:
        if sys.argv[0] == "-o" or sys.argv[0] == "--output":
            # User over-rides the default filename
            output_to_file(sys.argv[1])


if __name__ == "__main__":
    print(HEADING)
    main()

"""
Notes:

github.com/hampug/meetings extraction notes:

The url's returned html has an "<article class" which contains the text of 
README.md. For example:

<article class="markdown-body entry-content p-3 p-md-6" itemprop="text">
 <h1>
  <a aria-hidden="true" class="anchor" href="#2014-02-24" id="user-content-
    2014-02-24">
   <svg aria-hidden="true" class="octicon octicon-link" height="16" 
     version="1.1" viewbox="0 0 16 16" width="16">
    <path d="M4 9h1v1H4c-1.5 0-3-1.69-3-3.5S2.55 3 4 3h4c1.45 0 3 1.69 3 3.5 0 
      1.41-.91 2.72-2 3.25V8.59c.58-.45 1-1.27 1-2.09C10 5.22 8.98 4 8 4H4c-.
      98 0-2 1.22-2 2.5S3 9 4 9zm9-3h-1v1h1c1 0 2 1.22 2 2.5S13.98 12 13 
      12H9c-.98 0-2-1.22-2-2.5 0-.83.42-1.64 1-2.09V6.25c-1.09.53-2 1.84-2 
      3.25C6 11.31 7.55 13 9 13h4c1.45 0 3-1.69 3-3.5S14.5 6 13 6z" 
      fill-rule="evenodd">
    </path>
   </svg>
  </a>2014-02-24  <--- (SOME TEXT)
 </h1>

 <h4>
  <a aria-hidden="true" class="anchor" href="#1" id="user-content-1">
   <svg aria-hidden="true" class="octicon octicon-link" height="16" 
     version="1.1" viewbox="0 0 16 16" width="16">
    <path d="M4 9h1v1H4c-1.5 0-3-1.69-3-3.5S2.55 3 4 3h4c1.45 0 3 1.69 3 3.5 0 
      1.41-.91 2.72-2 3.25V8.59c.58-.45 1-1.27 1-2.09C10 5.22 8.98 4 8 4H4c-
      .98 0-2 1.22-2 2.5S3 9 4 9zm9-3h-1v1h1c1 0 2 1.22 2 2.5S13.98 12 13 
      12H9c-.98 0-2-1.22-2-2.5 0-.83.42-1.64 1-2.09V6.25c-1.09.53-2 1.84-2 
      3.25C6 11.31 7.55 13 9 13h4c1.45 0 3-1.69 3-3.5S14.5 6 13 6z" fill-rule="evenodd">
    </path>
   </svg>
  </a>1  <--- (SOME TEXT)
 </h4>

 <h2>
  <a aria-hidden="true" class="anchor" href="#initial-meeting-of-hamilton-
    python-user-group---hampug" id="user-content-initial-meeting-of-hamilton-
    python-user-group---hampug">
   <svg aria-hidden="true" class="octicon octicon-link" height="16" 
     version="1.1" viewbox="0 0 16 16" width="16">
    <path d="M4 9h1v1H4c-1.5 0-3-1.69-3-3.5S2.55 3 4 3h4c1.45 0 3 1.69 3 3.5 0 
      1.41-.91 2.72-2 3.25V8.59c.58-.45 1-1.27 1-2.09C10 5.22 8.98 4 8 4H4c-
      .98 0-2 1.22-2 2.5S3 9 4 9zm9-3h-1v1h1c1 0 2 1.22 2 2.5S13.98 12 13 
      12H9c-.98 0-2-1.22-2-2.5 0-.83.42-1.64 1-2.09V6.25c-1.09.53-2 1.84-2 
      3.25C6 11.31 7.55 13 9 13h4c1.45 0 3-1.69 3-3.5S14.5 6 13 6z" 
      fill-rule="evenodd">
    </path>
   </svg>
  </a>Initial Meeting of Hamilton Python User Group - HamPUG  <-- (SOME TEXT)
 </h2>

 <p>
  The meeting was held a Waikato University Room MS4.G.02.
  We discussed the objectives of the HamPUG group and possible content of 
  presentations to be delivered at future meetings. <-- (MAIN TEXT)
 </p>
</article>

=====

From the above example, this program will extract the following:

$ python3 hampug_meeting_readme_extractor_lxml.py 

Hamilton Python User Group - Meetings README.md extractor.
Meeting list is from 2014-02-24 to 2019-07-08, a total of 58 meetings.

***** Meeting: 1 *****

0. 2014-02-24
1. 1
2. Initial Meeting of Hamilton Python User Group - HamPUG
3. The meeting was held a Waikato University Room MS4.G.02.
We discussed the objectives of the HamPUG group and possible content of presentations to be delivered at future meetings.


***** Meeting: 2 *****

0. 2014-03-10
1. 2
2. Regular Meeting of HamPUG
...

==============================================================================

Meetup data extraction notes: 

10 main keys. Some keys have nested dictionaries.

for key, value in content_dict.items():
    print("\nKey: {}\nValue:{}".format(key, value))


Key: @context
Value:http://schema.org

Key: @type
Value:Event

Key: name
Value:Hamilton Python Meetup

Key: url
Value:https://www.meetup.com/NZPUG-Hamilton/events/257167804/

Key: description
Value:Peter Reutemann will briefly talk about Typing hints, introduced with Python 3.6, and also talk about different kernels for Jupyter Notebooks.

We follow the NZPUG code of conduct to create an inclusive, friendly environment. https://python.nz/Page/42341

We meet in MS4:
https://www.waikato.ac.nz/contacts/map/?MS4

Key: startDate
Value:2019-07-08T19:00+12:00

Key: endDate
Value:2019-07-08T21:00+12:00

Key: location
Value:{'@type': 'Place', 'name': 'MS4.G.02', 'address': {'@type': 'PostalAddress', 'streetAddress': 'University of Waikato', 'addressLocality': 'Hamilton', 'addressCountry': 'New Zealand'}, 'geo': {'@type': 'GeoCoordinates', 'latitude': 0, 'longitude': 0}}

Key: offers
Value:{'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'}

Key: organizer
Value:{'@type': 'Organization', 'name': 'New Zealand Python User Group - Hamilton', 'url': 'https://www.meetup.com/NZPUG-Hamilton/'}

===

Layout of dictionary in scripts[2]:

{
    "@context":"http://schema.org",
    "@type":"Event",
    "name":"Hamilton Python Meetup",
    "url":"https://www.meetup.com/NZPUG-Hamilton/events/257167804/",
    "description":"Peter Reutemann will briefly talk about Typing hints, 
        introduced with Python 3.6, and also talk about different kernels 
        for Jupyter Notebooks.\n\nWe follow the NZPUG code of conduct to 
        create an inclusive, friendly environment. 
        https://python.nz/Page/42341\n\nWe meet in 
        MS4:\nhttps://www.waikato.ac.nz/contacts/map/?MS4",

    "startDate":"2019-07-08T19:00+12:00",
    "endDate":"2019-07-08T21:00+12:00",

    "location":
        {
        "@type":"Place",
        "name":"MS4.G.02",
        "address":
            {
            "@type":"PostalAddress",
            "streetAddress":"University of Waikato",
            "addressLocality":"Hamilton",
            "addressCountry":"New Zealand"
            },
        "geo":
            {
            "@type":"GeoCoordinates",
            "latitude":0,
            "longitude":0
            }
        },

    "offers":
        {
        "@type":"Offer",
        "price":"0",
        "priceCurrency":"USD"
        },
    "organizer":
        {
        "@type":"Organization",
        "name":"New Zealand Python User Group - Hamilton",
        "url":"https://www.meetup.com/NZPUG-Hamilton/"
        }
}

"""

