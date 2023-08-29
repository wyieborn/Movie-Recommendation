import streamlit as st
import time
import numpy as np
import functools
from jina.logging.profile import TimeContext


st.set_page_config(page_title="Recommendation Demo")

st.sidebar.header("Filters")


st.markdown(
            """
                Experience personalized movie recommendations with our real-time movie recommendation system powered by Redis and Collaborative Filtering.
                By harnessing the power of collaborative filtering algorithms, we analyze user preferences and behaviors to generate accurate and dynamic movie suggestions in the blink of an eye. 
                Redis's lightning-fast performance ensures seamless real-time updates, ensuring that users receive tailored recommendations that align perfectly with thier taste, 
                creating a truly immersive and captivating movie-watching journey. 😊
            """
            )

users = ['none','new user','snow', 'fire', 'rain','thunder']
with st.sidebar:
    
    user = st.selectbox(
        "select user",
        users
    )

if user=='new user':
    genres = ['action', 'romance','comedy','thriller']
    release_years = [1980,2000,2001,2010,2015]
    overall_ratings = [5.0,7.0,8.5,7.5,6.0]

    with st.sidebar:
    
        genre = st.selectbox(
            "select genre",
            genres
        )
        
        min_year, max_year = st.slider("movie in year", min_value=1980, max_value=max(release_years), value=(1980, max(release_years)))
        min_overal_ratings, max_overal_ratings = st.slider("overal ratings", min_value=5.0, max_value = max(overall_ratings), value=(5.0, max(overall_ratings)))
        
    st.markdown("# Lets quickly set you up before starting.")


    st.write(
        """
            
            - Please select at least two filters from the genre or different types of movies you like \n
            - you can also search directly for the movies you like below.\n 
        """

    )
else :
    st.markdown("# Redis Search Demo")
    

with TimeContext('Retrieving products'):
    products = []
    pass
    # products = recommend(st.session_state.get('view_history', []), redis_da, color=color, category=category,
    #                      country=country, min_width=min_width, max_width=max_width, min_height=min_height,
    #                      max_height=max_height, k=st.session_state.get('k', 10))
    
    
    
#refactor later

def get_movie_by_index(index, query):
    """_summary_

    Args:
        index (string): index to search
        query (string): search query

    Returns:
        redisearch.result.Result: list of documents under docs and its available fields.
    """
    from redisearch import Client

    search_client = Client('idx:movie')
    search_result = search_client.search(query)
    return search_result



    
# get_movie_by_index('idx:movie','war')   

def view(product_id: str, doc):
    image_column, info_column = st.columns(2)
    # doc = da[product_id]
    try:
        if doc.poster:
            image_column.image(doc.poster)
    except:
        pass
    try:
        if doc.title:
            info_column.write(f'Title: {doc.title}')
    except:
        pass
    try:
        if doc.release_year:
            info_column.write(f'Released Year: {doc.release_year}')
    except:
        pass
    try:
        if doc.genre:
            info_column.write(f'Genre: {doc.genre}')
    except:
        pass
    try:
        if doc.rating:
            info_column.write(f'Rating: {doc.rating}')
    except:
        pass
    try:
        if doc.votes:
            info_column.write(f'Votes: {doc.votes}')
    
    except:
        pass
    
    
    try:
        if doc.plot:
            info_column.write(f'Plot Summary: {doc.plot}')
    except:
        pass
    

    # del st.session_state['product']
    
def set_viewed_product(product, k: int = 10):
    #get called when view image is clicked
    # print('\nfrom set viewed product \n',product)

    st.session_state['product'] = product.id
    view_history = st.session_state.get('view_history', [])
    view_history.insert(0, product)
    view_history = view_history[:k]
    st.session_state['view_history'] = view_history
    
def view_products(docs, k: int = 10):
    columns = st.columns(k)
    # print('one value of a columns container \n',len(docs))

    for doc, column in zip(docs[:k], columns):
        # print('one value of a columns container \n',column)
        # print('\n here in zip fucntion \n')
        container = column.container()
        container.button('view', on_click=functools.partial(set_viewed_product, product=doc, k=k), key=doc.id)
        container.image(doc.uri, use_column_width='always')


movies = ['avatar', 'fast', 'avenger', 'dictator']

search_movie = st.text_input('Search for a movie')

if st.button('Search') or search_movie:
    if search_movie :
        results = get_movie_by_index('idx:movie',search_movie)
        
        try :
            if results.total>0:
        
                view(results.docs[0].id, results.docs[0])
            else:
                'No movies found'
        except:
            'No movies found'
            pass




    
    

    



    
# filtered_options = [option for option in movies if search_movie.lower() in option.lower()]
# # Display the filtered options in real-time
# if search_movie:
#     for option in filtered_options:
#         st.write(option)