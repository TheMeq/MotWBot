import discord
from discord.ext import commands
import aiohttp
import asyncio
import logging
import async_timeout
import json
import time
import math
import subprocess
import aiomysql
import base64
import math
import configparser
from random import randint
from random import seed
from random import choice
import random
import ctypes
import sys
import os
import hashlib
import urllib.request
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ctypes.windll.kernel32.SetConsoleTitleW("MotW - Last Started: "+str(time.strftime("%c")))

bt = str(int(os.path.getmtime(__file__)))
ve = "0." + bt[:2] + "." + bt[2:-4] + "." + bt[-4:]

config = configparser.ConfigParser()
config.read('osu_motw.cfg')

osu_key = config.get('osu','key')
dis_key = config.get('discord','key')
main_server = config.get('discord','server')

bot_name = "MotW Bot"

mysql_host = config.get('mysql','host')
mysql_user = config.get('mysql','username')
mysql_pass = config.get('mysql','password')
mysql_data = config.get('mysql','database')

osu_api = 'https://osu.ppy.sh/api/'
channel_announcements = ""
channel_general = ""
channel_global = ""
channel_botlog = ""

osu_ranks = {
	"A":"",
	"B":"",
	"C":"",
	"D":"",
	"S":"",
	"SH":"",
	"X":"",
	"XH":"",
	}

hit_50 = ""
hit_100 = ""
hit_300 = ""
hit_0 = ""
hit_m_0 = ""
hit_m_50 = ""
hit_m_100 = ""
hit_m_200 = ""
hit_m_300 = ""
hit_m_350 = ""

osu_mods = {
	"1":"",
	"2":"",
	"8":"",
	"16":"",
	"32":"",
	"64":"",
	"128":"",
	"256":"",
	"512":"",
	"1024":"",
	"2048":"",
	"4096":"",
	"8192":"",
	"16384":"",
	"32768":"",
	"65536":"",
	"131072":"",
	"262144":"",
	"524288":"",
	"1048576":"",
	"2097152":"",
	"16777216":"",
	"67108864":"",
	"134217728":"",
	"268435456":""
	}
osu_mods_t = {
	"1":"NF",
	"2":"EZ",
	"8":"HD",
	"16":"HR",
	"32":"SD",
	"64":"DT",
	"128":"RX",
	"256":"HT",
	"512":"NC",
	"1024":"FL",
	"2048":"AP",
	"4096":"SO",
	"8192":"RX",
	"16384":"PF",
	"32768":"4K",
	"65536":"5K",
	"131072":"6K",
	"262144":"7K",
	"524288":"8K",
	"1048576":"FI",
	"2097152":"RD",
	"16777216":"9K",
	"67108864":"1K",
	"134217728":"3K",
	"268435456":"2K"
	}

osu_roles = {
	"EX":"EX - 1 to 2k",
	"IN":"IN - 2k to 5k",
	"HD":"HD - 5k to 10k",
	"NM":"NM - 10k to 25k",
	"EZ":"EZ - 25k to 50k",
	"BA":"BA - 50k to 100k",
	"NW":"NW - 100k to 200k",
	"WH":"WH - 200k to 1000k",
	"TON":"Taiko Oni - 1 to 10k",
	"TMU":"Taiko Muzu - 1k to 2.5k",
	"TFU":"Taiko Futsuu - 2.5k to 5k",
	"TKA":"Taiko Kantan - 5k+",
	"CRA":"CTB Rain - 1 to 1k",
	"CPL":"CTB Platter - 1k to 2.5k",
	"CSA":"CTB Salad - 2.5k to 5k",
	"CCU":"CTB Cup - 5k+",
	"MMX":"Mania MX - 1 to 4k",
	"MHD":"Mania HD - 5k to 10k",
	"MNM":"Mania NM - 10k to 30k",
	"MEZ":"Mania EZ - 30k+",
	"XX":"XX - 1000k+"
}

bot = commands.Bot(command_prefix='+', description='MotW Bot by TheMeq\r\n\r\nVersion '+str(ve), pm_help= True)

def Ordinal(x):
	return "%d%s" % (x,"tsnrhtdd"[(math.floor(x/10)%10!=1)*(x%10<4)*x%10::4])

def GetMods(x):
	return [(1<<i) for i in range(0,25) if int(x) & (1<<i)]

async def BeatmapData(id : str, mods="!",acc="100",nhun="0",nfif="0",combo="0",nmis="0"):
	if mods=="!":
		ps_script = '(New-Object System.Net.WebClient).DownloadString(\"https://osu.ppy.sh/osu/'+id+'\") | ./oppai - '+str(acc)+'% '+str(nhun)+'x100 '+str(nfif)+'x50 '+str(combo)+'x '+str(nmis)+'m -ojson -no-awkwardness'
	else:
		ps_script = '(New-Object System.Net.WebClient).DownloadString(\"https://osu.ppy.sh/osu/'+id+'\") | ./oppai - '+str(acc)+'% '+str(nhun)+'x100 '+str(nfif)+'x50 +' + mods + ' '+str(combo)+'x '+str(nmis)+'m -ojson -no-awkwardness'
	log("[BMS] - Running PowerShell Command\r\n" + ps_script)
	tmp = subprocess.run(['powershell',ps_script],stdout=subprocess.PIPE)
	output = str(tmp.stdout)[2:-5]
	new_output = output.replace("\\\'","")
	get_data = json.loads(new_output)
	return get_data
	
async def BeatmapDataS(id : str, mods="!"):
	if mods=="!":
		ps_script = '(New-Object System.Net.WebClient).DownloadString(\"https://osu.ppy.sh/osu/'+id+'\") | ./oppai - 100% -ojson -no-awkwardness'
	else:
		ps_script = '(New-Object System.Net.WebClient).DownloadString(\"https://osu.ppy.sh/osu/'+id+'\") | ./oppai - 100% +' + mods + ' -ojson -no-awkwardness'
	log("[BMS] - Running PowerShell Command\r\n" + ps_script)
	tmp = subprocess.run(['powershell',ps_script],stdout=subprocess.PIPE)
	output = str(tmp.stdout)[2:-5]
	new_output = output.replace("\\\'","")
	get_data = json.loads(new_output)
	return get_data

def getChannel(atx):
	a_channel = atx.message.channel.id
	log("[G_C] - Getting Bracket: " + str(a_channel))
	if a_channel == "":
		return "EZ"
	elif a_channel == "":
		return "NM"
	elif a_channel == "":
		return "HD"
	elif a_channel == "":
		return "IN"
	elif a_channel == "":
		return "EX"
	elif a_channel == "":
		return "BA"
	elif a_channel == "":
		return "NW"
	elif a_channel == "":
		return "WH"
	else:
		return "ERROR"

def getRole(rol):
	log("[G_R] - Getting Roll Table: " + str(rol))
	if rol == "EZ":
		return "roll_ez"
	elif rol == "NM":
		return "roll_nm"
	elif rol == "HD":
		return "roll_hd"
	elif rol == "IN":
		return "roll_in"
	elif rol == "EX":
		return "roll_ex"
	elif rol == "BA":
		return "roll_ba"
	elif rol == "NW":
		return "roll_nw"
	elif rol == "WH":
		return "roll_wh"

def getScores(rol):
	log("[G_S] - Getting Score Table: " + str(rol))
	if rol == "EZ":
		return "motw_scores_ez"
	elif rol == "NM":
		return "motw_scores_nm"
	elif rol == "HD":
		return "motw_scores_hd"
	elif rol == "IN":
		return "motw_scores_in"
	elif rol == "EX":
		return "motw_scores_ex"
	elif rol == "BA":
		return "motw_scores_ba"
	elif rol == "NW":
		return "motw_scores_nw"
	elif rol == "WH":
		return "motw_scores_wh"

def getMode(rol):
	log("[G_M] - Getting Game Mode from Bracket: " + str(rol))
	if rol in "EZ-NM-HD-IN-EX-BA-NW-WH":
		return 0
	else:
		return "ERROR"

def checkMods(gm):
	allowed = 0
	if gm == "":
		allowed = 1
	if "HD" in gm:
		allowed = 1
	if "HR" in gm:
		allowed = 1
	if "FI" in gm:
		allowed = 1
	if "DT" in gm:
		allowed = 1
	if "FL" in gm:
		allowed = 1
	if "EZ" in gm:
		allowed = 0
	if "HT" in gm:
		allowed = 0
	if "NF" in gm:
		allowed = 0
	return allowed

def olembed(co,se,me):
	te = discord.Embed(colour=discord.Colour(co), description=me)
	if not se == "!":
		te.set_footer(text=str(se) + " ran this command.")
	return te

@bot.event
async def on_ready():
	_=os.system("cls")
	print(r"")
	print(r"                 __  __       ___          __  ____        _   ")
	print(r"                |  \/  |     | \ \        / / |  _ \      | |  ")
	print(r"                | \  / | ___ | |\ \  /\  / /  | |_) | ___ | |_ ")
	print(r"                | |\/| |/ _ \| __\ \/  \/ /   |  _ < / _ \| __|")
	print(r"                | |  | | (_) | |_ \  /\  /    | |_) | (_) | |_ ")
	print(r"                |_|  |_|\___/ \__| \/  \/     |____/ \___/ \__|")
	print(r"")
	print(r"                ------------------- By TheMeq -----------------")
	print(r"")
	print(r"                Version "+ve)
	log("[SUP] - Logged in as: " + bot.user.id + " ("+ bot.user.name+")")
	log("[SUP] - Setting Discord game presence to \"osu! (+help)\"")
	await bot.change_presence(game=discord.Game(name='osu! (+help)'))

