import numpy as np
import pandas as pd
import ast
from redis_service import get_connection


def load_movies():
    movies_data = pd.read_csv('filt_poster_movie_metadata.csv')
    
    movies_data['vote_average'] = pd.to_numeric(movies_data['vote_average'])
    
    redis_client = get_connection()
    hset_pipe = redis_client.pipeline()
    
    for i,d in movies_data.iterrows():
        genre = ast.literal_eval(d.genres)
        if not genre:
            genre = ''
        else :
            genre = genre[0]['name']
        if d.release_date not in (np.nan,None,''):
            year = d.release_date.split('-')[0]
        else:
            year = ''
        hset_pipe.hset('movie:{}'.format(d.id), mapping={
            'title': d.title,
            'plot' : d.overview,
            "genre": genre,
            "votes": d.vote_count,
            "rating": d.vote_average,
            "release_year" : year,
            "poster" : d.poster
        })
    hset_pipe.execute()
    
    
    redis_client.close()
    
    print('\nsaving movies meta data in Redis task completed \n')
    

def load_ratings():
    user_df = pd.read_csv('filtered_ratings.csv')

    user_ratings = user_df.pivot(index='userId', columns='movieId', values='rating').fillna(0).rename_axis(columns=None,index=None)

    user_ratings_df = user_ratings

    #construct item to user matrix or dict
    item_to_user_df = user_ratings_df.T

    item_to_user_dict = item_to_user_df.to_dict()
    user_to_item_dict = user_ratings.to_dict()

    redis_client = get_connection()
    pipeline = redis_client.pipeline()

    #add user ratings for items by user in redis( 1 movie all users ratings)
    #here we are using item_to_user_dict because the key value pair when converting to dict takes 
    #cols as keys from dataframe
    #user:1:movie 2 1.0 3 2.5 
    for k,v in item_to_user_dict.items():
        try:
            if v.items():
                for i,j in v.items():
                    if j!=0:
                        #add to pipeline for each key and value chekced for 0 ratings
                        pipeline.zadd('user:{}:movie'.format(k), {i:j})
        except:
            print("exception here",k,v)

    pipeline.execute()

    #add user ratings for items by user
    #movie:1:user user:1 5.0 user:2 4.0
    pipeline = redis_client.pipeline()

    for k,v in user_to_item_dict.items():
        try:
            if v.items():
                for i,j in v.items():
                    if j!=0:
    #                     redis_client.zadd('movie:{}:user'.format(k), {i:j})
                        pipeline.zadd('movie:{}:user'.format(k), {i:j})
        except:
            print("exception here",k,v)

    pipeline.execute()
    
    

    print('\nsaving user ratings to redis task completed\n')

def load_user():
    print('\nloading user data \n')
    # redis_client = get_connection()
    pass
    


def create_index():
    redis_connection = get_connection()
    # create_index_movie =  """FT.CREATE idx:movie ON hash PREFIX 1 "movie:" SCHEMA title TEXT SORTABLE release_year NUMERIC SORTABLE rating NUMERIC SORTABLE genre TAG SORTABLE"""
    # redis_client.execute_command(create_index_movie)
    # create_index_user = """FT.CREATE idx:user ON hash PREFIX 1 "user:" SCHEMA gender TAG country TAG SORTABLE last_login NUMERIC SORTABLE location GEO"""
    # redis_client.execute_command(create_index_user)
    
    # redis_connection = redis.StrictRedis(host='localhost', port=6379, db=0)

    # Define the index creation query
    index_query_movie = [
        "idx:movie",
        "ON", "hash",
        "PREFIX", "1", "movie:",
        "SCHEMA", "title", "TEXT", "SORTABLE", "release_year", "NUMERIC", "SORTABLE",
        "rating", "NUMERIC", "SORTABLE", "genre", "TAG", "SORTABLE"
    ]

    # Execute the movie index creation query
    try :
        redis_connection.execute_command("FT.CREATE", *index_query_movie)
    except :
        pass
    
    index_query_user = [
        "idx:user",
        "ON", "hash",
        "PREFIX", "1", "user:",
        "SCHEMA", "gender", "TAG", "country", "TAG", "SORTABLE",
        "last_login", "NUMERIC", "SORTABLE",
        "location", "GEO"
    ]
    
    try:
        redis_connection.execute_command("FT.CREATE", *index_query_user)
    except:
        pass
    
    redis_connection.close()

    
def load_all():
    # load_user() # 
    load_movies()
    load_ratings()
    create_index()
    pass



    
