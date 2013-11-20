#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!
import json
import HTMLParser
import cgi

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

## GLOBALS ##
loggedIn = False
item = {}
categories = []
user = None

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def updateCurrentItemMap(item_id):
    global item
    current_time = sqlitedb.getTime()   
    item_found = sqlitedb.getItemById(item_id)
    item['id'] = item_found.id
    item['name'] = HTMLParser.HTMLParser().unescape(item_found.name)
    item['current_bid'] = item_found.current_bid
    item['buy_price'] = item_found.buy_price
    item['first_bid'] = item_found.first_bid
    item['num_bids'] = item_found.num_bids
    item['start'] = item_found.start
    item['end'] = item_found.end
    item['user_id'] = item_found.user_id
    item['description'] = HTMLParser.HTMLParser().unescape(item_found.description)
    if (string_to_time(str(item_found.end)) < string_to_time(str(current_time)) or (item_found.current_bid >= item_found.buy_price and item_found.buy_price is not None) or string_to_time(str(item_found.start)) > string_to_time(str(current_time))):
        item['isOpen'] = False
        # Need to account if the query does not return anything!
        item['winner'] = sqlitedb.getAuctionWinner(item['id'])
    else:
        item['isOpen'] = True

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################


urls = ('/', 'index',
        '/find', 'find',
        '/currtime', 'curr_time',
        '/selecttime', 'select_time',
        '/search', 'search',
        '/signup', 'signup',
        '/bid', 'bid',
        '/browse', 'browse',
        '/logout', 'logout',
        '/user', 'user'
        # TODO: add additional URLs here
        # first parameter => URL, second parameter => class name
        )

class index:
    def GET(self):
        global user
        global loggedIn
        return render_template('home.html', loggedIn = loggedIn, user = user)
    def POST(self):
        global loggedIn
        global user
        post_params = web.input()
        user = post_params['username']
        password = post_params['password']
        if (sqlitedb.validUser(user) and sqlitedb.validPassword(user,password)):
            loggedIn = True
        return render_template('home.html', loggedIn = loggedIn, user = user)

class logout:
    def GET(self):
        global loggedIn
        global user
        loggedIn = False
        return render_template('home.html', loggedIn = loggedIn, user = user)

class user:
    def get(self):
        global loggedIn
        global user
        userInfo = sqlitedb.getUser(user)
        return render_template('user.html', loggedIn = loggedIn, user = user, userInfo = userInfo)


class signup:
    # TODO: FINISH THIS
    def GET(self):
        return render_template('signup.html')
    def POST(self):
        global loggedIn
        global user
        post_params = web.input()
        username = post_params['username']
        password = post_params['password']
        location = post_params['location']
        country = post_params['country']
        if(sqlitedb.insertNewUser(username, password, location, country)):
            user = username
            loggedIn = True
            return render_template('home.html', loggedIn = loggedIn, user = user)
        else:
            print "oh no"
            # User exists!




class curr_time:
    # A simple GET request, to '/currtime'
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        current_time = sqlitedb.getTime()	
        return render_template('curr_time.html', time = current_time, loggedIn = loggedIn, user = user)

class select_time:
    # Aanother GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('select_time.html', loggedIn = loggedIn, user = user)

    # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests
    def POST(self):
        post_params = web.input()
        MM = post_params['MM']
        dd = post_params['dd']
        yyyy = post_params['yyyy']
        HH = post_params['HH']
        mm = post_params['mm']
        ss = post_params['ss'];
        enter_name = post_params['entername']

        selected_time = '%s-%s-%s %s:%s:%s' % (yyyy, MM, dd, HH, mm, ss)
        sqlitedb.updateCurrentTime(selected_time)
        update_message = '(Hello, %s. Previously selected time was: %s.)' % (enter_name, selected_time)
        # TODO: save the selected time as the current time in the database
        # Here, we assign `update_message' to `message', which means
        # we'll refer to it in our template as `message'
        return render_template('select_time.html', message = update_message, loggedIn = loggedIn, user = user)

class find:
    def GET(self):
        return render_template('find.html', item = None, loggedIn = loggedIn, user = user)
    def POST(self):
        global item
        post_params = web.input()
        item_found = None
        if (post_params['item-id'] is not None):
            item_id = post_params['item-id']
            item_found = sqlitedb.getItemById(item_id)
        #TODO: Auction closed boolean
        if(item_found is None):
            return render_template('search.html', item = None, loggedIn = loggedIn, user = user)
        else:
            updateCurrentItemMap(item_id)
            return render_template('search.html', item = item, loggedIn = loggedIn, user = user)

class search:
    def GET(self):
        global item
        return render_template('search.html', item = item, loggedIn = loggedIn, user = user)
    def POST(self):
        global item
        return render_template('bid.html', item = item, loggedIn = loggedIn, user = user)

class bid:
    def GET(self):
        global item
        return render_template('bid.html', item = item, loggedIn = loggedIn, user = user)
    def POST(self):
        global item
        post_params = web.input()
        item_id = post_params['item-id']
        bid_amt = post_params['bid']
        bidder = post_params['bidder']
        current_time = sqlitedb.getTime()   
        # use user testuser1        
        sqlitedb.enterBid(item_id, bid_amt, current_time, bidder)
        updateCurrentItemMap(item_id)
        return render_template('bid.html', item = item, loggedIn = loggedIn, user = user)

class browse:
    def GET(self):
        global categories
        global itemsPerPage
        allItems = sqlitedb.getAllItems()
        allCategories = sqlitedb.getAllCategories()
        for category in allCategories:
            name = HTMLParser.HTMLParser().unescape(category.name)
            categories.append(name)
        return render_template('browse.html', allItems = allItems, allCategories = json.dumps(categories), loggedIn = loggedIn, user = user)
    def POST(self):
        global categories
        global itemsPerPage
        post_params = web.input()
        category = cgi.escape(post_params['category'])
        status = post_params['status']
        price = post_params['price']
        superSet = sqlitedb.findSuperSet(category, status, price)
        return render_template('browse.html', allItems = superSet, allCategories = json.dumps(categories), loggedIn = loggedIn, user = user)



###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()
