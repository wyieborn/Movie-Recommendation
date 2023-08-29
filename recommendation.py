from redis_service import get_connection
import random
import numpy as np

def get_rms(user,user_same_item, redis_client):
    #calculating rms for the above intersection set created
    rms_dict = {}
    for i in user_same_item:
        compared_user = i[0].decode()
        values = redis_client.zrange('rms:{}:{}'.format(user, compared_user),0,-1,withscores = True)
        if values:
            sum = 0
            for v in values :
                sum += v[1]**2
            rms = np.sqrt(sum/len(values))
            rms_dict[compared_user] = rms
            
    filt_rms = dict()
    for k,v in rms_dict.items():
        if v <= 1 :
            filt_rms[k] = v
    return filt_rms

def item_recommend(user):
    redis_client = get_connection()
    user_movies = redis_client.zrange('user:{}:movie'.format(user),0 ,-1, withscores = True) #gets list of movies and ratings in tuples


    movie_key_list = ["movie:{}:user".format(m[0].decode()) for m in user_movies]

    redis_client.zunionstore('user:{}:same_items'.format(user), movie_key_list)

    user_same_item = redis_client.zrange('user:{}:same_items'.format(user),0,-1,withscores = True)
    
    #just to check similar users with RMS
    # With pipeline
    pipeline = redis_client.pipeline()
    
    # user = 'user1'
    # complete_one_query = 'zinterstore rms:user1:user5 2 user1 user2 weights 1 -1'
    #saving every user intersection and sum to aggregate the sorted set
    for i in user_same_item:
        compared_user = i[0].decode()
        make_query = 'zinterstore rms:{}:{} 2 user:{}:movie user:{}:movie weights 1 -1'.format(user, compared_user, user, compared_user)
        pipeline.execute_command(make_query)

    pipeline.execute()
    
    filtered_user = get_rms(user,user_same_item,redis_client)

    ##above we can see the user5 is more similar to user3 than any other user
    # However, for our calculations, we will choose RMS values less than or equal to 1. 
    # Therefore, we will consider the ratings all similar users
    #all common users index
    set_list = [] 
    #saving every user intersection and sum to aggregate the sorted set
    for i in filtered_user:
        compared_user = i
        set_list.append('user:{}:movie'.format(compared_user))

    redis_client.zunionstore('recommend:{}'.format(user),set_list, aggregate = 'Min')

    all_recommendations = redis_client.zrange('recommend:{}'.format(user), 0 ,-1,withscores = True) #usage = recommend: <user id> 

    
    if len(all_recommendations)>=100:
        top_rec = all_recommendations[-20:-1]
        # getting the random top recommendations
        random.shuffle(top_rec)
    
    else:
        top_rec = all_recommendations
        random.shuffle(top_rec)
    
    return top_rec
