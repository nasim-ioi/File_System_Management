# Description
this is file uploading and downloading system and only owners of stores can mange their products, files and subscription. 
Admin actions which are mentioned below in Features are main admin duties and can be done only by admin from Django-Pannel.
this project has 2 apps 
1. user ---> for login, signup and refresh jwt token
2. content ---> managing products, files, ..etc for storeing system


# Installation
 

## requirements:


  python version : 3.7.5
  
  Django : 2.2

  run pipenv install to install required packeages.


# Features


1. Owner actions:
    1. uploading file
    2. update(rename,...) files
    3. add and updates products
    4. add and updates subscriptions
  
2. Customer actions:
    1. see stores
    2. see products and buy them
    3. see subscription and buy them
    4. see files and buy or download them
    5. see their carts

3. Admin actions:
    1. make a user to owner
    2. specified a store to an owner
    3. Add categories from provided choices
  