@bot.event
async def on_message(m_message):
	v_server = str(m_message.server)
	if v_server != "None":
		v_channel = bot.get_channel(m_message.channel.id)
		sender_author_id = m_message.author.id
		log("[" + m_message.channel.name + "] " + m_message.author.name + ": "+m_message.content)
		try:
			mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
			mysql_curs = await mysql_conn.cursor()
			await mysql_curs.execute("SELECT * from linked_players WHERE DISCORD_ID = '"+str(sender_author_id)+"'")
			v_result = await mysql_curs.fetchone()
			if v_result:
				await mysql_curs.execute("UPDATE linked_players SET LAST_ACTION = '" + str(int(time.time())) +"' WHERE DISCORD_ID = '"+str(sender_author_id)+"'")
			await mysql_conn.commit()
			mysql_conn.close()
		except Exception as e:
			log('[on_message] Error: ' +str(e))
		if m_message.content == "+help":
			await bot.delete_message(m_message)
		if str(v_channel) in ["motw-public"]:
			if m_message.author.name != "TheMeq":
				await bot.delete_message(m_message)
		else:
			
			regex = r"osu\.ppy\.sh\/s\/([^\sa-zA-Z&]+)"
			test_str = str(m_message.content)
			matches = re.finditer(regex, test_str)
			for matchNum, match in enumerate(matches):
				log("[ONM] - Found a Song ID in the Sent Message")
				matchNum = matchNum + 1
				if "addmap" in m_message.content:
					await bot.send_message(v_channel,embed=olembed(0xffff00,"!","Don't include the entire link when adding a beatmap to the pool, just use the numbers that come after /b/"))
					log("[ONM] - Ignoring due to addmap command")
				else:
					log("[ONM] - Processing...")
					for groupNum in range(0, len(match.groups())):
						groupNum = groupNum + 1
						beatsong_id = match.group(groupNum)
						pre_embed = discord.Embed(colour=discord.Colour(0xFF00FF), description="Getting Beatmap Information... (00%)")
						msg = await bot.send_message(v_channel,embed=pre_embed)
						async with aiohttp.ClientSession() as cs:
							o_url = osu_api + "get_beatmaps?k=" + osu_key + "&s=" + str(beatsong_id)
							async with cs.get(o_url) as s:
								ses = await s.json()
								song_artis = ses[0]['artist']
								song_beats = ses[0]['beatmapset_id']
								song_title = ses[0]['title']
								song_mappe = ses[0]['creator']
								bson_embed = discord.Embed(colour=discord.Colour(0xFF00FF), description="[{0} - {1}](http://osu.ppy.sh/s/{3}) by {4}\r\n\r\n[Download via Website](http://osu.ppy.sh/d/{3})\r\n[Download via osu!Direct (Supporter Only)](http://themeq.xyz/r.php?b={3})".format(song_artis,song_title,0,beatsong_id,song_mappe,song_beats))
								bson_embed.set_thumbnail(url="http://b.ppy.sh/thumb/" + str(song_beats) + "l.jpg")
								await bot.edit_message(msg,embed=bson_embed)
					log("[ONM] - Finished!")
			regex = r"osu\.ppy\.sh\/b\/([^\sa-zA-Z&]+)"
			test_str = str(m_message.content)
			matches = re.finditer(regex, test_str)
			for matchNum, match in enumerate(matches):
				log("[ONM] - Found a Beatmap ID in the Sent Message")
				matchNum = matchNum + 1
				if "addmap" in m_message.content:
					await bot.send_message(v_channel,embed=olembed(0xffff00,"!","Don't include the entire link when adding a beatmap to the pool, just use the numbers that come after /b/"))
					log("[ONM] - Ignoring due to addmap command")
				else:
					log("[ONM] - Processing...")
					for groupNum in range(0, len(match.groups())):
						groupNum = groupNum + 1
						beatsong_id = match.group(groupNum)
						pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (00%)")
						msg = await bot.send_message(v_channel,embed=pre_embed)
						async with aiohttp.ClientSession() as cs:
							o_url = osu_api + "get_beatmaps?k=" + osu_key + "&b=" + str(beatsong_id)
							async with cs.get(o_url) as s:
								ses = await s.json()
								song_artis = ses[0]['artist']
								song_beats = ses[0]['beatmapset_id']
								song_title = ses[0]['title']
								song_diffi = ses[0]['version']
								song_mappe = ses[0]['creator']
								song_mode = ses[0]['mode']
								
								bson_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="[{0} - {1} ({2})](http://osu.ppy.sh/b/{3}) by {4}\r\n\r\n[Download via Website](http://osu.ppy.sh/d/{3})".format(song_artis,song_title,song_diffi,beatsong_id,song_mappe,song_beats))
								if song_mode == "0":
									data_beatmap_none = await BeatmapDataS(beatsong_id)
									star_rating_none = str(round(data_beatmap_none['stars'],2))
									pp_gained_none = str(round(data_beatmap_none['pp'],2))
									pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (12%)")
									msg = await bot.edit_message(msg,embed=pre_embed)
									data_beatmap_hdon = await BeatmapDataS(beatsong_id,"HD")
									star_rating_hdon = str(round(data_beatmap_hdon['stars'],2))
									pp_gained_hdon = str(round(data_beatmap_hdon['pp'],2))
									pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (25%)")
									msg = await bot.edit_message(msg,embed=pre_embed)
									data_beatmap_hron = await BeatmapDataS(beatsong_id,"HR")
									star_rating_hron = str(round(data_beatmap_hron['stars'],2))
									pp_gained_hron = str(round(data_beatmap_hron['pp'],2))
									pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (37%)")
									msg = await bot.edit_message(msg,embed=pre_embed)
									data_beatmap_dton = await BeatmapDataS(beatsong_id,"DT")
									star_rating_dton = str(round(data_beatmap_dton['stars'],2))
									pp_gained_dton = str(round(data_beatmap_dton['pp'],2))
									pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (50%)")
									msg = await bot.edit_message(msg,embed=pre_embed)
									data_beatmap_hdhr = await BeatmapDataS(beatsong_id,"HDHR")
									star_rating_hdhr = str(round(data_beatmap_hdhr['stars'],2))
									pp_gained_hdhr = str(round(data_beatmap_hdhr['pp'],2))
									pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (62%)")
									msg = await bot.edit_message(msg,embed=pre_embed)
									data_beatmap_dthd = await BeatmapDataS(beatsong_id,"DTHD")
									star_rating_dthd = str(round(data_beatmap_dthd['stars'],2))
									pp_gained_dthd = str(round(data_beatmap_dthd['pp'],2))
									pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (75%)")
									msg = await bot.edit_message(msg,embed=pre_embed)
									data_beatmap_dthr = await BeatmapDataS(beatsong_id,"DTHR")
									star_rating_dthr = str(round(data_beatmap_dthr['stars'],2))
									pp_gained_dthr = str(round(data_beatmap_dthr['pp'],2))
									pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (87%)")
									msg = await bot.edit_message(msg,embed=pre_embed)
									data_beatmap_dthh = await BeatmapDataS(beatsong_id,"DTHDHR")
									star_rating_dthh = str(round(data_beatmap_dthh['stars'],2))
									pp_gained_dthh = str(round(data_beatmap_dthh['pp'],2))
									bson_embed.add_field(name="No Mod", value = "OD: " + str(data_beatmap_none['od']) + "\r\nAR: " + str(data_beatmap_none['ar']) + "\r\nCS: " + str(data_beatmap_none['cs']) + "\r\nHP: " + str(data_beatmap_none['hp']) + "\r\nStar Rating: " + star_rating_none + "\r\nPP: " + pp_gained_none, inline=True)
									bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_hdon['od']) + "\r\nAR: " + str(data_beatmap_hdon['ar']) + "\r\nCS: " + str(data_beatmap_hdon['cs']) + "\r\nHP: " + str(data_beatmap_hdon['hp']) + "\r\nStar Rating: " + star_rating_hdon + "\r\nPP: " + pp_gained_hdon, inline=True)
									bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_hron['od']) + "\r\nAR: " + str(data_beatmap_hron['ar']) + "\r\nCS: " + str(data_beatmap_hron['cs']) + "\r\nHP: " + str(data_beatmap_hron['hp']) + "\r\nStar Rating: " + star_rating_hron + "\r\nPP: " + pp_gained_hron, inline=True)
									bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_hdhr['od']) + "\r\nAR: " + str(data_beatmap_hdhr['ar']) + "\r\nCS: " + str(data_beatmap_hdhr['cs']) + "\r\nHP: " + str(data_beatmap_hdhr['hp']) + "\r\nStar Rating: " + star_rating_hdhr + "\r\nPP: " + pp_gained_hdhr, inline=True)
									bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_dton['od']) + "\r\nAR: " + str(data_beatmap_dton['ar']) + "\r\nCS: " + str(data_beatmap_dton['cs']) + "\r\nHP: " + str(data_beatmap_dton['hp']) + "\r\nStar Rating: " + star_rating_dton + "\r\nPP: " + pp_gained_dton, inline=True)
									bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_dthd['od']) + "\r\nAR: " + str(data_beatmap_dthd['ar']) + "\r\nCS: " + str(data_beatmap_dthd['cs']) + "\r\nHP: " + str(data_beatmap_dthd['hp']) + "\r\nStar Rating: " + star_rating_dthd + "\r\nPP: " + pp_gained_dthd, inline=True)
									bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_dthr['od']) + "\r\nAR: " + str(data_beatmap_dthr['ar']) + "\r\nCS: " + str(data_beatmap_dthr['cs']) + "\r\nHP: " + str(data_beatmap_dthr['hp']) + "\r\nStar Rating: " + star_rating_dthr + "\r\nPP: " + pp_gained_dthr, inline=True)
									bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_dthh['od']) + "\r\nAR: " + str(data_beatmap_dthh['ar']) + "\r\nCS: " + str(data_beatmap_dthh['cs']) + "\r\nHP: " + str(data_beatmap_dthh['hp']) + "\r\nStar Rating: " + star_rating_dthh + "\r\nPP: " + pp_gained_dthh, inline=True)
								bson_embed.set_thumbnail(url="http://b.ppy.sh/thumb/" + str(song_beats) + "l.jpg")
								await bot.edit_message(msg,embed=bson_embed)
					log("[ONM] - Finished!")
			regex = r"osu\.ppy\.sh\/beatmapsets\/([^a-zA-Z&]+)\/#([a-z&]+)\/([^a-zA-Z&]+)"
			test_str = str(m_message.content)
			matches = re.finditer(regex, test_str)
			for matchNum, match in enumerate(matches):
				log("[ONM] - Found a Beatmap ID in the Sent Message")
				matchNum = matchNum + 1
				if "addmap" in m_message.content:
					await bot.send_message(v_channel,embed=olembed(0xffff00,"!","Don't include the entire link when adding a beatmap to the pool, just use the numbers that come after /b/"))
					log("[ONM] - Ignoring due to addmap command")
				else:
					log("[ONM] - Processing...")
					beatsong_id = match.group(3)
					pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (00%)")
					msg = await bot.send_message(v_channel,embed=pre_embed)
					async with aiohttp.ClientSession() as cs:
						o_url = osu_api + "get_beatmaps?k=" + osu_key + "&b=" + str(beatsong_id)
						async with cs.get(o_url) as s:
							ses = await s.json()
							song_artis = ses[0]['artist']
							song_beats = ses[0]['beatmapset_id']
							song_title = ses[0]['title']
							song_diffi = ses[0]['version']
							song_mappe = ses[0]['creator']
							song_mode = ses[0]['mode']
							
							bson_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="[{0} - {1} ({2})](http://osu.ppy.sh/b/{3}) by {4}\r\n\r\n[Download via Website](http://osu.ppy.sh/d/{3})".format(song_artis,song_title,song_diffi,beatsong_id,song_mappe,song_beats))
							if song_mode == "0":
								data_beatmap_none = await BeatmapDataS(beatsong_id)
								star_rating_none = str(round(data_beatmap_none['stars'],2))
								pp_gained_none = str(round(data_beatmap_none['pp'],2))
								pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (12%)")
								msg = await bot.edit_message(msg,embed=pre_embed)
								data_beatmap_hdon = await BeatmapDataS(beatsong_id,"HD")
								star_rating_hdon = str(round(data_beatmap_hdon['stars'],2))
								pp_gained_hdon = str(round(data_beatmap_hdon['pp'],2))
								pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (25%)")
								msg = await bot.edit_message(msg,embed=pre_embed)
								data_beatmap_hron = await BeatmapDataS(beatsong_id,"HR")
								star_rating_hron = str(round(data_beatmap_hron['stars'],2))
								pp_gained_hron = str(round(data_beatmap_hron['pp'],2))
								pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (37%)")
								msg = await bot.edit_message(msg,embed=pre_embed)
								data_beatmap_dton = await BeatmapDataS(beatsong_id,"DT")
								star_rating_dton = str(round(data_beatmap_dton['stars'],2))
								pp_gained_dton = str(round(data_beatmap_dton['pp'],2))
								pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (50%)")
								msg = await bot.edit_message(msg,embed=pre_embed)
								data_beatmap_hdhr = await BeatmapDataS(beatsong_id,"HDHR")
								star_rating_hdhr = str(round(data_beatmap_hdhr['stars'],2))
								pp_gained_hdhr = str(round(data_beatmap_hdhr['pp'],2))
								pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (62%)")
								msg = await bot.edit_message(msg,embed=pre_embed)
								data_beatmap_dthd = await BeatmapDataS(beatsong_id,"DTHD")
								star_rating_dthd = str(round(data_beatmap_dthd['stars'],2))
								pp_gained_dthd = str(round(data_beatmap_dthd['pp'],2))
								pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (75%)")
								msg = await bot.edit_message(msg,embed=pre_embed)
								data_beatmap_dthr = await BeatmapDataS(beatsong_id,"DTHR")
								star_rating_dthr = str(round(data_beatmap_dthr['stars'],2))
								pp_gained_dthr = str(round(data_beatmap_dthr['pp'],2))
								pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (87%)")
								msg = await bot.edit_message(msg,embed=pre_embed)
								data_beatmap_dthh = await BeatmapDataS(beatsong_id,"DTHDHR")
								star_rating_dthh = str(round(data_beatmap_dthh['stars'],2))
								pp_gained_dthh = str(round(data_beatmap_dthh['pp'],2))
								bson_embed.add_field(name="No Mod", value = "OD: " + str(data_beatmap_none['od']) + "\r\nAR: " + str(data_beatmap_none['ar']) + "\r\nCS: " + str(data_beatmap_none['cs']) + "\r\nHP: " + str(data_beatmap_none['hp']) + "\r\nStar Rating: " + star_rating_none + "\r\nPP: " + pp_gained_none, inline=True)
								bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_hdon['od']) + "\r\nAR: " + str(data_beatmap_hdon['ar']) + "\r\nCS: " + str(data_beatmap_hdon['cs']) + "\r\nHP: " + str(data_beatmap_hdon['hp']) + "\r\nStar Rating: " + star_rating_hdon + "\r\nPP: " + pp_gained_hdon, inline=True)
								bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_hron['od']) + "\r\nAR: " + str(data_beatmap_hron['ar']) + "\r\nCS: " + str(data_beatmap_hron['cs']) + "\r\nHP: " + str(data_beatmap_hron['hp']) + "\r\nStar Rating: " + star_rating_hron + "\r\nPP: " + pp_gained_hron, inline=True)
								bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_hdhr['od']) + "\r\nAR: " + str(data_beatmap_hdhr['ar']) + "\r\nCS: " + str(data_beatmap_hdhr['cs']) + "\r\nHP: " + str(data_beatmap_hdhr['hp']) + "\r\nStar Rating: " + star_rating_hdhr + "\r\nPP: " + pp_gained_hdhr, inline=True)
								bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_dton['od']) + "\r\nAR: " + str(data_beatmap_dton['ar']) + "\r\nCS: " + str(data_beatmap_dton['cs']) + "\r\nHP: " + str(data_beatmap_dton['hp']) + "\r\nStar Rating: " + star_rating_dton + "\r\nPP: " + pp_gained_dton, inline=True)
								bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_dthd['od']) + "\r\nAR: " + str(data_beatmap_dthd['ar']) + "\r\nCS: " + str(data_beatmap_dthd['cs']) + "\r\nHP: " + str(data_beatmap_dthd['hp']) + "\r\nStar Rating: " + star_rating_dthd + "\r\nPP: " + pp_gained_dthd, inline=True)
								bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_dthr['od']) + "\r\nAR: " + str(data_beatmap_dthr['ar']) + "\r\nCS: " + str(data_beatmap_dthr['cs']) + "\r\nHP: " + str(data_beatmap_dthr['hp']) + "\r\nStar Rating: " + star_rating_dthr + "\r\nPP: " + pp_gained_dthr, inline=True)
								bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_dthh['od']) + "\r\nAR: " + str(data_beatmap_dthh['ar']) + "\r\nCS: " + str(data_beatmap_dthh['cs']) + "\r\nHP: " + str(data_beatmap_dthh['hp']) + "\r\nStar Rating: " + star_rating_dthh + "\r\nPP: " + pp_gained_dthh, inline=True)
							bson_embed.set_thumbnail(url="http://b.ppy.sh/thumb/" + str(song_beats) + "l.jpg")
							await bot.edit_message(msg,embed=bson_embed)
			regex = r"osu\.ppy\.sh\/beatmapsets\/([^a-zA-Z&]+)#([a-z&]+)\/([^a-zA-Z&]+)"
			test_str = str(m_message.content)
			matches = re.finditer(regex, test_str)
			for matchNum, match in enumerate(matches):
				log("[ONM] - Found a Beatmap ID in the Sent Message")
				matchNum = matchNum + 1
				if "addmap" in m_message.content:
					await bot.send_message(v_channel,embed=olembed(0xffff00,"!","Don't include the entire link when adding a beatmap to the pool, just use the numbers that come after /b/"))
					log("[ONM] - Ignoring due to addmap command")
				else:
					log("[ONM] - Processing...")
					beatsong_id = match.group(3)
					pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (00%)")
					msg = await bot.send_message(v_channel,embed=pre_embed)
					async with aiohttp.ClientSession() as cs:
						o_url = osu_api + "get_beatmaps?k=" + osu_key + "&b=" + str(beatsong_id)
						async with cs.get(o_url) as s:
							ses = await s.json()
							song_artis = ses[0]['artist']
							song_beats = ses[0]['beatmapset_id']
							song_title = ses[0]['title']
							song_diffi = ses[0]['version']
							song_mappe = ses[0]['creator']
							song_mode = ses[0]['mode']
							
							bson_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="[{0} - {1} ({2})](http://osu.ppy.sh/b/{3}) by {4}\r\n\r\n[Download via Website](http://osu.ppy.sh/d/{3})".format(song_artis,song_title,song_diffi,beatsong_id,song_mappe,song_beats))
							if song_mode == "0":
								data_beatmap_none = await BeatmapDataS(beatsong_id)
								star_rating_none = str(round(data_beatmap_none['stars'],2))
								pp_gained_none = str(round(data_beatmap_none['pp'],2))
								pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (12%)")
								msg = await bot.edit_message(msg,embed=pre_embed)
								data_beatmap_hdon = await BeatmapDataS(beatsong_id,"HD")
								star_rating_hdon = str(round(data_beatmap_hdon['stars'],2))
								pp_gained_hdon = str(round(data_beatmap_hdon['pp'],2))
								pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (25%)")
								msg = await bot.edit_message(msg,embed=pre_embed)
								data_beatmap_hron = await BeatmapDataS(beatsong_id,"HR")
								star_rating_hron = str(round(data_beatmap_hron['stars'],2))
								pp_gained_hron = str(round(data_beatmap_hron['pp'],2))
								pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (37%)")
								msg = await bot.edit_message(msg,embed=pre_embed)
								data_beatmap_dton = await BeatmapDataS(beatsong_id,"DT")
								star_rating_dton = str(round(data_beatmap_dton['stars'],2))
								pp_gained_dton = str(round(data_beatmap_dton['pp'],2))
								pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (50%)")
								msg = await bot.edit_message(msg,embed=pre_embed)
								data_beatmap_hdhr = await BeatmapDataS(beatsong_id,"HDHR")
								star_rating_hdhr = str(round(data_beatmap_hdhr['stars'],2))
								pp_gained_hdhr = str(round(data_beatmap_hdhr['pp'],2))
								pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (62%)")
								msg = await bot.edit_message(msg,embed=pre_embed)
								data_beatmap_dthd = await BeatmapDataS(beatsong_id,"DTHD")
								star_rating_dthd = str(round(data_beatmap_dthd['stars'],2))
								pp_gained_dthd = str(round(data_beatmap_dthd['pp'],2))
								pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (75%)")
								msg = await bot.edit_message(msg,embed=pre_embed)
								data_beatmap_dthr = await BeatmapDataS(beatsong_id,"DTHR")
								star_rating_dthr = str(round(data_beatmap_dthr['stars'],2))
								pp_gained_dthr = str(round(data_beatmap_dthr['pp'],2))
								pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Getting Beatmap Information... (87%)")
								msg = await bot.edit_message(msg,embed=pre_embed)
								data_beatmap_dthh = await BeatmapDataS(beatsong_id,"DTHDHR")
								star_rating_dthh = str(round(data_beatmap_dthh['stars'],2))
								pp_gained_dthh = str(round(data_beatmap_dthh['pp'],2))
								bson_embed.add_field(name="No Mod", value = "OD: " + str(data_beatmap_none['od']) + "\r\nAR: " + str(data_beatmap_none['ar']) + "\r\nCS: " + str(data_beatmap_none['cs']) + "\r\nHP: " + str(data_beatmap_none['hp']) + "\r\nStar Rating: " + star_rating_none + "\r\nPP: " + pp_gained_none, inline=True)
								bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_hdon['od']) + "\r\nAR: " + str(data_beatmap_hdon['ar']) + "\r\nCS: " + str(data_beatmap_hdon['cs']) + "\r\nHP: " + str(data_beatmap_hdon['hp']) + "\r\nStar Rating: " + star_rating_hdon + "\r\nPP: " + pp_gained_hdon, inline=True)
								bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_hron['od']) + "\r\nAR: " + str(data_beatmap_hron['ar']) + "\r\nCS: " + str(data_beatmap_hron['cs']) + "\r\nHP: " + str(data_beatmap_hron['hp']) + "\r\nStar Rating: " + star_rating_hron + "\r\nPP: " + pp_gained_hron, inline=True)
								bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_hdhr['od']) + "\r\nAR: " + str(data_beatmap_hdhr['ar']) + "\r\nCS: " + str(data_beatmap_hdhr['cs']) + "\r\nHP: " + str(data_beatmap_hdhr['hp']) + "\r\nStar Rating: " + star_rating_hdhr + "\r\nPP: " + pp_gained_hdhr, inline=True)
								bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_dton['od']) + "\r\nAR: " + str(data_beatmap_dton['ar']) + "\r\nCS: " + str(data_beatmap_dton['cs']) + "\r\nHP: " + str(data_beatmap_dton['hp']) + "\r\nStar Rating: " + star_rating_dton + "\r\nPP: " + pp_gained_dton, inline=True)
								bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_dthd['od']) + "\r\nAR: " + str(data_beatmap_dthd['ar']) + "\r\nCS: " + str(data_beatmap_dthd['cs']) + "\r\nHP: " + str(data_beatmap_dthd['hp']) + "\r\nStar Rating: " + star_rating_dthd + "\r\nPP: " + pp_gained_dthd, inline=True)
								bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_dthr['od']) + "\r\nAR: " + str(data_beatmap_dthr['ar']) + "\r\nCS: " + str(data_beatmap_dthr['cs']) + "\r\nHP: " + str(data_beatmap_dthr['hp']) + "\r\nStar Rating: " + star_rating_dthr + "\r\nPP: " + pp_gained_dthr, inline=True)
								bson_embed.add_field(name="", value = "OD: " + str(data_beatmap_dthh['od']) + "\r\nAR: " + str(data_beatmap_dthh['ar']) + "\r\nCS: " + str(data_beatmap_dthh['cs']) + "\r\nHP: " + str(data_beatmap_dthh['hp']) + "\r\nStar Rating: " + star_rating_dthh + "\r\nPP: " + pp_gained_dthh, inline=True)
							bson_embed.set_thumbnail(url="http://b.ppy.sh/thumb/" + str(song_beats) + "l.jpg")
							await bot.edit_message(msg,embed=bson_embed)
	await bot.process_commands(m_message)

# @bot.event
# async def on_command_error(error, ctx):
	# if isinstance(error, commands.CommandNotFound):
		# await bot.send_message(ctx.message.author,"This is not a valid command! Try +help to see what's available.")
		# await bot.delete_message(ctx.message)

@bot.event
async def on_member_join(member):
	log("[OMJ] - New member joined!")
	server = bot.get_channel("")
	channel = bot.get_channel("")
	fmt = 'Welcome {0.mention} to the **Map of the Week** discord!\r\n\r\nRead {1.mention} for rules and details on the MotW!\r\nMake sure you link your account with +link ``osu username``. You can run the +link command in this channel.'
	await bot.send_message(bot.get_channel(channel_general), fmt.format(member,channel))

@bot.event
async def on_member_remove(member):
	log("[OML] - Member left!") 
	try:
		member_id = member.id
		member_name = member.name
		mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
		mysql_curs = await mysql_conn.cursor()
		await mysql_curs.execute("SELECT * from linked_players WHERE DISCORD_ID = '"+str(member_id)+"'")
		v_result = await mysql_curs.fetchone()
		if v_result:
			playerid = v_result[2]
			playername = v_result[3]
			bracket = v_result[6].lower()
		
			await mysql_curs.execute("DELETE FROM motw_scores_"+str(bracket)+" WHERE player_id = "+str(playerid)+"")
			await mysql_conn.commit()
			await mysql_curs.execute("DELETE FROM roll_"+str(bracket)+" WHERE UserID = '"+str(member_id)+"'")
			await mysql_conn.commit()
			await mysql_curs.execute("DELETE FROM linked_players WHERE DISCORD_ID = '"+str(member_id)+"'")
			await mysql_conn.commit()
			msg = await bot.send_message(bot.get_channel(channel_general), playername+' left the MotW. Click :regional_indicator_f: to pay respects!')
			await bot.add_reaction(msg,"\U0001f1eb")
			log("[on_member_remove] " + str(member_name) + " (" + str(member_id) + ") left the tourney.")
	except Exception as e:
		log("[on_member_remove] Error: "+str(e))
		
