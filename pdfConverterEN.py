#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
import os
import random as rnd

from pathlib import Path
from decimal import Decimal

from borb.pdf.canvas.layout.image.image import Image
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout
from borb.pdf.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF


token = 'YOUR_TOKEN'
bot = telebot.TeleBot(token)

doc_name = 'file'

ready_to_take_name = False
creating_in_process = False

images = []
size_box = []
replies = ['Prettily', 'Processed ', 'Go on', 'Lets go next ', 'Next', 'Yep, there is', 'Fixed', 'Yep']
prev_id = 0
print(bot.get_me())

@bot.message_handler(commands=["start"])
def start(m, res=False):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('Start building pdf', 'Finish building pdf')
    bot.send_message(m.chat.id, 'Hi!\nTo build pdf, use the panel at the bottom of the screen', reply_markup=user_markup)



@bot.message_handler(content_types=["text"])
def handle_text(message):
    global ready_to_take_name
    global creating_in_process
    global doc_name
    global images
    global size_box
    

    if ready_to_take_name == True:
        doc_name = message.text + '.pdf'
        ready_to_take_name = False
        creating_in_process = True
        bot.send_message(message.from_user.id, 'Now send images one by one!\nWhen you are done, just click the button at the bottom :)')
    
    elif message.text == 'Start building pdf':
        images = []
        size_box = []
        bot.send_message(message.from_user.id, 'Enter file name')
        ready_to_take_name = True
    
    elif message.text == 'Finish building pdf':
        
        if creating_in_process == True:
            creating_in_process = False

            pdf = Document()
            page = Page()
            pdf.append_page(page)
            layout = SingleColumnLayout(page)

            for i in range(len(images)):
                image_size = format_size(size_box[2*i], size_box[2*i+1])
                layout.add(
                    Image(
                        images[i],
                        width=Decimal(image_size[0]),
                        height=Decimal(image_size[1]),
                    )
                )

            with open(doc_name, "wb") as out_file_handle:
                PDF.dumps(out_file_handle, pdf)

            bot.send_chat_action(message.from_user.id, 'upload_document')
            bot.send_message(message.from_user.id, 'You are welcome :)')
            bot.send_document(message.from_user.id, open(Path(doc_name), "rb"))
            
            closing = open(Path(doc_name), "rb")
            closing.close()
            os.remove(doc_name)
        else:
            bot.send_message(message.from_user.id, 'Nothing to finish yet')

def format_size(width, height):
    image_size = [width, height]
    while (image_size[0] > 470) or (image_size[1] > 650):
        image_size[0] /= 1.1
        image_size[1] /= 1.1
    return image_size

@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    
    global prev_id
    global replies
    if creating_in_process == True:
        images.append("https://api.telegram.org/file/bot{0}/{1}".format(token, bot.get_file(message.photo[-1].file_id).file_path))
        size_box.append(message.photo[-1].width)
        size_box.append(message.photo[-1].height)
        prev_id = rnd_reply(message, prev_id)
    else:
        bot.send_message(message.from_user.id, 'Dont rush, press the button below first :3')

def rnd_reply(message, prev_id):
    rnd_id = rnd.randint(0, len(replies)-1)
    if rnd_id != prev_id:
        bot.send_message(message.from_user.id, replies[rnd_id])
        prev_id = rnd_id
    else:
        rnd_reply(message, prev_id)
    return rnd_id

bot.polling(none_stop=True, interval=0)