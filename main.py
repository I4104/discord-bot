import os
import ffmpeg
import discord
import sys
import asyncio
import time
import yaml
import random
import json
import os.path
import requests

from os import path
from PyDictionary import PyDictionary
from gtts import gTTS
from discord.ext import commands
from google_trans_new import google_translator
from discord import FFmpegPCMAudio

voice_client = None

client = discord.Client()

@client.event
async def on_ready():
    global voice_client

    if voice_client:
        await voice_client.disconnect()

    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="lệnh của Khoa"))
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    global voice_client

    language = 'vi'

    dictionary = PyDictionary()
    translator = google_translator()  

    country = "en, fa, pl, pt, pa, ro, ru, sm, gd, sr, st, sn, sd, si, sk, sl, so, es, su, sw, sv, tg, ta, te, th, tr, uk, ur, ug, uz, vi, cy, xh, yi, yo, zu"
    country = country.split(", ")

    if (message.content == "%_info"):
        contents  = "# Commands:\n"
        contents += " - % <text>: bot đọc những gì người dùng viết\n"
        contents += " - %_wiki <say> <text>: tìm kiếm thông tin trên wiki\n"
        contents += " - %_words <number>: ngẫu nhiên <number> từ tiếng anh\n"
        contents += " - %_clear <number>: xóa <number> dòng tính từ câu lệnh\n"
        contents += " - %_contain <word>: Từ đồng nghĩa\n"
        contents += " - %_trans <word>: dịch nghĩa của từ\n"
        contents += " - %_meaning <say> <word>: Lấy nghĩa của từ\n"
        contents += " \n"
        contents += "# Information:\n"
        contents += " - Project: Discord Bot\n"
        contents += " - IDEA: K04\n"
        contents += " - Version: 1.0.2-beta\n"


        embed = discord.Embed(color=0x01cb19)
        embed.add_field(name='Thông tin:', value=contents, inline=False)
        embed.set_footer(text='Bot version: 1.0.2 - Admin: Tạ Đăng Khoa')
        
        await message.channel.send(embed=embed)

    if (message.content == "%_clear" or message.content.split(" ")[0] == "%_clear"):
        if (len(message.content.split(" ")) < 2):
            await message.channel.send('Câu lệnh: %_clear <Số lượng>')
            return

        if (message.content.split(" ")[1] == "" or message.content.split(" ")[1] == " "): 
            await message.channel.send('Câu lệnh: %_clear <Số lượng>')
            return

        print("Clearing message...")
        await message.channel.purge(limit=int(message.content.split(" ")[1]))

    if (message.content == "%_trans" or message.content.split(" ")[0] == "%_trans"):
        await message.delete()
        if (len(message.content.split(" ")) < 2):
            await message.channel.send('Câu lệnh: %_trans <word>')
            return

        if (message.content.split(" ")[1] == "" or message.content.split(" ")[1] == " "): 
            await message.channel.send('Câu lệnh: %_trans <Số lượng>')
            return

        print("Translate " + message.content.split(" ")[1])
        translate_text = translator.translate(message.content.split(" ")[1], lang_src='en', lang_tgt='vi')
        await message.channel.send(message.content.split(" ")[1] + ": " + translate_text)

    if (message.content == "%_words" or message.content.split(" ")[0] == "%_words"):
        if (len(message.content.split(" ")) < 2):
            await message.channel.send('Câu lệnh: %_words <Số lượng>')
            return

        if (message.content.split(" ")[1] == "" or message.content.split(" ")[1] == " "): 
            await message.channel.send('Câu lệnh: %_words <Số lượng>')
            return

        print("Get " + message.content.split(" ")[1] + " keywords")
        mess = await message.channel.send("Vui lòng chờ...")
        all_words = list()

        with open('vocabulary.txt', 'r') as reader:
            for line in reader:
                all_words.append(line)

        words = list()
        while len(words) < int(message.content.split(" ")[1]):
            text = all_words[random.randrange(0, len(all_words))]
            if (text not in words):
                words.append(text)

        contents = ""
        for word in words:
            meanings = list(dictionary.meaning(word).keys())
            meaning = meanings[0]
            if (meaning == "Noun"): meaning = "n"
            elif (meaning == "Verb"): meaning = "v" 
            translate_text = translator.translate(word, lang_src='en', lang_tgt='vi')  
            contents += str(word.replace("\n", "") + ' ('+ meaning +'): ' + translate_text.lower()) + '\n'

        embed = discord.Embed(color=0xff0000)
        embed.add_field(name=message.content.split(" ")[1] + ' từ vựng bất kì cho bạn: ', value=contents, inline=False)
        embed.set_footer(text='Bot version: 1.0.2 - Admin: Tạ Đăng Khoa')
        await message.channel.send(embed=embed)
        await mess.delete()

    if (message.content == "%_contain" or message.content.split(" ")[0] == "%_contain"):
        await message.delete()
        if (len(message.content.split(" ")) < 2):
            await message.channel.send('Câu lệnh: %_contain <word>')
            return

        if (message.content.split(" ")[1] == "" or message.content.split(" ")[1] == " "): 
            await message.channel.send('Câu lệnh: %_contain <word>')
            return
        print("Get contain of " + message.content.split(" ")[1])
        mess = await message.channel.send("Vui lòng chờ...")

        contents = ""
        for word in dictionary.synonym(message.content.split(" ")[1]):
            contents += word + "\n"

        embed = discord.Embed(color=0xff0000)
        embed.add_field(name='Từ đồng nghĩa cho: "' + message.content.split(" ")[1] + '"', value=contents, inline=False)
        embed.set_footer(text='Bot version: 1.0.2 - Admin: Tạ Đăng Khoa')
        await message.channel.send(embed=embed)
        await mess.delete()

    if (message.content == "%_meaning" or message.content.split(" ")[0] == "%_meaning"):
        await message.delete()
        
        if (len(message.content.split(" ")) < 3):
            await message.channel.send('Câu lệnh: %_meaning <say: true or false> <word>')
            return

        if (message.content.split(" ")[2] == "" or message.content.split(" ")[2] == " "): 
            await message.channel.send('Câu lệnh: %_meaning <say: true or false> <word>')
            return

        if (message.content.split(" ")[1] != "true" and message.content.split(" ")[1] != "false" or message.content.split(" ")[1] == "" or message.content.split(" ")[1] == " "): 
            await message.channel.send('Câu lệnh: %_meaning <say: true or false> <word>')
            return

        print("Get meaning of " + message.content.split(" ")[1])
        mess = await message.channel.send("Vui lòng chờ...")

        contents = "\n"
        try:
            get = list(dictionary.meaning(message.content.split(" ")[2]).values())
            get = list(get[0])
            
            mean = ""
            for words in get:
                mean += words + " "

            translate_text = translator.translate(mean, lang_src='en', lang_tgt='vi') 
            contents += "- " + str(translate_text.lower()) + '\n'

            embed = discord.Embed(color=0xff0000)
            embed.add_field(name='Nghĩa cho từ: "' + message.content.split(" ")[1] + '"', value=contents, inline=False)
            embed.set_footer(text='Bot version: 1.0.2 - Admin: Tạ Đăng Khoa')
            await message.channel.send(embed=embed)

            if path.exists('output.mp3'):
                await message.channel.send("Đang đọc, cứ từ từ :| mỏi miệng")
                return

            if (message.content.split(" ")[1] == "true"):
                if voice_client:
                    await voice_client.disconnect()

                try:
                    channel = message.author.voice.channel
                except AttributeError:
                    await message.channel.send('Bạn cần tham gia một kênh voice!')
                    return
                
                voice_client = await channel.connect(reconnect=False)

                myobj = gTTS(text=translate_text, lang=language, slow=False) 
                myobj.save("output.mp3")
                 
                voice_client.play(discord.FFmpegPCMAudio(options = "-loglevel panic", source='output.mp3'), after=lambda x:os.remove("output.mp3"))

        except Exception:
            await message.channel.send("Không tồn tại nghĩa của từ này!")

        await mess.delete()

    if (message.content.split(" ")[0] == "%_wiki"):
        if (len(message.content.split(" ")) < 3):
            await message.channel.send('Câu lệnh: %_wiki <say: true or false> <định nghĩa cần tìm> 1')
            return

        if (message.content.split(" ")[2] == "" or message.content.split(" ")[2] == " "): 
            await message.channel.send('Câu lệnh: %_wiki <say: true or false> <định nghĩa cần tìm> 2')
            return

        if (message.content.split(" ")[1] != "true" and message.content.split(" ")[1] != "false" or message.content.split(" ")[1] == "" or message.content.split(" ")[1] == " "): 
            await message.channel.send('Câu lệnh: %_wiki <say: true or false> <định nghĩa cần tìm> 3')
            return

        msg = message.content.split(" ")
        request = msg[2:]
        
        request = " ".join(request)

        mess = await message.channel.send("Vui lòng chờ một chút...")

        try:
            r = requests.get('https://vi.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles=' + request.lower().replace(" ", "%20"))
            contents = str(r.json()).split("'extract':")[1].replace("{", "").replace("}", "").replace("'", "")
        except Exception:
            contents = "Không có thông tin!"

        if (len(contents) > 1024):
            contents = contents.split(str("\\n"))[1]
            if (len(contents) > 1024):
                contents = contents[0:1000]
                end = contents.split(str("."))[-1]
                contents = contents.replace(end, "") + "\n\n Còn nữa..."

        await mess.delete()
        embed = discord.Embed(color=0x3700ff)
        embed.add_field(name='Tìm kiếm thông tin cho: "' + request + '"', value=contents, inline=False)
        embed.set_footer(text='Bot version: 1.0.2 - Admin: Tạ Đăng Khoa')
        
        await message.channel.send(embed=embed)

        if (msg[1] == "true"):
            if voice_client:
                await voice_client.disconnect()

            try:
                channel = message.author.voice.channel
            except AttributeError:
                await message.channel.send('Bạn cần tham gia một kênh voice!')
                return

            voice_client = await channel.connect(reconnect=False)

            if path.exists('output.mp3'):
                await message.channel.send("Đang đọc, cứ từ từ :| mỏi miệng")
                return
            myobj = gTTS(text=contents, lang=language, slow=False) 
            myobj.save("output.mp3")

            voice_client.play(discord.FFmpegPCMAudio(options = "-loglevel panic", source='output.mp3'), after=lambda x:os.remove("output.mp3"))

    if (message.content == "%_leave"):
        try:
            channel = message.author.voice.channel
        except AttributeError:
            await message.channel.send('Bạn cần tham gia một kênh voice!')
        if os.path.isfile('output.mp3'): os.remove("output.mp3")
        await voice_client.disconnect()

    if (message.content.split(" ")[0] == "%"):
        if path.exists('output.mp3'):
            await message.channel.send("Đang đọc, cứ từ từ :| mỏi miệng")
            return

        if voice_client:
            await voice_client.disconnect()

        try:
            channel = message.author.voice.channel
        except AttributeError:
            await message.channel.send('Bạn cần tham gia một kênh voice!')

        voice_client = await channel.connect(reconnect=False)
        
        msg = message.content.split(" ")
        if (msg[1] in country):
            request = msg[2:]
            lang = msg[1]
        else:
            request = msg[1:]
            lang = language

        request = " ".join(request)

        myobj = gTTS(text=request, lang=lang, slow=False) 
        myobj.save("output.mp3")
         
        voice_client.play(discord.FFmpegPCMAudio(options = "-loglevel panic", source='output.mp3'), after=lambda x:os.remove("output.mp3"))

        await message.delete()

client.run('Nzc4NjQ5NTIzNzQ4MjA4NjQw.X7VD4Q.5jbVphclmXv5upqHaVO97jqSYkg')