@bot.command(pass_context=True,aliases=['setosu'])
async def link(ctx, *,player_name: str="!"):
	'''Link your osu! account to your discord ID!'''
	sender_author_id = ctx.message.author.id
	sender_author_name = ctx.message.author.name
	sender_author = ctx.message.author
	if sender_author_id == "":
		await bot.send_message(sender_author,embed=olembed(0xff0000,ctx.message.author.name,"You cannot join the MotW at the moment. Please speak to Staff."))
	else:
		try:
			if player_name == "!":
				await bot.send_message(sender_author, embed=olembed(0xff0000,"!","You didn't specify your osu! player name!"))
			else:
				generated_hash = hashlib.sha224(bytes(str(player_name)+str(time.strftime("%c")),'utf-8')).hexdigest()
				generated_hash_mini = "motw-" + generated_hash[4:12]
				log(sender_author_name +" ["+str(sender_author_id)+"] requested to link their account. Code is "+generated_hash_mini+".")
				try:
					async with aiohttp.ClientSession() as cs:
						url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name.replace(" ","+") + "&m=0"
						async with cs.get(url) as r:
							res = await r.json()
							if not res:
								await bot.send_message(sender_author,embed=olembed(0xff0000,"!","osu! does not list a player with that name."))
								log(sender_author_name +" ["+str(sender_author_id)+"] entered an incorrect osu player name to link with.")
							else:
								r_player = res[0]['username']
								r_playerid = res[0]['user_id']
								r_rank= res[0]['pp_rank']
								mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
								mysql_curs = await mysql_conn.cursor()
								await mysql_curs.execute("SELECT * from linked_players WHERE DISCORD_ID = '"+str(sender_author_id)+"'")
								v_result = await mysql_curs.fetchone()
								if v_result:
									await mysql_curs.execute("UPDATE linked_players SET PLAYER_ID = '"+r_playerid+"',PLAYER_NAME='"+r_player+"',RANK='"+r_rank+"',LINK_CODE = '"+generated_hash_mini+"',LINKED = 0 WHERE DISCORD_ID = '"+str(sender_author_id)+"'")
								else:
									await mysql_curs.execute("INSERT INTO linked_players (DISCORD_ID,PLAYER_ID,PLAYER_NAME,RANK,LINK_CODE,LINKED) VALUES ('"+sender_author_id+"','"+r_playerid+"','"+r_player+"','"+r_rank+"','"+generated_hash_mini+"',0)")
								await mysql_conn.commit()
								mysql_conn.close()
								await bot.send_message(sender_author,"Hi " + sender_author_name + ",\r\n\r\nPlease authenticate your osu! account by setting the following code\r\n\r\n``"+ generated_hash_mini + "``\r\n\r\nas your location on your osu! profile.\r\n\r\nOnce done, send the +auth ``osu_playername`` command.\r\n\r\nhttps://themeq.s-ul.eu/9p074QqK.gif")
								log(sender_author_name +" ["+str(sender_author_id)+"] recieved the link message.")
				except Exception as e:
					await bot.send_message(sender_author,"Hi " + sender_author_name + ",\r\n\r\nSorry about this, but the osu!api borked. Please try linking again in a minute. Thanks.")
					log(sender_author_name +" ["+str(sender_author_id)+"] osu!api borked. Couldn't get details. "+str(sys.exc_info()[0]))
					log("[link] Error: "+str(e))
			await bot.delete_message(ctx.message)
		except Exception as e:
			await bot.say(embed=olembed(0xff0000,ctx.message.author.name,"We couldn't link your account. Please ensure you can recieve PM's from people who you aren't friends with!"))
			log("[link] Error: " + str(e))

@bot.command(pass_context=True)
async def auth(ctx, *, player_name: str="!"):
	'''Authenticate your osu! account after linking it!'''
	sender_author_id = ctx.message.author.id
	sender_author_name = ctx.message.author.name
	sender_author = ctx.message.author
	if sender_author_id == "":
		await bot.send_message(sender_author,embed=olembed(0xff0000,"!","You cannot join the MotW at the moment. Please speak to Staff."))
	else:
		if player_name == "!":
			await bot.send_message(sender_author, embed=olembed(0xff0000,"!","You didn't specify your osu! player name!"))
			log(str(sender_author) +" ["+str(sender_author_id)+"] entered an incorrect osu player name to auth with.")
		else:
			mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
			mysql_curs = await mysql_conn.cursor()
			await mysql_curs.execute("SELECT LINK_CODE,RANK from linked_players WHERE DISCORD_ID = '"+str(sender_author_id)+"'")
			v_result = await mysql_curs.fetchone()
			if not v_result:
				await bot.send_message(sender_author,embed=olembed(0xff0000,"!","Hi " + sender_author_name + ",\r\n\r\nYou haven't generated a link code for your account yet. Please type in +link ``osu! playername``."))
				log(str(sender_author) +" ["+str(sender_author_id)+"] tried to authenticate their account but haven't linked it yet.")
			else:			
				response = urllib.request.urlopen("http://osu.ppy.sh/u/"+player_name)
				html = response.read()
				text = html.decode()
				endOfTemp = text.find(v_result[0])
				if endOfTemp > 0:
					await bot.send_message(sender_author,embed=olembed(0x00ff00,"!","Your osu! account has now been linked to your Discord ID. You can now participate in the MotW!\r\n\r\nPlease ensure you read the #welcome channel."))
					log(str(sender_author) +" ["+str(sender_author_id)+"] completed the authentication process as "+player_name+".")
					await mysql_curs.execute("UPDATE linked_players SET LINKED=1 WHERE DISCORD_ID = '"+str(sender_author_id)+"'")
					await mysql_conn.commit()
					async with aiohttp.ClientSession() as cs:
						url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name + "&m=0"
						async with cs.get(url) as r:
							player_bracket = "XX"
							tai_bracket = "TKA"
							man_bracket = "MEZ"
							ctb_bracket = "CCU"
							res = await r.json()
							r_rank = res[0]['pp_rank']
							v_server = bot.get_server(main_server)
							await bot.change_nickname(v_server.get_member(sender_author_id),player_name)
							if int(r_rank) >= 1 and int(r_rank) <= 2000:
								player_bracket = "EX"
								role = discord.utils.get(v_server.roles, name='EX - 1 to 2k')
							elif int(r_rank) > 2000 and int(r_rank) <= 5000:
								player_bracket = "IN"
								role = discord.utils.get(v_server.roles, name='IN - 2k to 5k')
							elif int(r_rank) > 5000 and int(r_rank) <= 10000:
								player_bracket = "HD"
								role = discord.utils.get(v_server.roles, name='HD - 5k to 10k')
							elif int(r_rank) > 10000 and int(r_rank) <= 25000:
								player_bracket = "NM"
								role = discord.utils.get(v_server.roles, name='NM - 10k to 25k')
							elif int(r_rank) > 25000 and int(r_rank) <= 50000:
								player_bracket = "EZ"
								role = discord.utils.get(v_server.roles, name='EZ - 25k to 50k')
							elif int(r_rank) > 50000 and int(r_rank) <= 100000:
								player_bracket = "BA"
								role = discord.utils.get(v_server.roles, name='BA - 50k to 100k')
							elif int(r_rank) > 100000 and int(r_rank) <= 200000:
								player_bracket = "NW"
								role = discord.utils.get(v_server.roles, name='NW - 100k to 200k')
							elif int(r_rank) > 200000 and int(r_rank) <= 1000000:
								player_bracket = "WH"
								role = discord.utils.get(v_server.roles, name='WH - 200k to 1000k')
							else:
								player_bracket = "XX"
								role = discord.utils.get(v_server.roles, name='XX - 1000k+')
							try:
								o_url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name + "&m=1"
								async with cs.get(o_url) as g:
									gur = await g.json()
									if gur:
										n_name = gur[0]['username']
										t_rank = gur[0]['pp_rank']
										if t_rank is None:
											t_rank = "0"
										if int(t_rank) >= 1 and int(t_rank) <= 1000:
											tai_bracket = "TON"
										elif int(t_rank) > 1000 and int(t_rank) <= 2500:
											tai_bracket = "TMU"
										elif int(t_rank) > 2500 and int(t_rank) <= 5000:
											tai_bracket = "TFU"
										else:
											tai_bracket = "TKA"
									else:
										log(player_name + " [Taiko] check didn't return anything from osu!api, please try again manually.")
										tai_bracket = "TKA"
							except Exception as e:
								log("[rankupdate>tai]  Error: " + str(e))
							try:
								o_url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name + "&m=2"
								async with cs.get(o_url) as g:
									gur = await g.json()
									if gur:
										n_name = gur[0]['username']
										c_rank = gur[0]['pp_rank']
										if c_rank is None:
											c_rank = "0"
										if int(c_rank) >= 1 and int(c_rank) <= 1000:
											ctb_bracket = "CRA"
										elif int(c_rank) > 1000 and int(c_rank) <= 2500:
											ctb_bracket = "CPL"
										elif int(c_rank) > 2500 and int(c_rank) <= 5000:
											ctb_bracket = "CSA"
										else:
											ctb_bracket = "CCU"
									else:
										log(player_name + " [CTB] check didn't return anything from osu!api, please try again manually.")
										ctb_bracket = "CCU"
							except Exception as e:
								log("[rankupdate>ctb] Error: " + str(e))
							try:
								o_url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name + "&m=3"
								async with cs.get(o_url) as g:
									gur = await g.json()
									if gur:
										n_name = gur[0]['username']
										m_rank = gur[0]['pp_rank']
										if m_rank is None:
											m_rank = "0"
										if int(m_rank) >= 1 and int(m_rank) <= 4000:
											man_bracket = "MMX"
										elif int(m_rank) > 4000 and int(m_rank) <= 10000:
											man_bracket = "MHD"
										elif int(m_rank) > 10000 and int(m_rank) <= 30000:
											man_bracket = "MNM"
										else:
											man_bracket = "MEZ"
									else:
										log(player_name + " [Mania] check didn't return anything from osu!api, please try again manually.")
										man_bracket = "MEZ"
							except Exception as e:
								log("[rankupdate>man] Error: " + str(e))
							try:
								log(player_name + " is going into " + player_bracket + "," + tai_bracket +","+ ctb_bracket+ ","+ man_bracket)
								tai_role = discord.utils.get(v_server.roles, name=osu_roles[tai_bracket])
								ctb_role = discord.utils.get(v_server.roles, name=osu_roles[ctb_bracket])
								man_role = discord.utils.get(v_server.roles, name=osu_roles[man_bracket])
								await bot.replace_roles(v_server.get_member(ctx.message.author.id),role,tai_role,ctb_role,man_role)
							except Exception as e: 
								log("Couldn't change roles for " + player_name)
								log("[rankupdate>roles] Error: " +str(e))
							await mysql_curs.execute("UPDATE linked_players SET BRACKET='"+player_bracket+"',TAIKO_RANK='"+str(t_rank)+"',TAIKO_BRACKET='"+tai_bracket+"',CTB_RANK='"+str(c_rank)+"',CTB_BRACKET='"+ctb_bracket+"',MANIA_RANK='"+str(m_rank)+"',MANIA_BRACKET='"+man_bracket+"' WHERE DISCORD_ID = '"+str(sender_author_id)+"'")
							await mysql_conn.commit()
							channel = bot.get_channel(channel_announcements)
							try:
								welcome = bot.get_channel("316841596228468736")
								motw_channel = discord.utils.get(v_server.channels, name="motw-" + player_bracket.lower(), type=discord.ChannelType.text) 
								fmt = '{0.mention} is now participating in the **Map of the Week**! Good Luck and Have Fun!\r\n\r\nPlease read {1.mention} and run your MotW related commands here!'
								await bot.send_message(motw_channel, fmt.format(ctx.message.author,welcome))
							except Exception as e:
								log("[auth] Error: "+str(e))
				else:
					await bot.send_message(sender_author,embed=olembed(0xff0000,"!","Hmmm, we couldn't find the link code on your profile page. You need to do this so we can make sure the profile belongs to you."))
					log(str(sender_author) +" ["+str(sender_author_id)+"] tried to authenticate but has not changed their location to the code.")
				mysql_conn.close()
	await bot.delete_message(ctx.message)

@bot.command(pass_context=True)
async def motw(ctx, bracket: str="!"):
	"""Get the current Map of the Week! """
	get_date = int(time.strftime("%d"))
	get_time = int(time.strftime("%H"))
	if get_date == 29 or get_date == 30 or get_date == 31 or (get_date == 28 and get_time >= 23):
		await bot.say(embed=olembed(0xffff00,"!","The MotW for the last month is now finished! A new round starts on the 1st!"))
	else:
		sender_channel_id = ctx.message.channel.id
		c_wel = bot.get_channel("")
		if bracket == "!":
			sender_channel = getChannel(ctx)
		elif bracket.upper() in ["WH","NW","BA","EZ","NM","HD","IN","EX","TON","TMU","TFU","TKA","MMX","MHD","MNM","MEZ","CRA","CPL","CSA","CCU"]:
			sender_channel = bracket.upper()
		else:
			sender_channel = getChannel(ctx)
		if sender_channel == "ERROR":
			if sender_channel_id == "":
				await bot.say(embed=olembed(0xffff00,"!","Welcome to the Map of the Week Discord! Please read {0.mention} to get started!".format(c_wel)))
			else:
				await bot.say(embed=olembed(0xff0000,"!","You can't check the Map of the Week from this channel. Please read {0.mention} to get started!".format(c_wel)))
		else:
			mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
			mysql_curs = await mysql_conn.cursor()
			mysql_quer = "SELECT map_id,date_range_tstmp,mode FROM beatmaps WHERE bracket = '" + sender_channel + "'"
			await mysql_curs.execute(mysql_quer)
			v_result = await mysql_curs.fetchone()
			i_beatmapid = v_result[0]
			i_mode = v_result[2]
			async with aiohttp.ClientSession() as cs:
				o_url = osu_api + "get_beatmaps?k=" + osu_key + "&b=" + str(i_beatmapid) + "&m="+str(i_mode)
				async with cs.get(o_url) as s:
					ses = await s.json()
					song_artis = ses[0]['artist']
					song_beats = ses[0]['beatmapset_id']
					song_title = ses[0]['title']
					song_diffi = ses[0]['version']
					song_mappe = ses[0]['creator']
					if bracket != "!":
						motw_embed = discord.Embed(colour=discord.Colour(0xFFFF00), description="**Map of the Week for the "+sender_channel+" bracket!**\r\n\r\n[{0} - {1} ({2})](http://osu.ppy.sh/b/{3}) by {4}\r\n\r\n[Download via Website](http://osu.ppy.sh/d/{5})\r\n[Download via osu!Direct (Supporter Only)](http://themeq.xyz/r.php?b={5})".format(song_artis,song_title,song_diffi,i_beatmapid,song_mappe,song_beats), timestamp=v_result[1])
					else:
						motw_embed = discord.Embed(colour=discord.Colour(0xFFFF00), description="**Map of the Week!**\r\n\r\nType **+scores** for latest scores!\r\n\r\n[{0} - {1} ({2})](http://osu.ppy.sh/b/{3}) by {4}\r\n\r\n[Download via Website](http://osu.ppy.sh/d/{5})\r\n[Download via osu!Direct (Supporter Only)](http://themeq.xyz/r.php?b={5})".format(song_artis,song_title,song_diffi,i_beatmapid,song_mappe,song_beats), timestamp=v_result[1])
					motw_embed.set_thumbnail(url="http://b.ppy.sh/thumb/" + str(song_beats) + "l.jpg")
					motw_embed.set_footer(text="This round ends")
					await bot.say(embed=motw_embed)
			mysql_conn.close()
	await bot.delete_message(ctx.message)

@bot.command(pass_context=True, aliases=['difficulty'])
async def stars(ctx):
	'''Get your brackets map limitations!'''
	s_min = 0
	s_max = 4
	v_channel = getChannel(ctx)
	c_wel = bot.get_channel("")
	if v_channel == "ERROR":
		await bot.say(embed=olembed(0x0000ff,"!","You can't check the difficulty rating from this channel. Please read {0.mention} to get started!".format(c_wel)))
	else:
		if v_channel == "WH" or v_channel == "TKA" or v_channel == "MEZ" or v_channel == "CCU":
			s_min = 2
			s_max = 4
		if v_channel == "NW":
			s_min = 2.5
			s_max = 4.5
		if v_channel == "BA" or v_channel == "TFU" or v_channel == "MNM" or v_channel == "CSA":
			s_min = 3
			s_max = 5
		if v_channel == "EZ":
			s_min = 3.5
			s_max = 5.5
		if v_channel == "NM" or v_channel == "TMU" or v_channel == "MHD" or v_channel == "CPL":
			s_min = 4
			s_max = 6
		if v_channel == "HD":
			s_min = 4.5
			s_max = 7
		if v_channel == "IN" or v_channel == "TON" or v_channel == "MMX" or v_channel == "CRA":
			s_min = 5
			s_max = 7.5
		if v_channel == "EX":
			s_min = 5.5
			s_max = 8
		await bot.say(embed=olembed(0x0000ff,"!","This bracket has a difficulty range of " + str(s_min) + "* and "+str(s_max)+"*\r\n\r\nThe map must be more than 1 minute long and less than 7 minutes long."))
	await bot.delete_message(ctx.message)

