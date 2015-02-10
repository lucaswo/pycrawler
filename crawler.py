# Simple crawler and visualisation for the reddit network
# author: Lucas Woltmann, 2014
#
# Please make sure that you have all the necessary packages installed. Run the script from a terminal with:
# python crawler.py name_of_the_subreddit_or_user number_of_max_steps
# For example:
# python crawler.py r/dataisbeautiful 10

import json
import urllib.request
import re
import sys
import time
from collections import deque
import itertools
#needs to be installed via package manager or as stated here http://matplotlib.org/1.4.2/faq/installing_faq.html
import matplotlib.pyplot as plt
#has to be installed manually (http://networkx.github.io/documentation/latest/install.html)
import networkx

#getting the short path to a subreddit or user
def get_short_description(urlline):
    return urlline.partition('.com/')[2]

def crawl():
    #setting up the frontier and Regex
    start = sys.argv[1]
    frontier = deque([start])
    visitedSites = {}
    connections = {}
    count = 1
    userRegex = re.compile(b'(user/.*?)[\"\?/\,\<\ ]')
    subRedditRegex = re.compile(b'(r/.*?)[\"\?/\,\<\ ]')

    #crawl limited by the frontier or the given upper bound
    while frontier and count<=int(sys.argv[2]):
        #get first item in frontier
        currentItem = frontier.popleft()
        #print(frontier)

        if not currentItem in visitedSites:

            #HTTP request and catching HTTP 429 (too many requests)
            try:
                s = urllib.request.urlopen('http://www.reddit.com/'+currentItem)
            except urllib.error.HTTPError as err:
                if err.code == 429:
                    print('429 occured')
                    time.sleep(3)
                    continue

            #update visited sites
            visitedSites[currentItem] = count

            siteText = s.read()

            #analyse HTML with regex
            nextItems = itertools.chain(re.finditer(subRedditRegex, siteText), re.finditer(userRegex, siteText))

            #update connections from this page
            for i in nextItems:
                i = i.group(1).decode('utf8')

                if currentItem in connections:
                    if not i in connections[currentItem]:
                        connections[currentItem].append(i)
                else:
                    connections[currentItem] = [i]

                #update frontier
                if not i in frontier:
                    frontier.append(i)
            count += 1

        #wait for 3 seconds to avoid traffic and 429's
        time.sleep(3)

    #write graph to file
    myfile = open('crawl.json', mode = 'w')
    json.dump(visitedSites, myfile, indent=4)
    json.dump(connections, myfile, indent=4)

    #draw graph
    G = networkx.DiGraph(connections)
    pos = networkx.spring_layout(G, scale=10.0)
    networkx.draw_networkx_nodes(G, pos, node_size=500, node_color='b', alpha=0.2)
    networkx.draw_networkx_edges(G, pos, alpha=0.2, arrows=False)
    networkx.draw_networkx_labels(G, pos, font_size=8)

    plt.axis('off')
    plt.show()

crawl()
