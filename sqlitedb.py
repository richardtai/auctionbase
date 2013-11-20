import web
import json
import HTMLParser

db = web.database(dbn='sqlite',
        db='cs145.db'
    )

######################BEGIN HELPER METHODS######################

# Enforce foreign key constraints
# WARNING: DO NOT REMOVE THIS!
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')

# initiates a transaction on the database
def transaction():
    return db.transaction()
# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except:
#     t.rollback()
#     raise
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples

# returns the current time from your database
def getTime():
    query_string = 'select * from time'
    results = query(query_string)
    return results[0].time
         
# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!
def getItemById(item_id):
    # TODO: rewrite this method to catch the Exception in case `result' is empty
    query_string = 'select * from items where id = $itemID'
    result = query(query_string, {'itemID': item_id})
    if (not(isResultEmpty(result))):
        query_string = 'select * from items where id = $itemID'
        result = query(query_string, {'itemID': item_id})
        return result[0]
    else:
    	return None 

def makeSet(results):
    resultSet = set()
    for result in results:
        itemMap = {}
        itemMap['id'] = result.id
        itemMap['name'] = HTMLParser.HTMLParser().unescape(result.name)
        itemMap['current_bid'] = result.current_bid
        itemMap['buy_price'] = result.buy_price
        itemMap['num_bids'] = result.num_bids
        itemMap['start'] = str(result.start)
        itemMap['end'] = str(result.end)
        itemMap['user_id'] = result.user_id
        itemMap['description'] = HTMLParser.HTMLParser().unescape(result.description)
        resultSet.add(json.dumps(itemMap))
    return resultSet

def insertNewUser(username, password, location, country):
    t = db.transaction()
    try:
        query_string = 'insert into users (id, rating, location, country, password) values ($username, $rating, $location, $country, $password)'
        query(query_string, {'username': username, 'location': location, 'country': country, 'password': password, 'rating':0} )
    except:
        t.rollback()
        raise
    else:
        t.commit()

# helper method to determine whether query result is empty
# Sample use:
# query_result = sqlitedb.query('select currenttime from Time')
# if (sqlitedb.isResultEmpty(query_result)):
#   print 'No results found'
# else:
#   .....
#
# NOTE: this will consume the first row in the table of results,
# which means that data will no longer be available to you.
# You must re-query in order to retrieve the full table of results
def isResultEmpty(result):
    try:
        result[0]
        return False
    except:
        return True

def validUser(username):
    t = db.transaction()
    try:
        query_string = 'select * from users where id=$name'
        result = query(query_string, {'name': username})
        return not(isResultEmpty(result))
    except:
        t.rollback()
        raise
    else:
        t.commit()

def validPassword(name, password):
    t = db.transaction()
    try:
        query_string = 'select password from users where id=$name'
        result = query(query_string, {'name': name})
        if(result[0].password == password):
            return True
        else:
            return False
    except:
        t.rollback()
        raise
    else:
        t.commit()
# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars = {}):
    return db.query(query_string, vars)

#####################END HELPER METHODS#####################

#TODO: additional methods to interact with your database,
# e.g. to update the current time

def updateCurrentTime(updatedTime):
    t = db.transaction()
    # query_string = 'select * from items where id = $itemID'
    # result = query(query_string, {'itemID': item_id})
    try:
        query_string = 'update time set time = $updatedTime'
        query(query_string, {'updatedTime': updatedTime})
    except:
        t.rollback()
        raise
    else:
        t.commit()

def getAuctionStatus(item_id):
    t = db.transaction()
    try:
        query_string = 'select * from items where id=$itemID'
        result = query(query_string, {'itemID': item_id})
        return result[0].end
    except:
        t.rollback()
        raise
    else:
        t.commit()

def checkUsername(username):
    t = db.transaction()
    try:
        query_string = 'select * from users where id=$username'
        result = query(query_string, {'username': username})
        return isResultEmpty(result)
    except:
        t.rollback()
        raise
    else:
        t.commit()

def enterBid(item_id, bid_amt, current_time, bidder):
    t = db.transaction()
    try:
        # testuser1 is my test user... lol
        query_string = 'insert into bids (item_id, user_id, time, amount) values ($item_id, $user_id, $current_time, $bid_amt)'
        query(query_string, {'item_id':item_id, 'user_id': bidder, 'current_time': current_time, 'bid_amt' : bid_amt})
    except:
        t.rollback()
        raise
    else:
        t.commit()

def getAuctionWinner(item_id):
    t = db.transaction()
    try:
        # testuser1 is my test user... lol
        query_string = 'select * from bids where item_id=$item_id order by id desc limit 1;'
        result = query(query_string, {'item_id':item_id})
        if (not((isResultEmpty(result)))):
            result1 = query(query_string, {'item_id':item_id})
            return result1[0].user_id
        else:
            return None
    except:
        t.rollback()
        raise
    else:
        t.commit()

def getAllItems():
    t = db.transaction()
    try:
        query_string = 'select * from items'
        result = query(query_string)
        return result
    except:
        t.rollback()
        raise
    else:
        t.commit()

def getAllCategories():
    t = db.transaction()
    try:
        query_string = 'select * from categories'
        result = query(query_string)
        return result
    except:
        t.rollback()
        raise
    else:
        t.commit()

def getItemsByCategory(category):
    t = db.transaction()
    try:
        if(category is not None):
            query_string = 'select i.id,i.name,i.current_bid,i.buy_price,i.first_bid,i.num_bids,i.start,i.end,i.user_id,i.description from items i join items_to_categories ic on i.id = ic.item_id join categories c on ic.category_id = c.id where c.name=$category'
            result = query(query_string, {'category': category})
        else:
            query_string = 'select * from items'
            result = query(query_string)
        return makeSet(result)
    except:
        t.rollback()
        raise
    else:
        t.commit()

def getItemsByStatus(status):
    t = db.transaction()
    current_time = getTime()
    try:
        if(status == "status-o"):
            query_string = 'select * from items where end > $current_time'

        else:
            query_string = 'select * from items where end < $current_time '
        result = query(query_string, {'current_time':current_time})
        return makeSet(result)
    except:
        t.rollback()
        raise
    else:
        t.commit()

def getItemsByPrice(price):        
    priceMap = {
                "li-1" : 'current_bid <= 10',
                "li-2" : 'current_bid > 10 and current_bid <= 30',
                "li-3" : 'current_bid > 30 and current_bid <= 50',    
                "li-4" : 'current_bid > 50 and current_bid <= 70',
                "li-5" : 'current_bid > 70 and current_bid <= 90',
                "li-6" : 'current_bid > 50 and current_bid <= 100',
                "li-7" : 'current_bid > 100'                
    }
    t = db.transaction()
    try:
        query_string = 'select * from items where ' + priceMap[price]
        result = query(query_string)
        return makeSet(result)
    except:
        t.rollback()
        raise
    else:
        t.commit()

def findSuperSet(category, status, price):
    allItems = makeSet(getAllItems())
    if (category == ''):
        categorySet = allItems
    else:
        categorySet = getItemsByCategory(category)
    if (status == ''):
        statusSet = allItems
    else:
        statusSet = getItemsByStatus(status)
    if (price == ''):
        priceSet = allItems
    else:
        priceSet = getItemsByPrice(price)
    set1 = categorySet & statusSet & priceSet
    superSet = []
    for item in set1:
        superSet.append(json.loads(item))

    return superSet

def getUser(user):
    t = db.transaction()
    try:
        query_string = 'select * from users where id=$user'
        result = query(query_string, {'user': user})
        print result[0]
        return result[0]
    except:
        t.rollback()
        raise
    else:
        t.commit()