@bot.command(pass_context=True, aliases=['leader'])
async def leaderboards(ctx,bracket: str="!"):
	'''Get this months current leaderboard!'''
	try:
		if bracket == "!":
			v_channel = getChannel(ctx)
		elif bracket.upper() in ["WH","NW","BA","EZ","NM","HD","IN","EX","TON","TMU","TFU","TKA","MMX","MHD","MNM","MEZ","CRA","CPL","CSA","CCU"]:
			v_channel = bracket.upper()
		else:
			v_channel = getChannel(ctx)
		c_wel = bot.get_channel("")
		if v_channel == "ERROR":
			if bracket != "!":
				await bot.say(embed=olembed(0xff0000,"!","You entered an invalid bracket. Please try one of the following: WH,NW,BA,EZ,NM,HD,IN,EX,TON,TMU,TFU,TKA,MMX,MHD,MNM,MEZ,CRA,CPL,CSA,CCU"))
			else:
				await bot.say(embed=olembed(0xff0000,"!","You cannot see the scores for a bracket from this channel. Please read {0.mention} to get started!".format(c_wel)))
		else:
			mysql_conn = await aiomysql.connect(host = mysql_host, port=3306, user=mysql_user,password=mysql_pass, db = mysql_data)
			mysql_curs = await mysql_conn.cursor()
			if v_channel in ["WH","NW","BA","EZ","NM","HD","IN","EX"]:
				await mysql_curs.execute("SELECT * FROM linked_players WHERE BRACKET = '"+v_channel+"' and LINKED = 1 and SCORE_MONTH > 0 ORDER BY SCORE_MONTH DESC LIMIT 0,10")
			if v_channel in ["TON","TMU","TFU","TKA"]:
				await mysql_curs.execute("SELECT * FROM linked_players WHERE TAIKO_BRACKET = '"+v_channel+"' and LINKED = 1 and SCORE_MONTH_TAIKO > 0 ORDER BY SCORE_MONTH_TAIKO DESC LIMIT 0,10")
			if v_channel in ["MMX","MHD","MNM","MEZ"]:
				await mysql_curs.execute("SELECT * FROM linked_players WHERE MANIA_BRACKET = '"+v_channel+"' and LINKED = 1 and SCORE_MONTH_MANIA > 0 ORDER BY SCORE_MONTH_MANIA DESC LIMIT 0,10")
			if v_channel in ["CRA","CPL","CSA","CCU"]:
				await mysql_curs.execute("SELECT * FROM linked_players WHERE CTB_BRACKET = '"+v_channel+"' and LINKED = 1 and SCORE_MONTH_CTB > 0 ORDER BY SCORE_MONTH_CTB DESC LIMIT 0,10")
			result = await mysql_curs.fetchall()
			count = 1
			ostring = "**Current Top 10 Leaderboard for this Month ("+v_channel+" Bracket)**\r\n\r\n"
			for row in result:
				p_name = row[3]
				p_id = row[2]
				if v_channel in ["WH","NW","BA","EZ","NM","HD","IN","EX"]:
					p_rank = row[5]
					p_points = row[15]
				if v_channel in ["TON","TMU","TFU","TKA"]:
					p_rank = row[7]
					p_points = row[16]
				if v_channel in ["MMX","MHD","MNM","MEZ"]:
					p_rank = row[9]
					p_points = row[17]
				if v_channel in ["CRA","CPL","CSA","CCU"]:
					p_rank = row[11]
					p_points = row[18]
				ostring = ostring + "{0} \t- [{1}](http://osu.ppy.sh/u/{2}) - Locked Rank: #{3:,} - Points: {4}\r\n\r\n".format(Ordinal(count),p_name,str(p_id),int(p_rank),str(p_points))
				count = count + 1
			embed = discord.Embed(colour=discord.Colour(0x6600FF), description=ostring)
			embed.set_footer(text=str(ctx.message.author.name) + " ran this command.")
			await bot.say(embed=embed)
			mysql_conn.close()
		await bot.delete_message(ctx.message)
	except Exception as e:
		log("[leaderboards] Error: "+str(e))

@bot.command(pass_context=True)
@commands.has_permissions(manage_channels=True)
async def asbot(ctx, * ,message):
	await bot.delete_message(ctx.message)
	await bot.say(message)

@bot.command(pass_context=True, aliases=['addbeatmap'])
async def addmap(ctx,beatmap_id:str="0"):
	'''Add a map to your bracket pool for the MotW!'''
	try:
		v_channel = getChannel(ctx)
		c_wel = bot.get_channel("")
		v_roll = getRole(v_channel)
		v_id = ctx.message.author.id
		mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
		mysql_curs = await mysql_conn.cursor()
		if v_channel == "ERROR":
			await bot.say(embed=olembed(0xff0000,"!","You can't add a map to the map pool from this channel. Please read {0.mention} to get started!".format(c_wel)))
		else:
			if beatmap_id == "0":
				await bot.say(embed=olembed(0xff0000,"!","You didn't specify a beatmap ID!"))
			else:
				async with aiohttp.ClientSession() as cs:
					if "&m=0" in beatmap_id or "&m=1" in beatmap_id or "&m=2" in beatmap_id or "&m=3" in beatmap_id:
						beatmap_id = beatmap_id[:-4]
					if v_channel in ["WH","NW","BA","EZ","NM","HD","IN","EX"]:
						url = osu_api + "get_beatmaps?k=" + osu_key + "&b=" + str(beatmap_id) + "&m=0&limit=1"
						gm = "0"
					if v_channel in ["TON","TMU","TFU","TKA"]:
						url = osu_api + "get_beatmaps?k=" + osu_key + "&b=" + str(beatmap_id) + "&m=1&limit=1"
						gm = "1"
					if v_channel in ["MMX","MHD","MNM","MEZ"]:
						url = osu_api + "get_beatmaps?k=" + osu_key + "&b=" + str(beatmap_id) + "&m=3&limit=1"
						gm = "3"
					if v_channel in ["CRA","CPL","CSA","CCU"]:
						url = osu_api + "get_beatmaps?k=" + osu_key + "&b=" + str(beatmap_id) + "&m=2&limit=1"
						gm = "2"
					async with cs.get(url) as s:
						ses = await s.json()
						if not ses:
							if "http" not in beatmap_id:
								await bot.say(embed=olembed(0xff0000,"!","Sorry, but this map either does not exist, is not the correct game mode or just cannot be added to the map pool right now.\r\nIf you are definitely sure it exists, make sure you are copying the beatmap ID and not the song ID."))
						else:
							song_artis = ses[0]['artist']
							song_beats = ses[0]['beatmapset_id']
							song_title = ses[0]['title']
							song_diffi = ses[0]['version']
							song_mappe = ses[0]['creator']
							song_appro = ses[0]['approved']
							song_srate = ses[0]['difficultyrating']
							song_lengt = ses[0]['hit_length']
							s_min = 0
							s_max = 4
							if v_channel == "WH" or v_channel == "TKA" or v_channel == "MEZ" or v_channel == "CCU":
								s_min = 2
								s_max = 4
							if v_channel == "NW":
								s_min = 2.5
								s_max = 4.5
							if v_channel == "BA" or v_channel == "TFU" or v_channel == "MNM" or v_channel == "CSA":
								s_min = 3
								s_max = 5
							if v_channel == "EZ":
								s_min = 3.5
								s_max = 5.5
							if v_channel == "NM" or v_channel == "TMU" or v_channel == "MHD" or v_channel == "CPL":
								s_min = 4
								s_max = 6
							if v_channel == "HD":
								s_min = 4.5
								s_max = 7
							if v_channel == "IN" or v_channel == "TON" or v_channel == "MMX" or v_channel == "CRA":
								s_min = 5
								s_max = 7.5
							if v_channel == "EX":
								s_min = 5.5
								s_max = 8
							if int(song_appro) <= 0 or int(song_appro) == 3:
								await bot.say(embed=olembed(0xff0000,"!","Sorry, but unranked, wip and graveyard maps can't be tracked, choose another!"))
							else:
								if float(song_srate) < s_min:
									await bot.say(embed=olembed(0xff0000,"!","Sorry, but this beatmap has been deemed too easy to be added to this bracket, choose another! ("+str(s_min)+"* to "+str(s_max)+"*)"))
								elif float(song_srate) > s_max:
									await bot.say(embed=olembed(0xff0000,"!","Sorry, but this beatmap has been deemed too hard to be added to this bracket, choose another! ("+str(s_min)+"* to "+str(s_max)+"*)"))
								else:
									if int(song_lengt) > 419:
										await bot.say(embed=olembed(0xff0000,"!","Sorry, but this beatmap is a bit too long! Try a map under 7 minutes in length (excluding drain time)."))
									elif int(song_lengt) < 61:
										await bot.say(embed=olembed(0xff0000,"!","Sorry, but this beatmap is a bit too short! Try a map over 1 minute in length (excluding drain time)."))
									else:
										''' Check if player has a pass on this map recently to prevent shitmaps '''
										await mysql_curs.execute("SELECT PLAYER_ID FROM linked_players WHERE DISCORD_ID = '"+v_id+"'")
										v_result = await mysql_curs.fetchone()
										url = osu_api + "get_user_recent?k=" + osu_key + "&u=" + v_result[0].replace(" ","+") + "&m="+gm+"&limit=50"
										async with cs.get(url) as s:
											ses = await s.json()
											log("Name: " + ctx.message.author.name)
											if not ses and str(ctx.message.author.name) not in ["TheMeq","Athrun","Lefafel","OG Baku","Renko","Weavile"]:
												await bot.say(embed=olembed(0xff0000,"!","We couldn't find your recent play data for some reason. Please try again in a minute."))
											else:
												found = 0
												has_r = 0
												has_a = 0
												has_m = 0
												for row in ses:
													if row["beatmap_id"] == beatmap_id:
														found = 1
														log("Has Rank: " + row["rank"])
														if row["rank"] in "F,D,C,B,A,S,SH,X,XH":
															has_r = 1
															cscore_score = int(row['score'])
															cscore_maxco = row['maxcombo']
															cscore_fifty = row['count50']
															cscore_hundr = row['count100']
															cscore_three = row['count300']
															cscore_misse = row['countmiss']
															cscore_katu = row['countkatu']
															cscore_geki = row['countgeki']
															cscore_modif = row['enabled_mods']
															cscore_accur = round(((((int(cscore_three) * 300) + (int(cscore_hundr) * 100) + (int(cscore_fifty) * 50) + (int(cscore_misse) * 0)) / ((int(cscore_three) + int(cscore_hundr) + int(cscore_fifty) + int(cscore_misse)) * 300)) * 100),2)
															if gm == 2:
																cscore_accur = round((((int(cscore_three)) + (int(cscore_hundr)) + (int(cscore_fifty))) / ((int(cscore_three)) + (int(cscore_hundr)) + (int(cscore_fifty)) + (int(cscore_misse)) + (int(cscore_katu))))*100,2)
															if gm == 3:
																cscore_accur = round((((int(cscore_fifty) * 50) + (int(cscore_hundr) * 100) + (int(cscore_katu) * 200) + (int(cscore_geki) * 300) + (int(cscore_three) * 300)) / ((int(cscore_fifty)+int(cscore_hundr)+int(cscore_katu)+int(cscore_geki)+int(cscore_three)+int(cscore_misse)) * 300) * 100) ,2)
															if cscore_accur > 88 or gm == "2":
																has_a = 1
															used_mods = GetMods(cscore_modif)
															if used_mods:
																gam = ""
																for mods in used_mods:
																	gam = gam + osu_mods_t[str(mods)] + ""
															else:
																gam = ""
															if gam == "" or checkMods(gam)==1:
																	has_m = 1
												log("Found BeatMap: " + str(found) + "| Has Rank: " + str(has_r) + "| Has Acc: "+ str(has_a) + "| Has Mods: "+ str(has_m))
												if (found == 1 and has_r == 1 and has_a == 1 and has_m == 1) or str(ctx.message.author.name) in ["TheMeq","Athrun","Lefafel","OG Baku","Renko","Weavile"]:
													mysql_query = "SELECT COUNT(*) AS COUN FROM "+v_roll+" where UserID = '" + v_id + "'"
													await mysql_curs.execute(mysql_query)
													v_result = await mysql_curs.fetchone()
													try:
														if v_result[0] == 0 or str(ctx.message.author.name) in ["TheMeq","Athrun","Lefafel","OG Baku","Renko","Weavile"]:
															mysql_query = "INSERT INTO "+v_roll+" (UserID,BeatmapID,BeatmapArtist,BeatmapTitle,BeatmapVersion,BeatmapMapper) VALUES ('"+str(v_id).replace("'","")+"','"+str(beatmap_id).replace("'","")+"','"+str(song_artis).replace("'","")+"','"+str(song_title).replace("'","")+"','"+str(song_diffi).replace("'","")+"','"+str(song_mappe).replace("'","")+"')"
															await mysql_curs.execute(mysql_query)
															await mysql_conn.commit()
															embed = discord.Embed(colour=discord.Colour(0xFFFF00), description="Beatmap **["+str(song_artis)+" - "+str(song_title)+"](http://osu.ppy.sh/b/"+str(beatmap_id)+")** ("+str(song_diffi)+") by "+str(song_mappe)+" has been added to the pool!")
															embed.set_footer(text=str(ctx.message.author.name) + " ran this command.")
															await bot.say(embed=embed)
														else:
															mysql_query = "UPDATE "+v_roll+" SET BeatmapID='"+str(beatmap_id)+"',BeatmapArtist='"+str(song_artis).replace("'","")+"',BeatmapTitle='"+str(song_title).replace("'","")+"',BeatmapVersion='"+str(song_diffi).replace("'","")+"',BeatmapMapper='"+str(song_mappe).replace("'","")+"' WHERE UserID = '"+str(v_id)+"'"
															
															await mysql_curs.execute(mysql_query)
															await mysql_conn.commit()
															embed = discord.Embed(colour=discord.Colour(0xFFFF00), description="Beatmap **["+str(song_artis)+" - "+str(song_title)+"](http://osu.ppy.sh/b/"+str(beatmap_id)+")** ("+str(song_diffi)+") by "+str(song_mappe)+" has replaced your previous selection and has been added to the pool!")
															embed.set_footer(text=str(ctx.message.author.name) + " ran this command.")
															await bot.say(embed=embed)
													except Exception as e:
														log("[addmap] Error: "+str(e))
												else:
													await bot.say(embed=olembed(0xff0000,"!","You cannot add this map to the pool yet. Please make sure that your chosen map fulfills all the following requirements:\r\n- It's one of your last 50 songs played.\r\n- You passed it in the past 24 hours.\r\n- You passed No Mod, or with HR, HD, DT or FL.\r\n- You achieved over 88% accuracy."))
		mysql_conn.close()
		await bot.delete_message(ctx.message)
	except Exception as e:
		log("[addmap] Error: "+str(e))
 
@bot.command(pass_context=True)
async def scores(ctx,bracket:str="!"):
	"""Show the Map of the Week leaderboards for your bracket!"""
	get_date = int(time.strftime("%d"))
	get_time = int(time.strftime("%H"))
	if get_date == 29 or get_date == 30 or (get_date == 31 and not get_time == 23):
		await bot.say(embed=olembed(0xffff00,"!","The MotW for the last month is now finished! A new round starts on the 1st!"))
	else:
		if bracket == "!":
			v_channel = getChannel(ctx)
		elif bracket.upper() in ["WH","NW","BA","EZ","NM","HD","IN","EX"]:
			v_channel = bracket.upper()
		else:
			v_channel = getChannel(ctx)
		c_wel = bot.get_channel("")
		v_scores = getScores(v_channel)
		if v_channel == "ERROR":
			if bracket != "!":
				await bot.say(embed=olembed(0xff0000,"!","You entered an invalid bracket. Please try one of the following: WH,NW,BA,EZ,NM,HD,IN,EX,TON,TMU,TFU,TKA,MMX,MHD,MNM,MEZ,CRA,CPL,CSA,CCU"))
			else:
				await bot.say(embed=olembed(0xff0000,"!","You cannot see the scores for a bracket from this channel. Please read {0.mention} to get started!".format(c_wel)))
		else:
			mysql_conn = await aiomysql.connect(host = mysql_host, port=3306, user=mysql_user,password=mysql_pass, db = mysql_data)
			mysql_curs = await mysql_conn.cursor()
			await mysql_curs.execute("SELECT map_id,date_range_tstmp,mode FROM beatmaps WHERE bracket = '"+v_channel+"'")
			get_map = await mysql_curs.fetchone()
			await mysql_curs.execute("SELECT COUNT(*) AS COUN FROM "+ v_scores +" where map_id = "+str(get_map[0]))
			get_cou = await mysql_curs.fetchone()
			await mysql_curs.execute("SELECT * FROM "+ v_scores +" where map_id = "+str(get_map[0])+" and not rank = 'F' order by score desc LIMIT 0,10")
			result = await mysql_curs.fetchall()
			count = 1
			ostring = "**Current Top 10 Leaderboard for Map of the Week ("+v_channel+" Bracket)**\r\n\r\n"
			if bracket != "!":
				async with aiohttp.ClientSession() as cs:
					url = osu_api + "get_beatmaps?k=" + osu_key + "&b=" + str(get_map[0]) + "&m=" + str(get_map[2]) + "&limit=1"
					async with cs.get(url) as s:
						ses = await s.json()
						song_artis = ses[0]['artist']
						song_title = ses[0]['title']
						song_diffi = ses[0]['version']
						song_mappe = ses[0]['creator']
						ostring = ostring + "The " + bracket.upper() + " bracket are playing " + song_title + " - " + song_artis + " (" + song_diffi + ") by "+song_mappe+"\r\n\r\n"
						
			for row in result:
				p_name = row[2]
				p_id = row[3]
				p_mc = row[4]
				if p_mc is None:
					p_mc = 0
				p_score = row[5]
				p_rank = row[6]
				p_acc = row[7]
				p_mods = row[8]
				ostring = ostring + "{1} \t- [{2}](http://osu.ppy.sh/u/{3}) - {4:,} - {5} - {8} Combo - {6}% {7}\r\n\r\n".format(count,Ordinal(count),p_name,p_id,p_score,osu_ranks[p_rank],p_acc,p_mods,p_mc)
				count = count + 1
			embed = discord.Embed(colour=discord.Colour(0x6600FF), description=ostring, timestamp=get_map[1])
			embed.set_footer(text="This round ends")
			await bot.say(embed=embed)
			mysql_conn.close()
	await bot.delete_message(ctx.message)

