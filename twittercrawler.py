#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 12:18:31 2018

@author: valquiria
"""

import tweepy 
import requests
import os
import io
#import subprocess

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from google.cloud import vision
consumer_key = "Your consumer_Key"
consumer_secret = "Your consumer_Secret"
access_key = "Your access_key"
access_secret = "Your access_secret"
#insert yours

#M3 
import mysql.connector
import pymongo
# mongodb data
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["twitterdata"]
mycol = mydb["miniproject3"]






def get_label(path):
    direct='PATH_TO_JSON_CREDENTIALS'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']=direct
    client = vision.ImageAnnotatorClient()
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    response = client.label_detection(image=image)
    labels = response.label_annotations
   
    size = 20
    ttfont = ImageFont.truetype("Arial.ttf",2*size)
    im = Image.open(path)
    draw = ImageDraw.Draw(im)
    i=0
    for label in labels:
         draw.text((size,size+2*size*i),label.description, fill=(0,255,0),font=ttfont)
         i+=1
    im.save(path)



def savepics(image_url,screen_name, filename):
    path='PATH_TO_YOUR_SAVING_DIRECTORY'+screen_name+'/'
    if not os.path.exists(path):
        os.makedirs(path)
    url = image_url
    r = requests.get(url,allow_redirects=True)
    file=open(path+filename, 'wb')
    if os.path.isfile(path+filename):
        print (filename)  
    file.write(r.content)
    file.close()
    get_label(path+filename)
    




def get_all_tweets(screen_name):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    
    picture_urls=[]
    new_tweets = api.user_timeline(screen_name = screen_name,count=10)
    if len(new_tweets)==0:
        print('not enough picture')
        return        
    oldest = new_tweets[-1].id - 1
    
    while len(picture_urls)<9 :
        for tweet in new_tweets:
            if 'media' not in tweet._json['entities']:
                continue
            picture_urls.append(tweet._json['entities']['media'][0]['media_url'])
        new_tweets = api.user_timeline(screen_name = screen_name,count=10,max_id=oldest)
        if len(new_tweets)==0:
            print('we have only '+str(len(picture_urls))+' pictures')
            return
        oldest = new_tweets[-1].id - 1
    
    for i in range(len(picture_urls)):
        filename="img00"+str(i)+".jpg"
        savepics(picture_urls[i],screen_name,filename)

    sqlrecord(screen_name,picture_urls)#upload data mysql
    mongorecord(picture_urls)
        
def sqlrecord(screen_name,picture_urls):#upload (topic , picture_urls) to my sql
    mydb=mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='yourpassword', #input your password
        database='TwitterCrawlerURLS',#build your database before using this
        auth_plugin='mysql_native_password')#this line should be added if it doesn't recognize your passwd form

    mycursor = mydb.cursor()
    sqlFormula = "INSERT INTO Twittercontent(Topic, URL) VALUES (%s,%s)"
    for url in picture_urls:
        mycursor.execute(sqlFormula,(screen_name, url))#upload to preset table
    mydb.commit()
    
def mongorecord(picture_urls):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["TwitterCrawlerUrls"]
    mycol = mydb["Twitter"]
    dp=dict(picture_urls)
    for key in picture_urls :   
        mycol.insert_one({key:dp[key]})    
    
    
if __name__ == '__main__':
    topic="@YOURTOPIC"#type in your topic
    get_all_tweets(topic)
