import functools
import os

import numpy as np
from docarray import DocumentArray, Document
import streamlit as st
import redis
from redis_service import get_top_rated_movies, get_all_users, get_user_movies, get_movie_details_by_id, get_user_details_by_id, save_poster
from seeding import load_all

import json
import requests


@st.cache_data(persist=True)
def load_data():
    load_all()    
    
    
def get_image(movie_id):
    
    
    url = "https://api.themoviedb.org/3/movie/{}/images?api_key=9769c00def3562ef2d9d8ca081bb44ac".format(movie_id)

    headers = {"accept": "application/json"}

    response = requests.get(url, headers=headers)
    try :
    
        if response.text :

            response = json.loads(response.text)

            path = response['backdrops'][0]['file_path']
            path = "https://image.tmdb.org/t/p/w500" + path
            #save url to redis
            # save_poster(path,movie_id)
            return path

        return ''
    except:
        return ''

def filter_movies_with_url(search_result):
    new_list = []
    
    for i in search_result:
        path = ''
        try:
            if i.poster :
                path = i.poster
                new_list.append(i)

        except:
            pass
        if path == '':
            try :
                id = i.id.split(':')[1]
            except:
                id = i['id']
                id = id.split(':')[1]
                pass
            path = get_image(id)
            if path != '' and id != '107406': #some id needs to blocked because of adult content
                try:
                    i.poster = path
                except:
                    i['poster'] = path
            
                new_list.append(i)
    
        if len(new_list)>= 10:
            return new_list
    
    
    return new_list

def get_top_movies(index):

    # get the top movies by rating
    results = get_top_rated_movies(index)    
    # filter for urls
    results = filter_movies_with_url(results)
    # return results that fits in the slot defined    
    return results[:8]

def get_recommended_movie_details(items):
    movies_ = []
    for i in items:
        id = i[0].decode()
        m_dict = get_movie_details_by_id(id,[])
        m_dict['id'] = "movie:{}".format(id)
        movies_.append(m_dict)
    
    results = movies_[:10]
    results = filter_movies_with_url(results)
    return results
    

def get_watched_movies(user_id):
    user_movies = get_user_movies(user_id)
    user_movies = user_movies[::-1]
    movies_ = []
    
    for i in user_movies:
        movie_id = i[0].decode()
        movie_dict = get_movie_details_by_id(movie_id,[])
        movie_dict['id'] = "movie:{}".format(movie_id)
        movies_.append(movie_dict)
    
    results = movies_[:10]
    results = filter_movies_with_url(results)
    return results
    
    
def view(product_id: str, doc):
    image_column, info_column = st.columns(2)
    # doc = da[product_id]
    try:
        if 'poster' in doc:
            image_column.image(doc['poster'])
        else:
            image_column.image(st.session_state['view_history'][0].poster)
        
    except:
        image_column.image(st.session_state['view_history'][0]['poster'])
        pass

    try:
        if doc['title']:
            info_column.write('Title: {}'.format(doc['title']))
    except:
        pass
    try:
        if doc['release_year']:
            info_column.write('Released Year: {}'.format(doc['release_year']))
    except:
        pass
    try:
        if doc['genre']:
            info_column.write('Genre: {}'.format(doc['genre']))
    except:
        pass
    try:
        if doc['rating']:
            info_column.write('Rating: {}'.format(doc['rating']))
    except:
        pass
    try:
        if doc['votes']:
            info_column.write('Votes: {}'.format(doc['votes']))
    
    except:
        pass
    
    try:
        if doc['plot']:
            info_column.write('Plot Summary: {}'.format(doc['plot']))
    except:
        pass
        

    del st.session_state['product']
    



def set_viewed_product(product, k: int = 8):
    #get called when view image is clicked
    st.session_state['product'] = product.id
    

    view_history = st.session_state.get('view_history', [])
    view_history.insert(0, product)
    view_history = view_history[:k]
    st.session_state['view_history'] = view_history
    

def set_viewed_rec_product(product, k: int = 8):    
    # st.session_state['product'] = product.id
    st.session_state['product'] = product['id']
    
    # print('viewing session state\n',st.session_state['product'])

    view_history = st.session_state.get('view_history', [])
    view_history.insert(0, product)
    view_history = view_history[:k]
    st.session_state['view_history'] = view_history
    
    # view(product.id, product)
    

def resize_image(image):
    from PIL import Image
    from io import BytesIO
    r = requests.get(image)
    img = Image.open(BytesIO(r.content))
    resizedImg = img.resize((225, 325), Image.LANCZOS)
    return resizedImg


def view_products(docs, k: int = 8):
    columns = st.columns(k)
    # print('one value of a columns container \n',docs)

    for doc, column in zip(docs[:k], columns):
        # print('one value of a columns container \n',column)
        # print('\n here in zip fucntion \n')
        container = column.container()
        container.button('view', on_click=functools.partial(set_viewed_product, product=doc, k=k), key=doc.id)
        try :
            # image = resize_image(doc.poster)
            image = doc.poster
            container.image(image, use_column_width='always', caption = doc.title)
            # container.image(doc.poster, use_column_width='always', caption = doc.title)
        except:
            container.image( 'https://dribbble.com/shots/3298625-Oops-Website-Error-Page/attachments/9752139?mode=media', use_column_width = 'always')
            pass

def view_recommended_products(docs, k: int = 8):
    columns = st.columns(k)
    # print('one value of a columns container \n',docs)

    for doc, column in zip(docs[:k], columns):
        # print('one value of a columns container \n',column)
        # print('\n here in zip fucntion \n')
        container = column.container()
        container.button('view', on_click=functools.partial(set_viewed_rec_product, product=doc, k=k), key=doc['id'])
        try :
            # image = resize_image(doc['poster'])
            image = doc['poster']
            container.image(image, use_column_width='always', caption = doc['title'] + ' - ' + doc['genre'])
            # container.image(doc.poster, use_column_width='always', caption = doc.title)
        except:
            container.image( 'https://dribbble.com/shots/3298625-Oops-Website-Error-Page/attachments/9752139?mode=media', use_column_width = 'always')
            pass

def view_watched_movies(docs, k: int = 8):
    columns = st.columns(k)
    # print('one value of a columns container \n',docs)

    for doc, column in zip(docs[:k], columns):
        # print('one value of a columns container \n',column)
        # print('\n here in zip fucntion \n')
        container = column.container()
        container.button('view', on_click=functools.partial(set_viewed_product, product=doc, k=k), key=doc.id)
        try :
            # image = resize_image(doc.poster)
            image = doc['poster']
            container.image(image, use_column_width='always', caption = doc.title)
            # container.image(doc.poster, use_column_width='always', caption = doc.title)
        except:
            container.image( 'https://dribbble.com/shots/3298625-Oops-Website-Error-Page/attachments/9752139?mode=media', use_column_width = 'always')
            pass
    
def view_watched_products(docs):
    k = 8
    cols = st.columns(k)

    for doc, column in zip(docs[:k], cols):
        with column:
            # for resizing the image to fit the container
            # image = resize_image(doc['poster'])
            image = doc['poster']
            st.image(image,caption = doc['title']+' - '+doc['genre'])


def get_users():
    # get user details by id
    users = get_all_users()
    dict_u = dict()
    dict_u['none'] = []
    dict_u['new user'] = []
    for i in users.docs:
        dict_u[i.id] = i
    return dict_u

def get_user_details(id):
    dict_user = get_user_details_by_id(id,[])
    return dict_user
    