@bot.command(pass_context=True, aliases=['mappool'])
async def pool(ctx,page : int=1):
	"""Shows you what beatmaps are in the pool up for selection!"""
	try:
		v_channel = getChannel(ctx)
		v_roll = getRole(v_channel)
		v_scores = getScores(v_channel)
		c_wel = bot.get_channel("")
		await bot.delete_message(ctx.message)
		v_id = ctx.message.author.id
		if v_channel == "ERROR":
			await bot.say(embed=olembed(0xff0000,"!","You cannot see a bracket's pool from this channel. Please read {0.mention} to get started!".format(c_wel)))
		else:
			mysql_conn = await aiomysql.connect(host = mysql_host, port=3306, user=mysql_user,password=mysql_pass, db = mysql_data)
			mysql_curs = await mysql_conn.cursor()
			await mysql_curs.execute("SELECT count(*) as COUN FROM "+ v_roll)
			v_count = await mysql_curs.fetchone()
			v_strin = "**Map Pool for Next Week's " + v_channel + " Bracket**\r\nOne of these maps will be picked for next weeks round.\r\nType ``+addmap beatmapid`` to add a map to the pool.\r\n\r\n"
			v_strin += "Page: "+str(page) + " (Do ``+pool <number>`` to check other pages).\r\n\r\n"
			fromp = 0 + (page*10)-10
			hasmap=0
			for k in range(fromp,fromp+10):
				await mysql_curs.execute("SELECT * FROM "+ v_roll + " ORDER BY DIWOR ASC LIMIT "+str(k)+",1")
				v_map = await mysql_curs.fetchone()
				if v_map:
					hasmap=1
					await mysql_curs.execute("SELECT PLAYER_NAME from linked_players where DISCORD_ID = "+str(v_map[1])+"")
					v_player = await mysql_curs.fetchone()
					if v_player:
						v_strin = v_strin + "[{0} - {1}](http://osu.ppy.sh/b/{2}) ({3}) by {4} - picked by {5}\r\n".format(v_map[3],v_map[4],v_map[2],v_map[5],v_map[6],v_player[0])
					else:
						v_strin = v_strin + "[{0} - {1}](http://osu.ppy.sh/b/{2}) ({3}) by {4} - picked by ?\r\n".format(v_map[3],v_map[4],v_map[2],v_map[5],v_map[6])
				if hasmap==0:
					v_strin = "There are no more maps to display."
			embed = discord.Embed(colour=discord.Colour(0x0066FF), description=v_strin)
			embed.set_footer(text=str(ctx.message.author.name) + " ran this command.")
			await bot.say(embed=embed)
		
	except Exception as e:
		log("[pool] Error "+str(e))

@bot.command(pass_context=True)
async def alltime(ctx):
	try:
		mysql_conn = await aiomysql.connect(host = mysql_host, port=3306, user=mysql_user,password=mysql_pass, db = mysql_data)
		mysql_curs = await mysql_conn.cursor()
		await mysql_curs.execute("SELECT PLAYER_NAME,PLAYER_ID,RANK,BRACKET,SCORE_ALLTIME FROM linked_players where LINKED = 1 ORDER BY SCORE_ALLTIME desc LIMIT 0,10")
		v_result = await mysql_curs.fetchall()
		ostring = "**Current Top 10 All Time Leaderboard across all brackets**\r\n\r\n"
		count=1
		for row in v_result:
			ostring = ostring + "{1} \t- [{2}](http://osu.ppy.sh/u/{3}) - #{4:,} ({5} Bracket) - {6} points!\r\n\r\n".format(count,Ordinal(count),str(row[0]),str(row[1]),int(row[2]),str(row[3]),str(int(row[4])))
			count = count + 1
		embed = discord.Embed(colour=discord.Colour(0x6600FF), description=ostring)
		embed.set_footer(text="Congratulations!")
		await bot.say(embed=embed)
		mysql_conn.close()
		await bot.delete_message(ctx.message)
	except Exception as e:
		log("[alltime] Error: " + str(e))
		

@bot.command(pass_context=True)
async def submit(ctx):
	"""Submit your score for Map of the Week!"""
	get_date = int(time.strftime("%d"))
	get_time = int(time.strftime("%H"))
	if get_date == 29 or get_date == 30 or (get_date == 31 and not get_time == 23):
		await bot.say(embed=olembed(0xff0000,"!","The MotW for the last month is now finished! A new round starts on the 1st!"))
	else:
		try:
			v_channel = getChannel(ctx)
			c_wel = bot.get_channel("316841596228468736")
			v_scores = getScores(v_channel)
			v_id = ctx.message.author.id
			pre_embed = discord.Embed(colour=discord.Colour(0x00FF00), description="Submitting Score... Please wait...")
			msg = await bot.send_message(ctx.message.channel,embed=pre_embed)
			if v_channel == "ERROR" or v_scores == "ERROR":
				await bot.edit_message(msg,embed=discord.Embed(colour=discord.Colour(0xFF0000), description="You cannot submit a score for a bracket from this channel. Please read {0.mention} to get started!".format(c_wel)))
			else:
				try:
					mysql_conn = await aiomysql.connect(host = mysql_host, port=3306, user=mysql_user,password=mysql_pass, db = mysql_data)
					mysql_curs = await mysql_conn.cursor()
					await mysql_curs.execute("SELECT PLAYER_NAME,LINKED FROM linked_players where DISCORD_ID = '"+str(v_id)+"'")
					v_result = await mysql_curs.fetchone()
					if v_result[1]==0:
						await bot.edit_message(msg,embed=discord.Embed(colour=discord.Colour(0xFF0000), description="Your account is not linked properly. Please contact Staff or TheMeq."))
					else:
						async with aiohttp.ClientSession() as cs:
							url = osu_api + "get_user?k=" + osu_key + "&u=" + v_result[0].replace(" ","+") + "&m=0"
							async with cs.get(url) as r:
								res = await r.json()
								log("1: PASS")
								r_player = res[0]['username']
								r_playerid = res[0]['user_id']
								r_rank = res[0]['pp_rank']
								r_timestamp = int(time.time())
								if v_channel in ["WH","NW","BA","EZ","NM","HD","IN","EX"]:
									url = osu_api + "get_user_recent?k=" + osu_key + "&u=" + v_result[0].replace(" ","+") + "&m=0&limit=1"
									game_mode_value = 0
								if v_channel in ["TON","TMU","TFU","TKA"]:
									url = osu_api + "get_user_recent?k=" + osu_key + "&u=" + v_result[0].replace(" ","+") + "&m=1&limit=1"
									game_mode_value = 1
								if v_channel in ["MMX","MHD","MNM","MEZ"]:
									url = osu_api + "get_user_recent?k=" + osu_key + "&u=" + v_result[0].replace(" ","+") + "&m=3&limit=1"
									game_mode_value = 3
								if v_channel in ["CRA","CPL","CSA","CCU"]:
									url = osu_api + "get_user_recent?k=" + osu_key + "&u=" + v_result[0].replace(" ","+") + "&m=2&limit=1"
									game_mode_value = 2
								async with cs.get(url) as g:
									gur = await g.json()
									if gur:
										log("2: PASS")
										lastplay_beatmap = gur[0]['beatmap_id']
										lastplay_score = int(gur[0]['score'])
										lastplay_maxco = gur[0]['maxcombo']
										lastplay_fifty = gur[0]['count50']
										lastplay_hundr = gur[0]['count100']
										lastplay_three = gur[0]['count300']
										lastplay_misse = gur[0]['countmiss']
										lastplay_katu = gur[0]['countkatu']
										lastplay_geki = gur[0]['countgeki']
										lastplay_ranks = gur[0]['rank']
										lastplay_modif = gur[0]['enabled_mods']
										lastplay_accur = round(((((int(lastplay_three) * 300) + (int(lastplay_hundr) * 100) + (int(lastplay_fifty) * 50) + (int(lastplay_misse) * 0)) / ((int(lastplay_three) + int(lastplay_hundr) + int(lastplay_fifty) + int(lastplay_misse)) * 300)) * 100),2)
										if game_mode_value == 2:
											lastplay_accur = round((((int(lastplay_three)) + (int(lastplay_hundr)) + (int(lastplay_fifty)))/((int(lastplay_three)) + (int(lastplay_hundr)) + (int(lastplay_fifty)) + (int(lastplay_misse)) + (int(lastplay_katu)))) * 100,2)
										if game_mode_value == 3:
											lastplay_accur = round((((int(lastplay_fifty) * 50) + (int(lastplay_hundr) * 100) + (int(lastplay_katu) * 200) + (int(lastplay_geki) * 300) + (int(lastplay_three) * 300)) / ((int(lastplay_fifty)+int(lastplay_hundr)+int(lastplay_katu)+int(lastplay_geki)+int(lastplay_three)+int(lastplay_misse)) * 300) * 100) ,2)
										if lastplay_modif != "" or lastplay_modif != "0" or lastplay_modif !=0:
											used_mods = GetMods(lastplay_modif)
										if used_mods:
											gm = ""
											for mods in used_mods:
												gm = gm + osu_mods_t[str(mods)] + ""
										else:
											gm = ""
										await mysql_curs.execute("SELECT map_id FROM beatmaps WHERE bracket = '"+v_channel+"'")
										get_map = await mysql_curs.fetchone()
										log("3: PASS")
										async with aiohttp.ClientSession() as cs:
											url = osu_api + "get_beatmaps?k=" + osu_key + "&b=" + str(get_map[0]) + "&m=" + str(game_mode_value)
											async with cs.get(url) as b:
												bur = await b.json()
												if bur: 
													song_name = bur[0]['title']
													song_artist = bur[0]['artist']
													song_mapper = bur[0]['creator']
													song_version = bur[0]['version']
													if str(get_map[0]) == str(lastplay_beatmap):
														await mysql_curs.execute("SELECT * FROM "+v_scores+" WHERE player_id = "+str(r_playerid)+" and map_id = "+str(lastplay_beatmap))
														get_sco = await mysql_curs.fetchone()
														v_server = bot.get_server(main_server)
														the_global_channel = discord.utils.get(v_server.channels, name="global-scores", type=discord.ChannelType.text) 
														log("4: PASS")
														if not get_sco:
															log("5: PASS")
															r_timestamp = int(time.time())
															await mysql_curs.execute("INSERT INTO " + v_scores + " (map_id,player_name,player_id,max_combo,score,rank,accuracy,mods,ach_date) VALUES ('" + str(lastplay_beatmap) + "','" + r_player + "','" + str(r_playerid) + "','"+str(lastplay_maxco)+"','" + str(lastplay_score) + "','" + lastplay_ranks + "','" + str(lastplay_accur) + "','" + gm + "','" + str(r_timestamp) + "')")
															await mysql_conn.commit()
															if lastplay_ranks != "F":
																embed = discord.Embed(colour=discord.Colour(0x00FF00), description="[{0}](http://osu.ppy.sh/u/{4}) (#{5:,}) just got a score of {1:,} and a rank of {2} with {3}% accuracy!".format(r_player,lastplay_score,osu_ranks[lastplay_ranks],lastplay_accur,r_playerid,int(r_rank)))
																embed.set_author(name=r_player, icon_url="https://a.ppy.sh/" + r_playerid + "_" + str(r_timestamp) + ".png")
																embed.set_footer(text=str(ctx.message.author.name) + " ran this command.")
																await bot.edit_message(msg,embed=embed)
																embed = discord.Embed(colour=discord.Colour(0x00FF00), description="[{0}](http://osu.ppy.sh/u/{4}) (#{5:,}) just got a score of {1:,} and a rank of {2} with {3}% accuracy on [{7} - {6} ({8})](http://osu.ppy.sh/b/{11}) by {9} in the {10} bracket!".format(r_player,lastplay_score,osu_ranks[lastplay_ranks],lastplay_accur,r_playerid,int(r_rank),song_name,song_artist,song_version,song_mapper,v_channel,str(get_map[0])))
																embed.set_author(name=r_player, icon_url="https://a.ppy.sh/" + r_playerid + "_" + str(r_timestamp) + ".png")
																await bot.send_message(the_global_channel,embed=embed)
																await mysql_curs.execute("UPDATE linked_players SET HAS_SUBMITTED = 1 WHERE PLAYER_ID = '" + str(r_playerid) + "'")
																await mysql_conn.commit()
															else:
																await bot.edit_message(msg,embed=discord.Embed(colour=discord.Colour(0x00FF00), description="Your last score on this map was a fail and wasn't recorded. Try again!"))
														else:
															log("6: PASS")
															if lastplay_score >= int(get_sco[5]):
																r_timestamp = int(time.time())
																await mysql_curs.execute("UPDATE "+v_scores+" SET max_combo='"+str(lastplay_maxco)+"',score='"+str(lastplay_score)+"',rank='"+lastplay_ranks+"',accuracy='"+str(lastplay_accur)+"',mods='"+gm+"',ach_date='"+str(r_timestamp)+"' WHERE player_id = "+str(r_playerid)+" and map_id = "+str(lastplay_beatmap))
																await mysql_conn.commit()
																log("7: PASS")
																if lastplay_ranks != "F":
																	embed = discord.Embed(colour=discord.Colour(0x00FF00), description="[{0}](http://osu.ppy.sh/u/{4}) (#{5:,}) just got a better score of {1:,} and a rank of {2} with {3}% accuracy!".format(r_player,lastplay_score,osu_ranks[lastplay_ranks],lastplay_accur,r_playerid,int(r_rank)))
																	embed.set_author(name=r_player, icon_url="https://a.ppy.sh/" + r_playerid + "_" + str(r_timestamp) + ".png")
																	embed.set_footer(text=str(ctx.message.author.name) + " ran this command.")
																	await bot.edit_message(msg,embed=embed)
																	embed = discord.Embed(colour=discord.Colour(0x00FF00), description="[{0}](http://osu.ppy.sh/u/{4}) (#{5:,}) just got a better score of {1:,} and a rank of {2} with {3}% accuracy on [{7} - {6} ({8})](http://osu.ppy.sh/b/{11}) by {9} in the {10} bracket!".format(r_player,lastplay_score,osu_ranks[lastplay_ranks],lastplay_accur,r_playerid,int(r_rank),song_name,song_artist,song_version,song_mapper,v_channel,str(get_map[0])))
																	embed.set_author(name=r_player, icon_url="https://a.ppy.sh/" + r_playerid + "_" + str(r_timestamp) + ".png")
																	await bot.send_message(the_global_channel,embed=embed)
																	await mysql_curs.execute("UPDATE linked_players SET HAS_SUBMITTED = 1 WHERE PLAYER_ID = '" + str(r_playerid) + "'")
																	await mysql_conn.commit()
																else:
																	embed = discord.Embed(colour=discord.Colour(0x00FF00), description="Your last score on this map was a fail and wasn't recorded. Try again!")
																	embed.set_author(name=r_player, icon_url="https://a.ppy.sh/" + r_playerid + "_" + str(r_timestamp) + ".png")
																	embed.set_footer(text=str(ctx.message.author.name) + " ran this command.")
																	await bot.edit_message(msg,embed=embed)
																	
															else:
																embed = discord.Embed(colour=discord.Colour(0x00FF00), description="Your latest score doesn't surpass the score you've already submitted on this Map of the Week.")
																embed.set_author(name=r_player, icon_url="https://a.ppy.sh/" + r_playerid + "_" + str(r_timestamp) + ".png")
																embed.set_footer(text=str(ctx.message.author.name) + " ran this command.")
																await bot.edit_message(msg,embed=embed)
													else:
														embed = discord.Embed(colour=discord.Colour(0x00FF00), description="Your latest play does not match the Map of the Week for this bracket. Please check the Map of the Week with ``+motw``")
														embed.set_author(name=r_player, icon_url="https://a.ppy.sh/" + r_playerid + "_" + str(r_timestamp) + ".png")
														embed.set_footer(text=str(ctx.message.author.name) + " ran this command.")
														await bot.edit_message(msg,embed=embed)
									else:
										embed = discord.Embed(colour=discord.Colour(0x00FF00), description="Your latest play does not match the Map of the Week for this bracket. Please check the Map of the Week with ``+motw``")
										embed.set_author(name=r_player, icon_url="https://a.ppy.sh/" + r_playerid + "_" + str(r_timestamp) + ".png")
										embed.set_footer(text=str(ctx.message.author.name) + " ran this command.")
										await bot.edit_message(msg,embed=embed)
												
								mysql_conn.close()
				except Exception as e:
					log('[submit] Error: '+ str(e))
					await bot.edit_message(msg,embed=olembed(0xff0000,"!","An error occured, please try again in a minute."))
		except Exception as e:
			log('[submit] Error: '+ str(e))
			await bot.edit_message(msg,embed=olembed(0xff0000,"!","An error occured, please try again in a minute."))
	await bot.delete_message(ctx.message)

