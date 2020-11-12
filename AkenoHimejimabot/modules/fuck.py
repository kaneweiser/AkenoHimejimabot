import datetime
from random import randint
from gtts import gTTS
import os
import re
import urllib
from datetime import datetime
import urllib.request
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import requests
from typing import List
from telegram import ParseMode, InputMediaPhoto, Update, TelegramError, ChatAction
from telegram.ext import CommandHandler, run_async, CallbackContext
from AkenoHimejimabot import dispatcher, TIME_API_KEY, CASH_API_KEY, WALL_API
from AkenoHimejimabot.modules.disable import DisableAbleCommandHandler

opener = urllib.request.build_opener()
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.38 Safari/537.36'
opener.addheaders = [('User-agent', useragent)]



@run_async
def tts(context: CallbackContext, update: Update):
    args = context.args
    datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    datetime.now().strftime("%d%m%y-%H%M%S%f")
    reply = " ".join(args)
    update.message.chat.send_action(ChatAction.RECORD_AUDIO)
    lang = "ml"
    tts = gTTS(reply, lang)
    tts.save("k.mp3")
    with open("k.mp3", "rb") as f:
        linelist = list(f)
        linecount = len(linelist)
    if linecount == 1:
        update.message.chat.send_action(ChatAction.RECORD_AUDIO)
        lang = "en"
        tts = gTTS(reply, lang)
        tts.save("k.mp3")
    with open("k.mp3", "rb") as speech:
        update.message.reply_voice(speech, quote=False)


@run_async
def reverse(update: Update, context: CallbackContext):
    args = context.args
    if os.path.isfile("okgoogle.png"):
        os.remove("okgoogle.png")

    msg = update.effective_message
    chat_id = update.effective_chat.id
    rtmid = msg.message_id
    imagename = "okgoogle.png"

    reply = msg.reply_to_message
    if reply:
        if reply.sticker:
            file_id = reply.sticker.file_id
        elif reply.photo:
            file_id = reply.photo[-1].file_id
        elif reply.document:
            file_id = reply.document.file_id
        else:
            msg.reply_text("Reply to an image or sticker to lookup.")
            return
        image_file = context.bot.get_file(file_id)
        image_file.download(imagename)
        if args:
            txt = args[0]
            try:
                lim = int(txt)
            except Exception as e:
                print(e)
                lim = 2
        else:
            lim = 2
    elif args:
        splatargs = msg.text.split(" ")
        if len(splatargs) == 3:
            img_link = splatargs[1]
            try:
                lim = int(splatargs[2])
            except Exception:
                lim = 2
        elif len(splatargs) == 2:
            img_link = splatargs[1]
            lim = 2
        else:
            msg.reply_text("/reverse <link> <amount of images to return.>")
            return
        try:
            urllib.request.urlretrieve(img_link, imagename)
        except HTTPError as HE:
            if HE.reason == 'Not Found':
                msg.reply_text("Image not found.")
                return
            elif HE.reason == 'Forbidden':
                msg.reply_text(
                    "Couldn't access the provided link, The website might have blocked accessing to the website by bot or the website does not existed.")
                return
        except URLError as UE:
            msg.reply_text(f"{UE.reason}")
            return
        except ValueError as VE:
            msg.reply_text(
                f"{VE}\nPlease try again using http or https protocol.")
            return
    else:
        msg.reply_markdown(
            "Please reply to a sticker, or an image to search it!\nDo you know that you can search an image with a link too? `/reverse [picturelink] <amount>`.")
        return

    try:
        searchUrl = 'https://www.google.com/searchbyimage/upload'
        multipart = {
            'encoded_image': (
                imagename,
                open(
                    imagename,
                    'rb')),
            'image_content': ''}
        response = requests.post(
            searchUrl,
            files=multipart,
            allow_redirects=False)
        fetchUrl = response.headers['Location']

        if response != 400:
            xx = context.bot.send_message(
                chat_id, "Image was successfully uploaded to Google."
                "\nParsing source now. Maybe.", reply_to_message_id=rtmid)
        else:
            context.bot.send_message(
                chat_id,
                "Google told me to go away.",
                reply_to_message_id=rtmid)
            return

        os.remove(imagename)
        match = ParseSauce(fetchUrl + "&hl=en")
        guess = match['best_guess']
        if match['override'] and match['override'] != '':
            imgspage = match['override']
        else:
            imgspage = match['similar_images']

        if guess and imgspage:
            xx.edit_text(
                f"[{guess}]({fetchUrl})\nLooking for images...",
                parse_mode='Markdown',
                disable_web_page_preview=True)
        else:
            xx.edit_text("Couldn't find anything.")
            return

        images = scam(imgspage, lim)
        if len(images) == 0:
            xx.edit_text(
                f"[{guess}]({fetchUrl})\n[Visually similar images]({imgspage})"
                "\nCouldn't fetch any images.",
                parse_mode='Markdown',
                disable_web_page_preview=True)
            return

        imglinks = []
        for link in images:
            lmao = InputMediaPhoto(media=str(link))
            imglinks.append(lmao)

        context.bot.send_media_group(
            chat_id=chat_id,
            media=imglinks,
            reply_to_message_id=rtmid)
        xx.edit_text(
            f"[{guess}]({fetchUrl})\n[Visually similar images]({imgspage})",
            parse_mode='Markdown',
            disable_web_page_preview=True)
    except TelegramError as e:
        print(e)
    except Exception as exception:
        print(exception)


