def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def aggregate(db, pipeline):
    result = db.seattle.aggregate(pipeline)
    return result

def count_all_things(selector=None):
    result = db.seattle.find(selector).count()
    return result


def coffee_shops_grouped_by_name():
    import re
    reg = re.compile(r'coffee|cafe', re.IGNORECASE)
    pipeline = [{'$match': {'cuisine': reg, 'name': {'$ne': None}} },
                          {'$group': {'_id': '$name', 'count': {'$sum': 1}}},
                          {'$sort': {'count': -1}},
                          {'$limit': 10}]
    res = aggregate(db,pipeline)
    return res


if __name__ == '__main__':
    # The following statements will be used to test your code by the grader.
    # Any modifications to the code past this point will not be reflected by
    # the Test Run.
    db = get_db('osm')
    # pipeline = make_pipeline()
    # result = aggregate(db, pipeline)
    all_rows = None
    all_nodes = {'type': 'node'}
    all_ways = {'type': 'way'}
    print count_all_things(all_ways)
    import pprint
   # pprint.pprint(result["result"][0])
