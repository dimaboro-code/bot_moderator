from redis import Redis


rclient = Redis(host='localhost', port=6379, db=0, decode_responses=True)