def ParseSauce(googleurl):
    """Parse/Scrape the HTML code for the info we want."""
    source = opener.open(googleurl).read()
    soup = BeautifulSoup(source, 'html.parser')
    results = {
        'similar_images': '',
        'override': '',
        'best_guess': ''
    }
    try:
        for bess in soup.findAll('a', {'class': 'PBorbe'}):
            url = 'https://www.google.com' + bess.get('href')
            results['override'] = url
    except Exception as e:
        print(e)
    for similar_image in soup.findAll('input', {'class': 'gLFyf'}):
        url = 'https://www.google.com/search?tbm=isch&q=' + \
            urllib.parse.quote_plus(similar_image.get('value'))
        results['similar_images'] = url

    for best_guess in soup.findAll('div', attrs={'class': 'r5a77d'}):
        results['best_guess'] = best_guess.get_text()
    return results


__help__ = """
──「 *Corona:* 」──
-> `/covid`
To get Global data
-> `/covid` <country>
To get data of a country
──「 *Urban Dictionary:* 」──
-> `/ud` <word>: Type the word or expression you want to search use.
──「 *Currency Converter:* 」──
Example syntax: `/cash 1 USD INR`
-> `/cash`
currency converter
──「 *Wallpapers:* 」──
-> `/wall` <query>
get a wallpaper from wall.alphacoders.com
──「 *Google Reverse Search:* 」──
-> `/reverse`
Does a reverse image search of the media which it was replied to.
──「 *Text-to-Speach* 」──
-> `/tts` <sentence>
Text to Speech!
──「 *Last FM:* 」──
-> `/setuser` <username>
sets your last.fm username.
-> `/clearuser`
removes your last.fm username from the bot's database.
-> `/lastfm`
returns what you're scrobbling on last.fm.
──「 *Playstore:* 」──
-> `/app` <app name>
finds an app in playstore for you
"""
#APP_HANDLER = DisableAbleCommandHandler("app", app)
#UD_HANDLER = DisableAbleCommandHandler("ud", ud)
#COVID_HANDLER = DisableAbleCommandHandler(["covid", "corona"], covid)
#WALL_HANDLER = DisableAbleCommandHandler("wall", wall, pass_args=True)
#CONVERTER_HANDLER = DisableAbleCommandHandler('cash', convert)
REVERSE_HANDLER = DisableAbleCommandHandler(
    "reverse", reverse, pass_args=True, admin_ok=True)
TTS_HANDLER = DisableAbleCommandHandler('tts', tts, pass_args=True)

#dispatcher.add_handler(APP_HANDLER)
#dispatcher.add_handler(COVID_HANDLER)
dispatcher.add_handler(REVERSE_HANDLER)
#dispatcher.add_handler(WALL_HANDLER)
#dispatcher.add_handler(CONVERTER_HANDLER)
dispatcher.add_handler(TTS_HANDLER)
#dispatcher.add_handler(UD_HANDLER)

__mod_name__ = "Extras"
__command_list__ = [
    #"cash",
    #"wall",
    "reverse",
    #"covid",
    #"corona",
    "tts",
    #"ud",
    #"app"
]
__handlers__ = [
    #CONVERTER_HANDLER,
    #WALL_HANDLER,
    REVERSE_HANDLER,
    #COVID_HANDLER,
    TTS_HANDLER,
    #UD_HANDLER,
    #APP_HANDLER
]
