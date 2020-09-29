# Chat Back-end 
Personal project presenting back-end of the chat app.

The app works both with private and group chats.
##  I've created it with:
 * [Django][djangolink]
 * [Django Rest Framework][restframeworklink]
 * [Django Channels][channelslink]
 
## Databases I used:
 * [PostgreSQL][postgreslink]
 * [Redis][redislink]
 * [Memcached][memcachedlienk] (Caching system)
 
 All additional extensions and packages can be found in 'requirements.txt'.
 
 ## The backend contain two main endpoints:
 * Standard, comprehensive REST API
 
 * Channels to handle WebSockets
 
 ## REST API
 All endpoints are available on `apischema/`.
 ![](media-readMe/Screenshot%20from%202020-08-06%2021-27-27.png)
 
##### Example query(searching users):
![](media-readMe/Screenshot%20from%202020-08-06%2021-39-00.png)

 
 ## CHANNELS ROUTES
 * Fetching previous messages with command `fetch_messages`. 
 We have to pass 'time stamp' of last loaded message or pass 0/current time
 if we want to fetch messages for the first time. One package contain 15 messages.
 
 * Sending new message to all connected users with command `new_message`.
 In this case all we have to dispatch is content of new message.
 
 ![](media-readMe/Screenshot%20from%202020-08-06%2021-46-06.png)
 
 Image presents private chat of two users.
 
 This screenshot was made on my sandbox(client-side) only for presentation purpose.
 I do not attach these files in the repository. 
 
 ## Caching
 Thanks to distributed memory-caching system -> Memcached, 
 we are able to save request execution time.
 Cached endpoints:
 - 90 seconds:
    - `/api/chat/mychats/`
    - `/api/chat/mychats/<str:type>/`   
    - `/api/user/search/<str:phrase>/`    
 - 60 seconds: 
    - `/api/user/<uuid:uuid>/`
 
 ## Authentication and Permission
 Whole project works with Token authentication 
 due to security reasons.
 You have to attach the Token key with every request.
 
 ![](media-readMe/Screenshot%20from%202020-08-06%2021-35-36.png)
 &nbsp;
 ![](media-readMe/Screenshot%20from%202020-08-06%2021-34-55.png)
 
 ##### Issues
 ###### * Google authentication doesn't work completely. I mentioned this issue in the `settings.py` file. To make it work, positive response(user successfully logged in) from the server should contain generated Token(for our   app). However authentication with google account works fine when we add Session Authentication to our authentication classes.
  
 [restframeworklink]:https://www.django-rest-framework.org/
 [djangolink]:https://www.djangoproject.com/
 [channelslink]:https://channels.readthedocs.io/en/latest/
 [postgreslink]:https://www.postgresql.org/
 [redislink]:https://redis.io/
 [memcachedlienk]:https://memcached.org/
