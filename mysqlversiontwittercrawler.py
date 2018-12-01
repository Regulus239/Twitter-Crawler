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


#M3 
import mysql.connector
mydb=mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='Yourpassword',
        database='twittercrawler_recorder')

mycursor = mydb.cursor()

sqlFormula = "INSERT INTO PictureURLS(Topic, URL) VALUES (%s,%s)"







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
        mycursor.execute(screen_name, picture_urls)
        filename="img00"+str(i)+".jpg"
        savepics(picture_urls[i],screen_name,filename)  
        
    
    
    
    
if __name__ == '__main__':
    topic="@YOURTOPIC"
    get_all_tweets(topic)
    #subprocess.call("cd ./"+topic,shell=True)
    #subprocess.call("ffmpeg -r 60 -f image2 -s 1920x1080 -i img%04d.jpg -vcodec libx264 -crf 25  -pix_fmt yuv420p test.mp4",shell=True)
    
    mydb.commit()
