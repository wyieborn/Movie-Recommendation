import streamlit as st
from jina.logging.profile import TimeContext

from recommendation import item_recommend

from service import load_data, view_products, view, get_top_movies,view_recommended_products ,view_watched_products, get_watched_movies,get_user_details,get_recommended_movie_details
from redis_service import  get_movie_details_by_id

#clear resources like saved index id in cache at the startup.
st.cache_resource.clear()

st.title('Recommendations based on Redis using Collaborative Filtering Algorithm.')


with st.spinner(text='Loading and indexing data...'):
    # load the required data into the database
    load_data()
    pass


# we dont have user meta data and only 672 users ratings are present in the data, so just taking first 672 user ids
# make sure to fetch them from redis like we did for movies if you have real users.
# we are interested in ratings by user and to maintain that relation for recommending products. For loading user metadata directly if we dont have any
# $ curl -s https://raw.githubusercontent.com/RediSearch/redisearch-getting-started/master/sample-app/redisearch-docker/dataset/import_users.redis | redis-cli -h localhost -p 6379 --pipe

users_id = ['none'] # if no user id i.e. only show top rated movies
users_id = users_id + ["user:{}".format(i) for i in range(1,672)]


#Side bar functions from here
st.sidebar.header("Filters")
with st.sidebar:
    
    user = st.selectbox(
        "select user",
        users_id
    )


if user != "none" :
    user_id = user.split(':')
    user_id = user_id[1]
    dict_user = get_user_details(user_id)
    f_name = dict_user['first_name']
    l_name = dict_user['last_name']
    email = dict_user['email']
    u_cols = st.columns(2)
    with u_cols[0]:
        st.write('Welcome, {} {}'.format(f_name, l_name))
    with u_cols[1]:
        st.write('Email : {}'.format(email))
    
    

#watched movies
if user not in ('new user','none'):
    user_id = user.split(':')
    user_id = user_id[1]        
    st.subheader('Watched Movies')
    watched_products = get_watched_movies(user_id)
    # print('from get watched movies\n',len(watched_products))
    view_watched_products(watched_products)

    
with TimeContext('Loading From Redis : The execution time '):
    products = get_top_movies('idx:movie')
    #watched movies
    if user not in ('new user','none'):
        user_id = user.split(':')
        user_id = user_id[1]
        
        #recommended movies
        itembased = item_recommend(user_id)
        recommended_product = get_recommended_movie_details(itembased)

    
    
    
if st.session_state.get('product'):
    id = st.session_state.get('product').split(":")[1]
    doc = get_movie_details_by_id(id,[])
    # set the view for selected product
    view(st.session_state.get('product'), doc)



#watched movies
if user not in ('new user','none'):
    
    st.subheader('Recommended Movies')
    view_recommended_products(recommended_product)
    
else :
    #Top rated movies for others

    st.subheader('Top Rated Movies')
    view_products(products)
    