@bot.command(pass_context=True)
async def players(ctx):
	'''Show how many people have entered the Map of the Week Tourney'''
	mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
	mysql_curs = await mysql_conn.cursor()
	mysql_quer = "SELECT COUNT(*) AS COUN from linked_players WHERE RANK > 0 and RANK <= 2000 and LINKED = 1"
	await mysql_curs.execute(mysql_quer)
	v_result = await mysql_curs.fetchone()
	v_ex = v_result[0]
	mysql_quer = "SELECT COUNT(*) AS COUN from linked_players WHERE RANK > 2000 and RANK <= 5000 and LINKED = 1"
	await mysql_curs.execute(mysql_quer)
	v_result = await mysql_curs.fetchone()
	v_in = v_result[0]
	mysql_quer = "SELECT COUNT(*) AS COUN from linked_players WHERE RANK > 5000 and RANK <= 10000 and LINKED = 1"
	await mysql_curs.execute(mysql_quer)
	v_result = await mysql_curs.fetchone()
	v_hd = v_result[0]
	mysql_quer = "SELECT COUNT(*) AS COUN from linked_players WHERE RANK > 10000 and RANK <= 25000 and LINKED = 1"
	await mysql_curs.execute(mysql_quer)
	v_result = await mysql_curs.fetchone()
	v_nm = v_result[0]
	mysql_quer = "SELECT COUNT(*) AS COUN from linked_players WHERE RANK > 25000 and RANK <= 50000 and LINKED = 1"
	await mysql_curs.execute(mysql_quer)
	v_result = await mysql_curs.fetchone()
	v_ez = v_result[0]
	mysql_quer = "SELECT COUNT(*) AS COUN from linked_players WHERE RANK > 50000 and RANK <= 100000 and LINKED = 1"
	await mysql_curs.execute(mysql_quer)
	v_result = await mysql_curs.fetchone()
	v_ba = v_result[0]
	mysql_quer = "SELECT COUNT(*) AS COUN from linked_players WHERE RANK > 100000 and RANK <= 200000 and LINKED = 1"
	await mysql_curs.execute(mysql_quer)
	v_result = await mysql_curs.fetchone()
	v_nw = v_result[0]
	mysql_quer = "SELECT COUNT(*) AS COUN from linked_players WHERE RANK > 200000 and RANK <= 1000000 and LINKED = 1"
	await mysql_curs.execute(mysql_quer)
	v_result = await mysql_curs.fetchone()
	v_wh = v_result[0]
	mysql_quer = "SELECT COUNT(*) AS COUN from linked_players WHERE LINKED = 0"
	await mysql_curs.execute(mysql_quer)
	v_result = await mysql_curs.fetchone()
	v_ul = v_result[0]
	v_all = v_ex+v_in+v_hd+v_nm+v_ez+v_ba+v_nw+v_wh
	g_string = "**Player Count in the Map of the Week**\r\n\r\nTotal Participants: {4} players!\r\n\r\nExpert Group (EX): {0} players\r\nInsane Group (IN): {1} players\r\nHard Group (HD): {2} players\r\nNormal Group (NM): {3} players\r\n".format(str(v_ex),str(v_in),str(v_hd),str(v_nm),str(v_all))
	g_string = g_string + "Easy Group (EZ): {0} players\r\nBasic Group (BA): {1} players\r\nNewbie Group (NW): {2} players\r\nWho? Group (WH): {3} players\r\n\r\n{4} players haven't linked yet!".format(str(v_ez),str(v_ba),str(v_nw),str(v_wh),str(v_ul))
	pla_embed = discord.Embed(colour=discord.Colour(0xFF00FF), description=g_string)
	pla_embed.set_footer(text=str(ctx.message.author.name) + " ran this command.")
	await bot.send_message(ctx.message.channel,embed=pla_embed)
	await bot.delete_message(ctx.message)

@bot.command(pass_context=True)
@commands.has_permissions(manage_channels=True)
async def removemap(ctx, map_id: int=1, *, reason: str="!"):
	await bot.delete_message(ctx.message)
	v_channel = getChannel(ctx)
	v_roll = getRole(v_channel)
	if reason == "!": 
		reason = "No Reason Provided."
	if v_channel == "ERROR":
		await bot.send_message(ctx.message.channel,embed=discord.Embed(colour=discord.Colour(0xFF0000), description="You cannot delete maps from this channel."))
	else:
		try:
			mysql_conn = await aiomysql.connect(host = mysql_host, port=3306, user=mysql_user,password=mysql_pass, db = mysql_data)
			mysql_curs = await mysql_conn.cursor()
			mysql_quer = "SELECT * FROM "+v_roll+" WHERE BeatmapID = "+str(map_id)
			await mysql_curs.execute(mysql_quer)
			v_result = await mysql_curs.fetchone()
			await bot.say(embed=olembed(0xffff00,"!","A Map has been removed from the pool.\r\n\r\nReason: "+reason+"\r\n\r\nMap Removed: "+v_result[4]+" - "+v_result[3]+" ("+v_result[5]+" by "+v_result[6]+")"))
			mysql_quer = "DELETE FROM "+v_roll+" WHERE BeatmapID = "+str(map_id)
			await mysql_curs.execute(mysql_quer)
			await mysql_conn.commit()
		except Exception as e:
			log("ERROR: "+str(e))

@bot.command(pass_context=True)
@commands.has_permissions(manage_channels=True)
async def updatenicks(ctx):
	await bot.delete_message(ctx.message)
	mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
	mysql_curs = await mysql_conn.cursor()
	mysql_quer = "SELECT COUNT(*) AS COUN from linked_players WHERE LINKED = 1"
	await mysql_curs.execute(mysql_quer)
	v_count = await mysql_curs.fetchone()
	mysql_quer = "SELECT PLAYER_NAME,DISCORD_ID FROM linked_players WHERE LINKED = 1"
	await mysql_curs.execute(mysql_quer)
	v_result = await mysql_curs.fetchall()
	cur = 0
	v_server = bot.get_server(main_server)
	for v_row in v_result:
		cur=cur+1
		try:
			await bot.change_nickname(v_server.get_member(v_row[1]),str(v_row[0]))
			log("Updated DiscordID " + str(v_row[1]) + " to use Nickname "+ str(v_row[0]))
			v_logchannel = bot.get_channel(channel_botlog)
			await bot.send_message(v_logchannel,"Updated DiscordID " + str(v_row[1]) + " to use Nickname "+ str(v_row[0]))
		except Exception as e:
			log("Couldn't update the Nickname for " + str(v_row[0]))
			v_logchannel = bot.get_channel(channel_botlog)
			await bot.send_message(v_logchannel,"Couldn't update the Nickname for " + str(v_row[0]))
			log("[updatenicks] Error: "+str(e))
			

@bot.command(pass_context=True)
async def namechange(ctx):
	
	await bot.delete_message(ctx.message)
	v_server = bot.get_server(main_server)
	try:
		mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
		mysql_curs = await mysql_conn.cursor()
		mysql_quer = "SELECT PLAYER_ID,DISCORD_ID FROM linked_players WHERE DISCORD_ID = '" + str(ctx.message.author.id) + "' and linked = 1"
		await mysql_curs.execute(mysql_quer)
		v_result = await mysql_curs.fetchone()
		async with aiohttp.ClientSession() as cs:
			url = osu_api + "get_user?k=" + osu_key + "&u=" + v_result[0].replace(" ","+") + "&m=0"
			async with cs.get(url) as r:
				res = await r.json()
				if res:
					n_name = res[0]['username']
					await bot.change_nickname(v_server.get_member(v_result[1]),str(n_name))
					mysql_quer = "UPDATE linked_players SET PLAYER_NAME = '" + str(n_name) + "' WHERE DISCORD_ID = '" + str(v_result[1]) + "'"
					await mysql_curs.execute(mysql_quer)
					await mysql_conn.commit()
					log("Updated DiscordID " + str(v_result[1]) + " to use Nickname "+ str(n_name))
					prevwin_embed = discord.Embed(colour=discord.Colour(0x00FF00), description="Your nickname has been updated!")
					await bot.say(embed=prevwin_embed)
				else:
					log("Couldn't update the Nickname for " + str(v_result[1]))
					prevwin_embed = discord.Embed(colour=discord.Colour(0xFF0000), description="Couldn't update your nickname right now.")
					await bot.say(embed=prevwin_embed)
					log("[updatenicks] Error: "+str(e))
	except Exception as e:
		log("[namechange] Error: "+str(e)+"")

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def raffleall(ctx):
	channel = ctx.message.channel
	member = random.choice(list(ctx.message.server.members))
	fmt = ':tada: Congratulations {0.mention}! A month of supporter has been dropped and you\'ve won it! Wew! :tada: '
	await bot.send_message(channel, fmt.format(member))
	await bot.delete_message(ctx.message)
		

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def raffle(ctx):
	f=0
	channel = ctx.message.channel
	while f==0:
		member = random.choice(list(ctx.message.server.members))
		mysql_conn = await aiomysql.connect(host = mysql_host, port=3306, user=mysql_user,password=mysql_pass, db = mysql_data)
		mysql_curs = await mysql_conn.cursor()
		mysql_quer = "SELECT COUNT(*) AS RESULT FROM linked_players WHERE DISCORD_ID = '"+member.id+"' and LINKED=1 and HAS_SUBMITTED=1"
		log(mysql_quer)
		await mysql_curs.execute(mysql_quer)
		v_result = await mysql_curs.fetchone()
		if v_result[0]==1:
			f=1
			fmt = ':tada: Congratulations {0.mention}! A month of supporter has been dropped and you\'ve won it! Wew! :tada: '
			await bot.send_message(channel, fmt.format(member))
	await bot.delete_message(ctx.message)

@bot.command(pass_context=True)
@commands.has_permissions(manage_channels=True)
async def updateranks(ctx):
	'''Runs the rank update function. Run at start and end of MotW.'''
	await bot.delete_message(ctx.message)
	mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
	mysql_curs = await mysql_conn.cursor()
	mysql_quer = "SELECT COUNT(*) AS COUN from linked_players WHERE LINKED = 1"
	await mysql_curs.execute(mysql_quer)
	v_count = await mysql_curs.fetchone()
	mysql_quer = "SELECT PLAYER_ID,PLAYER_NAME,DISCORD_ID,LINKED,BRACKET,TAIKO_BRACKET,CTB_BRACKET,MANIA_BRACKET FROM linked_players WHERE LINKED = 1"
	await mysql_curs.execute(mysql_quer)
	v_result = await mysql_curs.fetchall()
	std_bracket = "XX"
	tai_bracket = "TKA"
	ctb_bracket = "CCU"
	man_bracket = "MEZ"
	v_server = bot.get_server(main_server)
	async with aiohttp.ClientSession() as cs:
		for v_row in v_result:
			i_playerid = v_row[0]
			i_playername = v_row[1]
			v_id = str(v_row[2])
			i_linked = v_row[3]
			cur_std_bracket = v_row[4]
			std_cbracket = v_row[4]
			tai_cbracket = v_row[5]
			man_cbracket = v_row[6]
			ctb_cbracket = v_row[7]
			try:
				o_url = osu_api + "get_user?k=" + osu_key + "&u=" + i_playerid + "&m=0"
				async with cs.get(o_url) as g:
					gur = await g.json()
					if gur:
						n_name = gur[0]['username']
						s_rank = gur[0]['pp_rank']
						if s_rank is None:
							s_rank = "0"
						if int(s_rank) >= 1 and int(s_rank) <= 2000:
							std_bracket = "EX"
						elif int(s_rank) > 2000 and int(s_rank) <= 5000:
							std_bracket = "IN"
						elif int(s_rank) > 5000 and int(s_rank) <= 10000:
							std_bracket = "HD"
						elif int(s_rank) > 10000 and int(s_rank) <= 25000:
							std_bracket = "NM"
						elif int(s_rank) > 25000 and int(s_rank) <= 50000:
							std_bracket = "EZ"
						elif int(s_rank) > 50000 and int(s_rank) <= 100000:
							std_bracket = "BA"
						elif int(s_rank) > 100000 and int(s_rank) <= 200000:
							std_bracket = "NW"
						elif int(s_rank) > 200000 and int(s_rank) <= 1000000:
							std_bracket = "WH"
						else:
							std_bracket = "XX"
					else:
						log(i_playername + " [Standard] check didn't return anything from osu!api, please try again manually.")
						std_bracket = "XX"
			except Exception as e:
				log("[rankupdate>std] Error: " + str(e))
			try:
				o_url = osu_api + "get_user?k=" + osu_key + "&u=" + i_playerid + "&m=1"
				async with cs.get(o_url) as g:
					gur = await g.json()
					if gur:
						n_name = gur[0]['username']
						t_rank = gur[0]['pp_rank']
						if t_rank is None:
							t_rank = "0"
						if int(t_rank) >= 1 and int(t_rank) <= 1000:
							tai_bracket = "TON"
						elif int(t_rank) > 1000 and int(t_rank) <= 2500:
							tai_bracket = "TMU"
						elif int(t_rank) > 2500 and int(t_rank) <= 5000:
							tai_bracket = "TFU"
						else:
							tai_bracket = "TKA"
					else:
						log(i_playername + " [Taiko] check didn't return anything from osu!api, please try again manually.")
						tai_bracket = "TKA"
			except Exception as e:
				log("[rankupdate>tai]  Error: " + str(e))
			try:
				o_url = osu_api + "get_user?k=" + osu_key + "&u=" + i_playerid + "&m=2"
				async with cs.get(o_url) as g:
					gur = await g.json()
					if gur:
						n_name = gur[0]['username']
						c_rank = gur[0]['pp_rank']
						if c_rank is None:
							c_rank = "0"
						if int(c_rank) >= 1 and int(c_rank) <= 1000:
							ctb_bracket = "CRA"
						elif int(c_rank) > 1000 and int(c_rank) <= 2500:
							ctb_bracket = "CPL"
						elif int(c_rank) > 2500 and int(c_rank) <= 5000:
							ctb_bracket = "CSA"
						else:
							ctb_bracket = "CCU"
					else:
						log(i_playername + " [CTB] check didn't return anything from osu!api, please try again manually.")
						ctb_bracket = "CCU"
			except Exception as e:
				log("[rankupdate>ctb] Error: " + str(e))
			try:
				o_url = osu_api + "get_user?k=" + osu_key + "&u=" + i_playerid + "&m=3"
				async with cs.get(o_url) as g:
					gur = await g.json()
					if gur:
						n_name = gur[0]['username']
						m_rank = gur[0]['pp_rank']
						if m_rank is None:
							m_rank = "0"
						if int(m_rank) >= 1 and int(m_rank) <= 4000:
							man_bracket = "MMX"
						elif int(m_rank) > 4000 and int(m_rank) <= 10000:
							man_bracket = "MHD"
						elif int(m_rank) > 10000 and int(m_rank) <= 30000:
							man_bracket = "MNM"
						else:
							man_bracket = "MEZ"
					else:
						log(i_playername + " [Mania] check didn't return anything from osu!api, please try again manually.")
						man_bracket = "MEZ"
			except Exception as e:
				log("[rankupdate>man] Error: " + str(e))
			try:
				v_logchannel = bot.get_channel(channel_botlog)
				await bot.send_message(v_logchannel,i_playername + " ranks detected as: STD: " + str(s_rank) + ", TAI: "+ str(t_rank) + ", CTB: " + str(c_rank) + ", MAN: "+str(m_rank))
				log(i_playername + " ranks detected as: STD: " + str(s_rank) + ", TAI: "+ str(t_rank) + ", CTB: " + str(c_rank) + ", MAN: "+str(m_rank))
				await bot.send_message(v_logchannel,i_playername + " is going into " + std_bracket + "," + tai_bracket +","+ ctb_bracket+ ","+ man_bracket)
				log(i_playername + " is going into " + std_bracket + "," + tai_bracket +","+ ctb_bracket+ ","+ man_bracket)
				if i_linked==1:
					try: 
						std_role = discord.utils.get(v_server.roles, name=osu_roles[std_bracket])
						tai_role = discord.utils.get(v_server.roles, name=osu_roles[tai_bracket])
						ctb_role = discord.utils.get(v_server.roles, name=osu_roles[ctb_bracket])
						man_role = discord.utils.get(v_server.roles, name=osu_roles[man_bracket])
						await bot.replace_roles(v_server.get_member(v_id),std_role,tai_role,ctb_role,man_role)
					except Exception as e: 
						v_logchannel = bot.get_channel(channel_botlog)
						await bot.send_message(v_logchannel,"" + str(i_playername) + " couldn't be updated, they are either staff, or they left the tourney.")
			except Exception as e: 
				log("Couldn't change roles for " + i_playername)
				log("[rankupdate>roles] Error: " +str(e))
			time_string = str(time.time())
			mysql_quer = "UPDATE linked_players SET PLAYER_NAME='"+ n_name +"',LAST_CHECKED='"+ time_string + "',RANK = "+str(s_rank)+",BRACKET='"+std_bracket+"',TAIKO_RANK = "+str(t_rank)+",TAIKO_BRACKET='"+tai_bracket+"',CTB_RANK ="+str(c_rank)+",CTB_BRACKET='"+ctb_bracket+"',MANIA_RANK = "+str(m_rank)+",MANIA_BRACKET='"+man_bracket+"' WHERE PLAYER_ID = "+str(i_playerid)+""
			await mysql_curs.execute(mysql_quer)
			await mysql_conn.commit()
			v_logchannel = bot.get_channel(channel_botlog)
			await bot.send_message(v_logchannel,i_playername + " has had their ranks and brackets changed.") 
			log(i_playername + " has had their ranks and brackets changed.")
			if cur_std_bracket != std_bracket:
				v_channel = bot.get_channel("316842433260421130")
				await bot.send_message(v_channel,"" + str(i_playername) + " is moving to the " + str(std_bracket) + " bracket!")
			await asyncio.sleep(2)
	mysql_conn.close()
	log("Done!")

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def restartbot(ctx):
	await bot.delete_message(ctx.message)
	safe_shutdown = open("osu_motw_safeshutdown.txt", "w")
	safe_shutdown.write("1")
	safe_shutdown.close()
	exit()

