import io
import os
import requests
import numpy as np
import cv2
from PIL import Image
from google.cloud import vision
import discord

bot = discord.Client()

listening_channel = ''

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = vision.ImageAnnotatorClient()

def preprocess_image(imageLink):
    response = requests.get(imageLink)
    img = np.array(Image.open(io.BytesIO(response.content)))
    image_srcg = cv2.bitwise_not(img)
    gray = cv2.cvtColor(image_srcg, cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    cv2.imwrite('image.jpg', img)
    
    
def get_text(file_name, number=True):
    file_name = os.path.abspath(file_name)
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
    my_image = vision.Image(content=content)
    if number:
        response = client.text_detection(image=my_image)
    else:
        response = client.document_text_detection(image=my_image)
    if len(response.error.message) > 0:
        return response.error.message
    return response.text_annotations[0].description

@bot.event
async def on_message(message):
    if (message.author.bot):
        return
    if message.channel.id == listening_channel:
        if message.attachments:  # checks for attachments
            link = message.attachments[0].url
            fileType = link.split('.')
            imageFileTypes = ['png', 'jpg', 'jpeg']
            preprocess_image(link)
            if fileType[-1].lower() in imageFileTypes:
                content = get_text('image.jpg')
                await message.channel.send(content)
                
            if message.content.startswith('!debug'):
                await message.channel.send(file=discord.File('image.jpg'))

bot.run(discord_bot_key)
