from redisearch import Client, Query
from redisearch.aggregation import AggregateRequest
import redis

def get_connection():
    # Connect to Redis
    redis_host = 'localhost'
    redis_port = 6379
    redis_db = 0
    redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    return redis_client

redis_client = get_connection()

def save_poster(img,id):
    try :
        redis_client = get_connection()
        
        
        redis_client.hset('movie:{}'.format(id), mapping={
        
            "poster" : img
        })
        # redis_client.execute()
    except Exception as e:
        print('update failed',str(e))
    
    
    redis_client.close()
def get_movie_by_index(index, query):
    """_summary_

    Args:
        index (string): index to search
        query (string): search query

    Returns:
        redisearch.result.Result: list of documents under docs and its available fields.
    """

    search_client = Client('idx:movie')
    search_result = search_client.search(query)
    return search_result

def get_top_rated_movies(index):
    client = Client(index)
    request = client.search('@rating:[8 +inf]')
    return request.docs

def get_all_users(index:str='idx:user'):
    client = Client(index)
    quer = Query("*")#.paging(0,20)
    request = client.search(quer)#get all users
    return request
    
def get_user_details_by_id(user,field_list):
    if not field_list:
        field_list = ['first_name','last_name','email','gender','country','city']
    dict_movie = {}
    user_details = redis_client.hmget('user:{}'.format(user), field_list)
    for i,v in enumerate(field_list):
        if user_details[i]:
            dict_movie[v] = user_details[i].decode()
    return dict_movie
    
def get_user_movies(user):
    user_movies = redis_client.zrange('user:{}:movie'.format(user),0 ,-1, withscores = True) #gets list of movies and ratings in tuples
    return user_movies

def get_movie_details_by_id(id, field_list):
    if not field_list:
        field_list = ['title','genre','rating','release_year','plot','poster']
    dict_movie = {}
    movies_details = redis_client.hmget('movie:{}'.format(id), field_list)
    for i,v in enumerate(field_list):
        if movies_details[i]:
            dict_movie[v] = movies_details[i].decode()
    return dict_movie
        

        
        