@bot.command(pass_context=True)
@commands.has_permissions(manage_channels=True)
async def clearscores(ctx):
	v_channel = getChannel(ctx)
	v_roll = getRole(v_channel)
	v_scores = getScores(v_channel)
	mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
	mysql_curs = await mysql_conn.cursor()
	mysql_quer = "DELETE FROM " + v_scores
	await mysql_curs.execute(mysql_quer)
	await mysql_conn.commit()
	mysql_quer = "UPDATE linked_players SET SCORE_MONTH=0"
	await mysql_curs.execute(mysql_quer)
	await mysql_conn.commit()
	mysql_conn.close()
	await bot.delete_message(ctx.message)
	
@bot.command(pass_context=True)
@commands.has_permissions(manage_channels=True)
async def updatescores(ctx):
	try: 
		v_channel = getChannel(ctx)
		v_roll = getRole(v_channel)
		v_scores = getScores(v_channel)
		bstring = "Winner's of the last MotW was:\r\n\r\n"
		mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
		mysql_curs = await mysql_conn.cursor()
		for k in range(1,11,1):
			mysql_quer = "SELECT * from "+ v_scores + " order by score desc LIMIT "+str(k-1)+",1"
			await mysql_curs.execute(mysql_quer)
			a_result = await mysql_curs.fetchone()
			if a_result:
				if v_channel in ["WH","NW","BA","EZ","NM","HD","IN","EX"]:
					mysql_quer = "UPDATE linked_players SET SCORE_MONTH=SCORE_MONTH+"+str(11-k)+",SCORE_ALLTIME=SCORE_ALLTIME+"+str(11-k)+" WHERE PLAYER_ID = "+str(a_result[3])
				elif v_channel in ["TON","TMU","TFU","TKA"]:
					mysql_quer = "UPDATE linked_players SET SCORE_MONTH_TAIKO=SCORE_MONTH_TAIKO+"+str(11-k)+",SCORE_ALLTIME=SCORE_ALLTIME+"+str(11-k)+" WHERE PLAYER_ID = "+str(a_result[3])
				elif v_channel in ["MMX","MHD","MNM","MEZ"]:
					mysql_quer = "UPDATE linked_players SET SCORE_MONTH_MANIA=SCORE_MONTH_MANIA+"+str(11-k)+",SCORE_ALLTIME=SCORE_ALLTIME+"+str(11-k)+" WHERE PLAYER_ID = "+str(a_result[3])
				elif v_channel in ["CRA","CPL","CSA","CCU"]:
					mysql_quer = "UPDATE linked_players SET SCORE_MONTH_CTB=SCORE_MONTH_CTB+"+str(11-k)+",SCORE_ALLTIME=SCORE_ALLTIME+"+str(11-k)+" WHERE PLAYER_ID = "+str(a_result[3])
				await mysql_curs.execute(mysql_quer)
				await mysql_conn.commit()
				bstring = bstring + "[{0}](http://osu.ppy.sh/u/{1}) with a score of {2:,}! Gained {3} points!\r\n".format(str(a_result[2]),str(a_result[3]),int(a_result[5]),str(11-k))
		mysql_conn.close()
		prevwin_embed = discord.Embed(colour=discord.Colour(0xFFFF00), description=bstring)
		await bot.say(embed=prevwin_embed)
		await bot.delete_message(ctx.message)
	except Exception as e:
		log("[updatescores] Error: " +str(e))

@bot.command(pass_context=True)
async def whopicked(ctx):
	'''Tells you who picked the current MotW'''
	try:
		v_channel = getChannel(ctx)
		mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
		mysql_curs = await mysql_conn.cursor()
		mysql_quer = "SELECT map_picker FROM beatmaps where bracket ='"+str(v_channel)+"'"
		await mysql_curs.execute(mysql_quer)
		v_result = await mysql_curs.fetchone()
		await bot.say(embed=olembed(0xffff00,"!",str(v_result[0])+" picked the current MotW for the "+str(v_channel)+" bracket this week. Blame them :)"))
		mysql_conn.close()
		await bot.delete_message(ctx.message)
	except Exception as e:
		log("[whopicked] Error: "+str(e))

@bot.command(pass_context=True)
@commands.has_permissions(manage_channels=True)
async def rollmotw(ctx):
	'''(Perms Required) Roll the next MotW!'''
	await bot.delete_message(ctx.message)
	try:
		get_date = int(time.strftime("%d"))
		get_month = int(time.strftime("%m"))
		get_year = int(time.strftime("%Y"))
		new_date = get_date
		new_month = get_month
		new_year = get_year
		time_string = ""
		if get_date == 31 or get_date == 30 or get_date == 29 or get_date == 1:
			new_date = 7
			if get_date == 1:
				log("")
			else:
				new_month = new_month + 1
			if new_month > 12:
				new_year = new_year + 1
				new_month = 1
		if get_date == 7 or get_date == 8:
			new_date = 14
		if get_date == 14 or get_date == 15:
			new_date = 21
		if get_date == 21 or get_date == 22:
			new_date = 28
		time_string = "{1:02d}/{0:02d}/{2} 11:00:00 PM".format(new_month, new_date, new_year)
		v_channel = getChannel(ctx)
		v_roll = getRole(v_channel)
		v_scores = getScores(v_channel)
		log("1: PASS")
		if v_channel == "ERROR":
			await bot.say(embed=olembed(0xff0000,"!","You can't roll the map pool from this channel. Don't be an idiot TheMeq..."))
		else:
			pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Rolling the Maps:\r\nSeeding the Randomiser...")
			msg = await bot.send_message(ctx.message.channel,embed=pre_embed)
			await asyncio.sleep(1)
			mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
			mysql_curs = await mysql_conn.cursor()
			j=""
			await mysql_curs.execute("SELECT COUNT(*) AS COUN FROM " + v_roll)
			v_rowcount = await mysql_curs.fetchone()
			log(str(v_rowcount[0]))
			log("2: PASS")
			if int(v_rowcount[0])==1:
				mysql_quer = "SELECT * from " + v_roll + " LIMIT 0,1"
				await mysql_curs.execute(mysql_quer)
				log("3: PASS")
			else:
				for k in range(0,np.random.randint(0, 20)):
					seed = str(np.random.randint(0, int(v_rowcount[0])))
					mysql_quer = "SELECT * from " + v_roll + " LIMIT "+str(seed)+",1"
					await mysql_curs.execute(mysql_quer)
					v_result = await mysql_curs.fetchone()
					a = v_result[3]
					t = v_result[4]
					v = v_result[5]
					m = v_result[6]
					pre_embed = discord.Embed(colour=discord.Colour(0x00FFFF), description="Rolling the Maps: "+j+"\r\n" + a + " - " + t + " (" + v + ") by " + m)
					msg = await bot.edit_message(msg,embed=pre_embed)
					j=j+"."
					await asyncio.sleep(1)
				seed = str(np.random.randint(0, int(v_rowcount[0])-1))
				mysql_quer = "SELECT * from " + v_roll + " LIMIT "+str(seed)+",1"
				await mysql_curs.execute(mysql_quer)
				log("4: PASS")
			v_result = await mysql_curs.fetchone()
			log("5: PASS")
			
			p = v_result[1]
			mysql_quer = "SELECT PLAYER_NAME FROM linked_players where DISCORD_ID = "+str(p)
			
			await mysql_curs.execute(mysql_quer)
			p_result = await mysql_curs.fetchone()
			if p_result:
				p_n = p_result[0]
			else:
				p_n = "?"
			i = v_result[2]
			a = v_result[3]
			t = v_result[4]
			v = v_result[5]
			m = v_result[6]

			mysql_quer = "UPDATE beatmaps SET map_id = "+str(i)+",date_range_tstmp=STR_TO_DATE('"+ time_string +"','%d/%m/%Y %r'),map_picker='"+str(p_n)+"' WHERE bracket = '"+v_channel+"'"
			await mysql_curs.execute(mysql_quer)
			await mysql_conn.commit()
			log("7: PASS")
			async with aiohttp.ClientSession() as cs:
				if v_channel in ["WH","NW","BA","EZ","NM","HD","IN","EX"]:
					mode = 0
				elif v_channel in ["TON","TMU","TFU","TKA"]:
					mode = 1
				elif v_channel in ["MMX","MHD","MNM","MEZ"]:
					mode = 3
				elif v_channel in ["CRA","CPL","CSA","CCU"]:
					mode = 2
				log("8: PASS")
				url = osu_api + "get_beatmaps?k=" + osu_key + "&b=" + str(i) + "&m=" + str(mode)
				async with cs.get(url) as s:
					log("9: PASS")
					ses = await s.json()
					song_artis = ses[0]['artist']
					song_artis = ses[0]['artist']
					song_beats = ses[0]['beatmapset_id']
					song_title = ses[0]['title']
					song_diffi = ses[0]['version']
					song_mappe = ses[0]['creator']
					setmotw_embed = discord.Embed(colour=discord.Colour(0xFFFF00), description="New Map of the Week has been chosen!\r\n\r\n[{0} - {1} ({2})](http://osu.ppy.sh/b/{3}) by {4}\r\n\r\n[Download via Website](http://osu.ppy.sh/d/{5})\r\n[Download via osu!Direct (Supporter Only)](http://themeq.xyz/r.php?b={5})".format(song_artis,song_title,song_diffi,i,song_mappe,song_beats))
					setmotw_embed.set_thumbnail(url="http://b.ppy.sh/thumb/" + str(song_beats) + "l.jpg")
					await bot.edit_message(msg,embed=setmotw_embed)
					server = bot.get_channel("316842433260421130")
					fmt = 'Map of the Week has been set for the **{5}** bracket! {0} - {1} ({2}) by {4}'
					await bot.send_message(server, fmt.format(song_artis,song_title,song_diffi,i,song_mappe,v_channel))
			try:
				mysql_quer = "DELETE FROM " + v_scores + " WHERE 1=1"
				await mysql_curs.execute(mysql_quer)
				await mysql_conn.commit()
				mysql_quer = "DELETE FROM " + v_roll + " WHERE BeatmapID = " + str(i)
				await mysql_curs.execute(mysql_quer)
				await mysql_conn.commit()
				mysql_conn.close()
			except Exception as e:
				log("[rollmotw] Delete Error: "+str(e))
	except Exception as e:
		log("[rollmotw] Error: "+str(e))

@bot.command(pass_context=True)
async def rank(ctx, player_name : str="!", game_mode = "standard"):
	"""Get yours or another players current rank and pp! (Can also specify taiko,mania and ctb.)"""
	try:
		sender_channel_id = ctx.message.channel.id
		sender_bracket = getChannel(ctx)
		sender_mode = getMode(sender_bracket)
		
		player_discord_id = ctx.message.author.id
			
		game_mode_string = "standard"
		
		if player_name == "!":
			player_name = ctx.message.author.name
			mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
			mysql_curs = await mysql_conn.cursor()
			await mysql_curs.execute("SELECT * from linked_players WHERE DISCORD_ID = '"+str(player_discord_id)+"' and LINKED='1'")
			v_result = await mysql_curs.fetchone()
			if v_result:
				player_name = v_result[3]
				game_mode_value = sender_mode
				if game_mode_value == 0:
					game_mode_string = "standard"
				if game_mode_value == 1:
					game_mode_string = "taiko"
				if game_mode_value == 2:
					game_mode_string = "ctb"
				if game_mode_value == 3:
					game_mode_string = "mania"
			else:
				await bot.say(embed=olembed(0xff0000,"!",":bangbang: You're account is not linked. You will need to specify a player name!"))
		elif player_name != "!":
			if game_mode.lower() == "standard":
				game_mode_value = 0
				game_mode_string = "standard"
			elif game_mode.lower() == "taiko":
				game_mode_value = 1
				game_mode_string = "taiko"
			elif game_mode.lower() == "ctb":
				game_mode_value = 2
				game_mode_string = "ctb"
			elif game_mode.lower() == "mania":
				game_mode_value = 3
				game_mode_string = "mania"
			else:
				game_mode_value = 0
				game_mode_string = "standard"
		async with aiohttp.ClientSession() as cs:
			url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name.replace(" ","+") + "&m=" + str(game_mode_value)
			async with cs.get(url) as r:
				res = await r.json()
				if not res:
					await bot.say(embed=olembed(0xff0000,"!",":bangbang: osu! doesn't have a player with that name!"))
				else:
					r_player = res[0]['username']
					r_playerid = res[0]['user_id']
					r_rank = int(res[0]['pp_rank'])
					r_pp = float(res[0]['pp_raw'])
					r_acc = float(res[0]['accuracy'])
					r_cpp = int(res[0]['pp_country_rank'])
					if r_pp == "0":
						await bot.say(embed=olembed(0x00ff00,"!",":bangbang: {0} hasn't played recently and doesn't have a rank or score.".format(r_player)))
					else:
						r_timestamp = int(time.time())
						url = 'https://a.ppy.sh/' + str(r_playerid) + '_' + str(r_timestamp) + '.png'  
						urllib.request.urlretrieve(url, 'image_cache/ava_' + str(r_playerid) + '.png')
						img = Image.open("images/rank_bg.png")
						ava = Image.open("image_cache/ava_" + str(r_playerid) + ".png")
						fnt = ImageFont.truetype('fonts/dope.ttf', 40)
						txt = ImageFont.truetype('fonts/roboto.ttf', 13)
						img_w = 400
						ava = ava.resize((96,96), Image.BILINEAR)
						img.paste(ava, (10,10))
						d = ImageDraw.Draw(img)
						r_player = r_player.replace("[","(").replace("]",") ")
						name_w, name_h = fnt.getsize(r_player)
						name_x = int(img_w - ((img_w-116)/2)-(name_w/2))
						
						for x in range(name_x-1,name_x+2):
							for y in range(9,12):
								d.text((x,y), r_player, font=fnt, fill=(0,0,0,255))
						d.text((name_x,10), r_player, font=fnt, fill=(255,255,255,255))
						for x in range(115,118):
							for y in range(64,67):
								d.text((x,y), "Rank: #{0:,}\r\nPP: {1:,}pp".format(r_rank,r_pp), font=txt, fill=(0,0,0,255))
						d.text((116,65), "Rank: #{0:,}\r\nPP: {1:,}pp".format(r_rank,r_pp), font=txt, fill=(255,255,255,255))
						c = int(img_w - ((img_w-116)/2))-10
						for x in range(c-1,c+2):
							for y in range(64,67):
								d.text((x,y), "Acc: {0:.2f}%\r\nCountry Rank: #{1:,}".format(r_acc, r_cpp), font=txt, fill=(0,0,0,255))
						d.text((c,65), "Acc: {0:.2f}%\r\nCountry Rank: #{1:,}".format(r_acc, r_cpp), font=txt, fill=(255,255,255,255))
						img.save("output_cache/output.png")
						await bot.send_file(ctx.message.channel, "output_cache/output.png")			
	except Exception as e:
		log("[rank] Error: "+str(e))
	await bot.delete_message(ctx.message)
	
