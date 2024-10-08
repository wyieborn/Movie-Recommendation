# Movie-Recommendation

![image](https://github.com/user-attachments/assets/e54f40b5-4039-446a-aef7-b22289617d40)

Movie Recommendation using Collaborative Filtering, Redis and Docker. The jupyter notebook file "reproduce_redis_recommendation.ipynb" has redis commands for interacting with redis server and recommendations steps breakdown. Please install docker and make sure its running.

-------------------------------------------------------------------------------------------------------------

<img width="1267" alt="Screenshot 2023-07-31 114519" src="https://github.com/wyieborn/Movie-Recommendation/assets/24772740/35d016ad-a7a2-4b38-8ced-d5770bbba734">



# OBJECTIVES

- Data Collection and Preprocessing.
- Collaborative Filtering Implementation.
- Redis Integration.
- Loading and Indexing.
- Real-time Recommendation
- Generation.

![image](https://github.com/user-attachments/assets/35e3aed6-5a94-458d-b4e6-237b30903426)

## Why Redis
Redis is a fast, in-memory data store used for caching and real-time data processing in various applications.

- Real-Time Performance
- Low Latency
- Caching Capabilities
- Ecient Data Structures
- Scalability
- Persistence Options

## COLLABORATIVE FILTERING.
Collaborative Filtering is a recommendation technique that predicts a user's preferences or interests based on the behaviors and preferences of other users. Memory-based CF, also known as neighborhood-based CF, relies on the direct use of user-item interaction data to make recommendations. Model-based CF involves creating predictive models from user-item interactions. These models are typically constructed using machine learning algorithms

![image](https://github.com/user-attachments/assets/ff0a2466-ca01-49d4-a060-997190b2ebbb)

## Example to other use cases

The grocery chain introduces item ratings (1-5) for users. Customers with similar purchases and ratings are grouped, promoting items based on both purchasing behavior and ratings.

![image](https://github.com/user-attachments/assets/cfcebff2-02f4-48f9-9817-bebb5161803d)

![image](https://github.com/user-attachments/assets/5870f794-d50a-4f3c-9331-f842d504ecae)

![image](https://github.com/user-attachments/assets/b474f414-b080-4046-bcec-236f7117f81f)


## Redis and docker steps.

![image](https://github.com/user-attachments/assets/d7c65fab-af44-4601-a9c5-4f0280f7f7f8)

It is recommended to manually index the movie and user after seeding using below commands. 

- FT.CREATE idx:movie ON hash PREFIX 1 "movie:" SCHEMA title TEXT SORTABLE release_year NUMERIC SORTABLE rating NUMERIC SORTABLE genre TAG SORTABLE

- FT.CREATE idx:user ON hash PREFIX 1 "user:" SCHEMA gender TAG country TAG SORTABLE last_login NUMERIC SORTABLE location GEO

![image](https://github.com/user-attachments/assets/1eb07ba6-726d-426f-92c7-9be86c0da608)


## Redis Cli and basic commands

Below are commands for practice and useful when making our application.

sadd, srem, smembers , sunion, sunionstore

![image](https://github.com/user-attachments/assets/a5061f1a-ec4d-4b66-ac7b-d245cc0d5f03)

![image](https://github.com/user-attachments/assets/c1f8bd9f-76c2-45c0-82dd-b095bf26bef6)

## user-item collaborative approach in redis

![image](https://github.com/user-attachments/assets/38c89a04-36f1-4724-99e6-00f8740d1249)

![image](https://github.com/user-attachments/assets/200cb759-dc6b-4556-9231-a4b1b700eae5)  ![image](https://github.com/user-attachments/assets/6ca4c15b-8cf8-43a2-9fc5-075018384f04)