@bot.command(pass_context=True)
async def topplay(ctx, player_name: str="!", game_mode = "standard"):
	"""Get the details of a players top play! (Can also specify taiko,mania and ctb.)"""
	v_id = ctx.message.author.id
	msg = await bot.send_message(ctx.message.channel,embed=olembed(0xFFFF00,"!","Getting top play for this player..."))
	v_name = ctx.message.author.name
	v_author = ctx.message.author
	if player_name == "!":
		mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
		mysql_curs = await mysql_conn.cursor()
		await mysql_curs.execute("SELECT * from linked_players WHERE DISCORD_ID = '"+str(v_id)+"' and LINKED='1'")
		v_result = await mysql_curs.fetchone()
		if v_result:
			player_name = v_result[3]
	if player_name != "!":
		async with aiohttp.ClientSession() as cs:
			url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name.replace(" ","+") + "&m=0"
			async with cs.get(url) as r:
				res = await r.json()
				if not res:
					await bot.edit_message(msg,embed=olembed(0xff0000,"!","osu! doesn't have a player with that name!"))
				else:
					r_player = res[0]['username']
					r_playerid = res[0]['user_id']
					r_rank = res[0]['pp_rank']
					r_timestamp = int(time.time())
					if game_mode.lower() == "standard":
						game_mode_value = 0
						game_mode_string = "standard"
					elif game_mode.lower() == "taiko":
						game_mode_value = 1
						game_mode_string = "taiko"
					elif game_mode.lower() == "ctb":
						game_mode_value = 2
						game_mode_string = "ctb"
					elif game_mode.lower() == "mania":
						game_mode_value = 3
						game_mode_string = "mania"
					else:
						game_mode_value = 0
						game_mode_string = "standard"
					url = osu_api + "get_user_best?k=" + osu_key + "&u=" + player_name.replace(" ","+") + "&m=" + str(game_mode_value) + "&limit=1"
					async with cs.get(url) as b:
						bes = await b.json()
						if not bes:
							await bot.edit_message(msg,embed=olembed(0xffff00,"!","osu! does not list a recent play for " + r_player + "!"))
						else:
							try:
								beatmap_id = bes[0]['beatmap_id']
								lastplay_score = int(bes[0]['score'])
								lastplay_maxco = bes[0]['maxcombo']
								lastplay_fifty = bes[0]['count50']
								lastplay_hundr = bes[0]['count100']
								lastplay_three = bes[0]['count300']
								lastplay_misse = bes[0]['countmiss']
								lastplay_katu = bes[0]['countkatu']
								lastplay_geki = bes[0]['countgeki']
								lastplay_modif = bes[0]['enabled_mods']
								lastplay_accur = round(((((int(lastplay_three) * 300) + (int(lastplay_hundr) * 100) + (int(lastplay_fifty) * 50) + (int(lastplay_misse) * 0)) / ((int(lastplay_three) + int(lastplay_hundr) + int(lastplay_fifty) + int(lastplay_misse)) * 300)) * 100),2)
								if game_mode_value == 2:
									lastplay_accur = round((((int(lastplay_three)) + (int(lastplay_hundr)) + (int(lastplay_fifty))) / ((int(lastplay_three)) + (int(lastplay_hundr)) + (int(lastplay_fifty)) + (int(lastplay_misse)) + (int(lastplay_katu))))*100,2)
								if game_mode_value == 3:
									lastplay_accur = round((((int(lastplay_fifty) * 50) + (int(lastplay_hundr) * 100) + (int(lastplay_katu) * 200) + (int(lastplay_geki) * 300) + (int(lastplay_three) * 300)) / ((int(lastplay_fifty)+int(lastplay_hundr)+int(lastplay_katu)+int(lastplay_geki)+int(lastplay_three)+int(lastplay_misse)) * 300) * 100) ,2)
								if lastplay_modif != "" or lastplay_modif != "0" or lastplay_modif !=0:
									used_mods = GetMods(lastplay_modif)
								if used_mods:
									gm = ""
									for mods in used_mods:
										gm = gm + osu_mods_t[str(mods)] + ""
										if game_mode_string == "standard":
											data_beatmap = await BeatmapData(beatmap_id,gm,lastplay_accur,lastplay_hundr,lastplay_fifty,lastplay_maxco,lastplay_misse)
								else:
									gm = ""
									if game_mode_string == "standard":
										data_beatmap = await BeatmapData(beatmap_id,"!",lastplay_accur,lastplay_hundr,lastplay_fifty,lastplay_maxco,lastplay_misse)
								if game_mode_string == "standard":
									star_rating = str(round(data_beatmap['stars'],2))
									pp_gained = str(round(data_beatmap['pp'],2))
								else:
									star_rating = ""
									pp_gained = ""
								lastplay_ranks = bes[0]['rank']
								url = osu_api + "get_beatmaps?k=" + osu_key + "&b=" + str(beatmap_id) + "&m=" + str(game_mode_value)
								async with cs.get(url) as s:
									ses = await s.json()
									song_artis = ses[0]['artist']
									song_beats = ses[0]['beatmapset_id']
									song_title = ses[0]['title']
									song_diffi = ses[0]['version']
									song_mappe = ses[0]['creator']
									song_bpm = ses[0]['bpm']
									if used_mods:
										for mods in used_mods:
											if mods == 64:
												song_bpm = float(song_bpm) * 1.5
											if mods == 256:
												song_bpm = float(song_bpm) * 0.75
									lastplay_score = "{:,}".format(lastplay_score)
									embed = discord.Embed(colour=discord.Colour(0xFFCC66), description="Top play by [{0}](http://osu.ppy.sh/u/{8}) (#{11:,}) with a rank of {1} and a score of {2}\r\n[{3} - {4}](http://osu.ppy.sh/s/{5}) ([{6}](http://osu.ppy.sh/b/{9})) by {7} - osu!{10}".format(player_name,osu_ranks[lastplay_ranks],lastplay_score,song_artis,song_title,song_beats,song_diffi,song_mappe,r_playerid,beatmap_id,game_mode_string,int(r_rank)))
									embed.set_thumbnail(url="http://b.ppy.sh/thumb/" + str(song_beats) + "l.jpg")
									embed.set_author(name=r_player, icon_url="https://a.ppy.sh/" + r_playerid + "_" + str(r_timestamp) + ".png")
									if game_mode_string == "standard":
										embed.add_field(inline=False,name="Beatmap Details", value = "OD: " + str(data_beatmap['od']) + " | AR: " + str(data_beatmap['ar']) + " | CS: " + str(data_beatmap['cs']) + " | HP: " + str(data_beatmap['hp']) + " | Star Rating: " + star_rating +" | BPM: "+ str(song_bpm)+"\r\n")
									if used_mods:
										um = ""
										for mods in used_mods:
											um = um + osu_mods[str(mods)] + " "
									else:
										um = "None"
									embed.add_field(inline=False,name="Mods", value=um)
									if lastplay_ranks != "F":
										if pp_gained == "":
											embed.add_field(name="Stats", value="Max Combo: " + lastplay_maxco + "\r\nAccuracy: " + str(lastplay_accur) + "% "+hit_300+": " + lastplay_three + " "+hit_100+": " + lastplay_hundr + " "+hit_50+": " + lastplay_fifty + " "+hit_0+": " + lastplay_misse)
										else:
											embed.add_field(name="Stats", value="Max Combo: " + lastplay_maxco + "\r\nAccuracy: " + str(lastplay_accur) + "% "+hit_300+": " + lastplay_three + " "+hit_100+": " + lastplay_hundr + " "+hit_50+": " + lastplay_fifty + " "+hit_0+": " + lastplay_misse + "\r\nPP: "+pp_gained)
									embed.set_footer(text=str(ctx.message.author.name) + " ran this command.")
									await bot.edit_message(msg,embed=embed)
							except Exception as e:
								await bot.edit_message(msg,embed=olembed(0xff0000,"!","osu! does not list a recent play for " + r_player + "!"))
								log("[topplay] Error: "+str(e))
	else:
		await bot.edit_message(msg,embed=olembed(0xff0000,"!","Your account isn't linked, so you need to specify a player name."))
	await bot.delete_message(ctx.message)

@bot.command(pass_context=True)
async def lastplay(ctx, player_name : str="!",game_mode = "!"):
	"""Get the details of a players last play! (Can also specify taiko,mania and ctb.)"""
	await bot.delete_message(ctx.message)
	v_id = ctx.message.author.id
	msg = await bot.send_message(ctx.message.channel,embed=olembed(0xFFFF00,"!","Getting lastplay for this player..."))
	v_name = ctx.message.author.name
	v_author = ctx.message.author
	v_channel = getChannel(ctx)
	if player_name == "!":
		mysql_conn = await aiomysql.connect(host= mysql_host, port= 3306, user= mysql_user, password= mysql_pass, db= mysql_data)
		mysql_curs = await mysql_conn.cursor()
		await mysql_curs.execute("SELECT * from linked_players WHERE DISCORD_ID = '"+str(v_id)+"' and LINKED='1'")
		v_result = await mysql_curs.fetchone()
		if v_result:
			player_name = v_result[3]
			player_id = v_result[2]
		else:
			await bot.edit_message(msg,embed=olembed(0xffff00,"!","Your account isn't linked so you will have to specify a player name!"))
	try:
		async with aiohttp.ClientSession() as cs:
			if v_channel in ["WH","NW","BA","EZ","NM","HD","IN","EX"] and game_mode == "!":
				url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name.replace(" ","+") + "&m=0"
				game_mode = "standard"
			elif v_channel in ["TON","TMU","TFU","TKA"]:
				url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name.replace(" ","+") + "&m=1"
				game_mode = "taiko"
			elif v_channel in ["MMX","MHD","MNM","MEZ"]:
				url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name.replace(" ","+") + "&m=3"
				game_mode = "mania"
			elif v_channel in ["CRA","CPL","CSA","CCU"]:
				url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name.replace(" ","+") + "&m=2"
				game_mode = "ctb"
			else:
				url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name.replace(" ","+") + "&m=0"
			if game_mode != "standard":
				if game_mode == "taiko":
					url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name.replace(" ","+") + "&m=1"
					game_mode = "taiko"
				elif game_mode == "mania":
					url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name.replace(" ","+") + "&m=3"
					game_mode = "mania"
				elif game_mode == "ctb":
					url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name.replace(" ","+") + "&m=2"
					game_mode = "ctb"
				else:
					url = osu_api + "get_user?k=" + osu_key + "&u=" + player_name.replace(" ","+") + "&m=0"
					game_mode = "standard"
			log(url)
			async with cs.get(url) as r:
				res = await r.json()
				log(str(res))
				if not res:
					await bot.edit_message(msg,embed=olembed(0xff0000,"!","osu! doesn't have a player called " + player_name + "!"))
				else:
					
					r_player = res[0]['username']
					r_playerid = res[0]['user_id']
					r_rank = res[0]['pp_rank']
					r_timestamp = int(time.time())
					if game_mode.lower() == "standard":
						game_mode_value = 0
						game_mode_string = "standard"
					elif game_mode.lower() == "taiko":
						game_mode_value = 1
						game_mode_string = "taiko"
					elif game_mode.lower() == "ctb":
						game_mode_value = 2
						game_mode_string = "ctb"
					elif game_mode.lower() == "mania":
						game_mode_value = 3
						game_mode_string = "mania"
					else:
						game_mode_value = 0
						game_mode_string = "standard"
					url = osu_api + "get_user_recent?k=" + osu_key + "&u=" + player_name.replace(" ","+") + "&m=" + str(game_mode_value) + "&limit=1"
					log(url)
					async with cs.get(url) as b:
						bes = await b.json()
						
						if not bes:
							await bot.edit_message(msg,embed=olembed(0xff0000,"!","osu! does not list a recent "+game_mode_string+" play for " + r_player + "!"))
						else:
							try:
								log(str(bes))
								beatmap_id = bes[0]['beatmap_id']
								lastplay_score = int(bes[0]['score'])
								lastplay_maxco = bes[0]['maxcombo']
								lastplay_fifty = bes[0]['count50']
								lastplay_hundr = bes[0]['count100']
								lastplay_three = bes[0]['count300']
								lastplay_misse = bes[0]['countmiss']
								lastplay_katu = bes[0]['countkatu']
								lastplay_geki = bes[0]['countgeki']
								lastplay_modif = bes[0]['enabled_mods']
								lastplay_accur = round(((((int(lastplay_three) * 300) + (int(lastplay_hundr) * 100) + (int(lastplay_fifty) * 50) + (int(lastplay_misse) * 0)) / ((int(lastplay_three) + int(lastplay_hundr) + int(lastplay_fifty) + int(lastplay_misse)) * 300)) * 100),2)
								if game_mode_value == 2:
									lastplay_accur = round((((int(lastplay_three)) + (int(lastplay_hundr)) + (int(lastplay_fifty))) / ((int(lastplay_three)) + (int(lastplay_hundr)) + (int(lastplay_fifty)) + (int(lastplay_misse)) + (int(lastplay_katu))))*100,2)
								if game_mode_value == 3:
									lastplay_accur = round((((int(lastplay_fifty) * 50) + (int(lastplay_hundr) * 100) + (int(lastplay_katu) * 200) + (int(lastplay_geki) * 300) + (int(lastplay_three) * 300)) / ((int(lastplay_fifty)+int(lastplay_hundr)+int(lastplay_katu)+int(lastplay_geki)+int(lastplay_three)+int(lastplay_misse)) * 300) * 100) ,2)
								if lastplay_modif != "" or lastplay_modif != "0" or lastplay_modif !=0:
									used_mods = GetMods(lastplay_modif)
								if used_mods:
									gm = ""
									for mods in used_mods:
										gm = gm + osu_mods_t[str(mods)] + ""
										if game_mode_string == "standard":
											data_beatmap = await BeatmapData(beatmap_id,gm,lastplay_accur,lastplay_hundr,lastplay_fifty,lastplay_maxco,lastplay_misse)
								else:
									gm = ""
									if game_mode_string == "standard":
										data_beatmap = await BeatmapData(beatmap_id,"!",lastplay_accur,lastplay_hundr,lastplay_fifty,lastplay_maxco,lastplay_misse)
								if game_mode_string == "standard":
									star_rating = str(round(data_beatmap['stars'],2))
									pp_gained = str(round(data_beatmap['pp'],2))
								else:
									star_rating = ""
									pp_gained = ""
								lastplay_ranks = bes[0]['rank']
								url = osu_api + "get_beatmaps?k=" + osu_key + "&b=" + str(beatmap_id) + "&m=" + str(game_mode_value)
								async with cs.get(url) as s:
									ses = await s.json()
									song_artis = ses[0]['artist']
									song_beats = ses[0]['beatmapset_id']
									song_title = ses[0]['title']
									song_diffi = ses[0]['version']
									song_mappe = ses[0]['creator']
									song_bpm = ses[0]['bpm']
									m, s = divmod(int(ses[0]['total_length']), 60)
									song_length = "%02d:%02d" % (m, s)
									m, s = divmod(int(ses[0]['hit_length']), 60)
									song_drain = "%02d:%02d" % (m, s)
									if used_mods:
										for mods in used_mods:
											if mods == 64:
												song_bpm = float(song_bpm) * 1.5
											if mods == 256:
												song_bpm = float(song_bpm) * 0.75
									if lastplay_ranks == "F":
										embed = discord.Embed(colour=discord.Colour(0xFF0000), description="Last map played by [{0}](http://osu.ppy.sh/u/{6}) (#{9:,}) was not passed.\r\nScore: {10:,}\r\n[{1} - {2}](http://osu.ppy.sh/s/{3}) ([{4}](http://osu.ppy.sh/b/{7})) by {5} - osu!{8}".format(player_name,song_artis,song_title,song_beats,song_diffi,song_mappe,r_playerid,beatmap_id,game_mode_string,int(r_rank),lastplay_score))
									else:
										lastplay_score = "{:,}".format(lastplay_score)
										embed = discord.Embed(colour=discord.Colour(0x00FF00), description="Last map played by [{0}](http://osu.ppy.sh/u/{8}) (#{11:,}) with a rank of {1} and a score of {2}\r\n[{3} - {4}](http://osu.ppy.sh/s/{5}) ([{6}](http://osu.ppy.sh/b/{9})) by {7} - osu!{10}".format(player_name,osu_ranks[lastplay_ranks],lastplay_score,song_artis,song_title,song_beats,song_diffi,song_mappe,r_playerid,beatmap_id,game_mode_string,int(r_rank)),)
										embed.set_thumbnail(url="http://b.ppy.sh/thumb/" + str(song_beats) + "l.jpg")
									embed.set_author(name=r_player, icon_url="https://a.ppy.sh/" + r_playerid + "_" + str(r_timestamp) + ".png")
									
									if game_mode_string == "standard":
										embed.add_field(inline=False,name="Beatmap Details", value = "OD: " + str(data_beatmap['od']) + " | AR: " + str(data_beatmap['ar']) + " | CS: " + str(data_beatmap['cs']) + " | HP: " + str(data_beatmap['hp']) + " | Star Rating: " + star_rating +" | BPM: " + str(song_bpm) + "\r\nLength: "+str(song_length)+" ("+song_drain+" Drain)")
									if used_mods:
										um = ""
										for mods in used_mods:
											um = um + osu_mods[str(mods)] + " "
									else:
										um = "None"
									embed.add_field(inline=False,name="Mods", value=um)
									if lastplay_ranks != "F":
										if pp_gained == "":
											if game_mode_value == 3:
												embed.add_field(name="Stats", value="Max Combo: " + lastplay_maxco + "\r\nAccuracy: " + str(lastplay_accur) + "% "+hit_m_350+": "+lastplay_geki+" "+hit_m_300+": " + lastplay_three + " "+hit_m_200+": "+lastplay_katu+" "+hit_m_100+": " + lastplay_hundr + " "+hit_m_50+": " + lastplay_fifty + " "+hit_m_0+": " + lastplay_misse)
											else:
												embed.add_field(name="Stats", value="Max Combo: " + lastplay_maxco + "\r\nAccuracy: " + str(lastplay_accur) + "% "+hit_300+": " + lastplay_three + " "+hit_100+": " + lastplay_hundr + " "+hit_50+": " + lastplay_fifty + " "+hit_0+": " + lastplay_misse)
										else:
											embed.add_field(name="Stats", value="Max Combo: " + lastplay_maxco + "\r\nAccuracy: " + str(lastplay_accur) + "% "+hit_300+": " + lastplay_three + " "+hit_100+": " + lastplay_hundr + " "+hit_50+": " + lastplay_fifty + " "+hit_0+": " + lastplay_misse + "\r\nPP: "+pp_gained)
									embed.set_footer(text=str(ctx.message.author.name) + " ran this command.")
									await bot.edit_message(msg,embed=embed)
							except Exception as e:
								await bot.edit_message(msg,embed=olembed(0xffff00,"!","osu! does not list a recent play for " + r_player + "!"))
								log("[lastplay] Error: "+str(e))
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
								

@bot.command(pass_context=True)
async def roll(ctx,v = "100"):
	"""Roll a random number between 0 and whatever!"""
	if not v.isnumeric():
		v=int(100)
	else:
		v=int(v)
	v_author = ctx.message.author.nick
	if v_author == None:
		v_author = ctx.message.author.name
	v_random = np.random.randint(0,v)
	embed = discord.Embed(colour=discord.Colour(0x3366FF), description="{0} rolled {1:,}!".format(v_author,v_random))
	await bot.say(embed=embed)
	await bot.delete_message(ctx.message)

@bot.command(pass_context=True)
@commands.has_permissions(manage_channels=True)
async def clear(ctx, r : int):
	"""(Perms Required) Delete x given messages from the current channel!"""
	o_channel = ctx.message.channel
	i_counter = 0
	i_number = r + 1
	async for x in bot.logs_from(o_channel,i_number):
		if i_counter <= i_number:
			await bot.delete_message(x)
			i_counter += 1
			await asyncio.sleep(0.1)

def log(log :str):
	print("<" + str(time.strftime("%d %b %Y - %H:%M:%S")) + "> " + log)

bot.run(dis_key)
