from io import BytesIO
from logging import exception
from typing import Type
import typing
import discord,pymongo,json,osuapi,requests,re
from discord.errors import HTTPException
from PIL import Image as img, ImageDraw
from PIL import ImageFont as imgfont
from PIL import ImageDraw as imgdraw
from PIL import ImageOps, ImageSequence
from discord.flags import Intents
from discord.ext.commands.errors import CommandInvokeError, CommandNotFound
from discord.ext import commands
import time,random

enc = open("config.json","r",encoding="utf-8")

config = json.load(enc)


mongo = pymongo.MongoClient(config["mongo"])

osu = osuapi.OsuApi(config['osu'], connector=osuapi.ReqConnector())

SPX = mongo["Usuarios"]
SPXU = SPX["SPXUSERS"]
SPXS = SPX["SPXSERVERS"]
SPXB = SPX["SPXBL"]


p = discord.Colour.from_rgb(114, 137, 218)

def prefix(bot,message):
    x = SPXU.find({"_id":message.guild.id}).limit(1)
    lis=[]
    prefix = ""
    for i in x:
        lis.append(i)
    try:
        if lis[0]['prefix'] == None:
            prefix = "!!"
        else:
            prefix = lis[0]['prefix']
    except:
        prefix = "!!"
    return commands.when_mentioned_or(prefix)(bot, message)

bot = commands.AutoShardedBot(command_prefix=prefix,intents=Intents.all(),case_insensitive=True)
bot.remove_command("help")


def DadosS(server: int) -> dict:
    x = SPXS.find({"_id":server}).limit(1)
    for i in x:
        return i  

def DadosU(user: int) -> dict:
    x = SPXU.find({"_id":user}).limit(1)
    for i in x:
        return i  

async def listallusers() -> list:
    d = []
    for i in SPXU.find().distinct('_id'):
        d.append(i)
    return d

async def listallservers() -> list:
    d = []
    for i in SPXS.find().distinct('_id'):
        d.append(i)
    return d

async def SalvarU(dados,id) -> None:
    sets = {"$set":dados}
    SPXU.update_one(SPXU.find_one({"_id":id}),sets)

async def SalvarS(dados,id) -> None:
    sets = {"$set":dados}
    SPXS.update_one(SPXS.find_one({"_id":id}),sets)

async def CConta(user: discord.Member) -> None:
    if str(user.id) in await listallusers():
        return
    else:
        if user.bot == True:
            return
        SPXU.insert_one({"_id":user.id,'nome':user.name,'mar':0,'desc':'Eu sou uma pessoa misteriosa, mas eu posso mudar minha descrição usando .desc','rep':0,"xp_time":0,'money':0,'gold':0,'inventory':{"Padrão": {"name": "Padrão","desc": "Background padrão","tip": "BackGround Profile","use": True,"cont": 0,"onetime": True,"preview": "https://media.discordapp.net/attachments/776197504378732555/795800876383338496/default.png?width=642&height=459","tipte": "back-pf","author": "SPX Team"}},'profile':{'back-pf':{'url':'https://media.discordapp.net/attachments/776197504378732555/795800876383338496/default.png?width=642&height=459','name':"Padrão"}}})

async def GCConta(guild: discord.Guild) -> None:
    if str(guild.id) in await listallservers():
        return
    else:
        SPXS.insert_one({"_id":guild.id,'nome':guild.name,'users':{},'config':{'time_xp':30,'role_mute':0,'welcome_channel':0,'leave_channel':0,'mediaxp':10,'WelcomeMsg':'[mention] bem vindo! ','LeaveMsg':'[mention] saiu do servidor!','dmpu':0,'autorole':{},'controle':0,'rr':{},'rrcont':0},'reg':{},'prefix':"!!",'contIDreg':0,'automessage':0,'tick':{}})

def IMAGEGET(ctx,item) -> None or str:
    
    if len(ctx.message.attachments) >= 1:
        if re.search("(\.png|\.jpeg|\.jpg|\.gif|\.webp)",ctx.message.attachments[0].url) != None:
            return ctx.message.attachments[0].url
        else:
            pass    
    if isinstance(item,discord.Member):
        return item.avatar_url
    elif isinstance(item,discord.PartialEmoji): 
        return item.url
    elif isinstance(item, str):
        a = re.search("(\.png|\.jpeg|\.jpg|\.gif|\.webp)",item)
        if a == None:
            return None
        else:
            return item
    else:
        return None

def IMAGEGETEXT(link:str) -> str or bool:
    a = re.search("(\.png|\.jpeg|\.jpg|\.gif|\.webp)",str(link))
    if a == None:
        return False
    else:
        return a[0]

def thumbnails(frames,size):
    for frame in frames:
        thumbnail = frame.copy()
        print("a")
        thumbnail.thumbnail(size, img.ANTIALIAS)
        yield thumbnail

def current_milli_time():
    return round(time.time() * 1000)

def blacklist():
    def checar(ctx):
        try:
            if SPXB.find({"_id":id})[0]['blacklisted'] == True:
                return False
            else:
                return True
        except Exception as ex: 
            return True
    return commands.check(checar)

def get_prefix(idguild) -> str:
    return DadosS(idguild)['prefix'] or "!!"

@bot.event
async def on_ready() -> None:
    print("~~ SPX está ligado ~~" )
    print("Analizando Servidores...")
    guilds = await listallservers()
    servers = 0 
    serversname = []
    for i in bot.guilds:
        if not i.id in guilds:
           await GCConta(i)
           servers += 1
           serversname.append(i.name)
    print("------------------------")
    print(f"Foram registrados {servers} servidor(es)!")
    print(f"Servidores:")
    for x in serversname:
        print(x)

@bot.event
async def on_message(message: discord.Message) -> None:
    if message.content in [f"<@!{bot.user.id}>",f"<@{bot.user.id}>"]:
        await message.channel.send(f"Olá! Você me chamou? Use `{get_prefix(message.guild.id)}help` para saber meus comandos!")
    await bot.process_commands(message)
class Utils(commands.Cog):
    
    @commands.command(name='help', description="Comando de ajuda",aliases=["ajuda","h","a","ajd","ajudinhaae"])
    @commands.cooldown(1,5,commands.BucketType.user)
    @blacklist()
    async def help(self,ctx:commands.Context,command_=None) -> None:
        if command_ == None:
            embed = discord.Embed(title="Ajuda SPX",description="Site para meus comandos: https://spx.bot/commands\n\nDica! Use **!!help <nome do comando>** para ver uma ajuda mais detalhada!")
            embed.set_thumbnail(url=bot.user.avatar_url)
            embed.colour = p
            await ctx.send(embed=embed)
        else:
            try:
                command: commands.Command = bot.get_command(command_)
                await ctx.send(f"**{command.name} / {command}**\n\nDescrição: **{command.description if command.description != '' else 'Nenhuma descrição fornecida' }**\nOutros nomes: **{str(command.aliases).replace('[','').replace(']','').replace('aspas','') if command.aliases != [] else 'Não tem variações'}**") 
            except AttributeError:
                await ctx.send("**:warning: | O comando não existe...**")

    @commands.command(name="avatar", description="Veja o seu avatar ou o do seus amigos",aliases=['av','pfp'])
    @commands.cooldown(1,5,commands.BucketType.user)
    @blacklist()
    async def avatar(self,ctx:commands.Context,user:discord.User=None) -> None:
        user = user or ctx.author
        embed = discord.Embed(title=f'Avatar de {user.name}',description=f"Link: [Avatar Link]({user.avatar_url})")
        embed.set_image(url=user.avatar_url)
        embed.colour = p
        await ctx.send(embed=embed)

    @commands.command(name="ping", description="Veja a latencia do bot, caso esteja lento em seus comandos.",aliases=['pong','<@!660193448711946262>','<@660193448711946262>',"latency","latencia"])
    @commands.cooldown(1,5,commands.BucketType.user)
    @blacklist()
    async def ping(self,ctx:commands.Context) -> None:
        before = time.monotonic()
        a = await ctx.send(f":ping_pong: | **Calculando...**")         
        ping = (time.monotonic() - before) * 1000
        before = time.monotonic()
        _ = DadosS(ctx.guild.id)
        ping_db = (time.monotonic() - before) * 1000
        status = ""
        if max([ping,ping_db,int(bot.latency * 1000)]) > 200:
            status = ":pensive: Meh"
        elif max([ping,ping_db,int(bot.latency * 1000)]) > 400:
            status = ":sneezing_face: Horrivel"
        elif max([ping,ping_db,int(bot.latency * 1000)]) > 50:
            status = ":sunglasses: Excelente"
        elif max([ping,ping_db,int(bot.latency * 1000)]) > 100:
            status = ":+1: Bom"
        await a.edit(content=f":ping_pong: | **Latencia da API: {int(bot.latency * 1000)}ms**\n⠀⠀⠀⠀-> **Latencia do BOT: {int(ping)}ms**\n⠀⠀⠀⠀-> **Latencia do Banco de dados: {int(ping_db)}ms**\n{status}")

class ServerManagement(commands.Cog):

    @commands.command(name="addemoji", description="Adicione um emoji no servidor fácil!",aliases=['aemoji','adicionar_emoji'])
    @commands.cooldown(1,5,commands.BucketType.user)
    @blacklist()
    async def addemoji(self,ctx:commands.Context,emojiname,IMAGEOPEN:typing.Union[discord.PartialEmoji, discord.Member, str]):
        link = IMAGEGET(ctx,IMAGEOPEN)
        emoji_ext = IMAGEGETEXT(link)
        if link == None:
            await ctx.send("**:x: | Formato invalido! Formatos aceitados: [JPEG,JPG,PNG,GIF,WEBP]**")
            return
        image = None
        warning = "Tudo certo!"
        RESIZE = False
        m = await ctx.send("Baixando imagem...")
        if BytesIO(requests.get(link).content).getbuffer().nbytes / 1000 > 256:
            image = img.open(BytesIO(requests.get(link).content))
            RESIZE = True
            warning = "O(a) imagem/Gif estava muito pesada, a altura e a largura foi alterada para **256x256**"
        else:
            image = img.open(BytesIO(requests.get(link).content))
        if emoji_ext == ".gif":
            a = ImageSequence.Iterator(image)
            if RESIZE == True:
                size = (256,256)
            else:
                size = image.size
            frames = thumbnails(a,size)
            image = next(frames)
            image.save(f"image{emoji_ext}",
                    save_all=True,
                    append_images=list(frames),
                    loop=0
            )
        else:
            if RESIZE == True:
                image = image.resize((256,256))
            image.save(f"image{emoji_ext}")
        image.close()
        arq = discord.File(open(f"image{emoji_ext}",'rb'))
        a = await ctx.send(file=arq)
        link = a.attachments[0].url
        await a.delete()
        await m.edit(content="Imagem baixada :white_check_mark:")
        try:
            em = await ctx.guild.create_custom_emoji(name=emojiname.lower(),image=requests.get(link).content)
        except HTTPException:
            await ctx.send("Infelizmente não consegui adicionar o emoji, o emoji é **extremamente pesado**, mesmo tentando fazer a compressão do arquivo não consegui adicionar.")
            return
        await ctx.send(f"Emoji adicionado: {str(em)}!\n{warning}")

bot.add_cog(ServerManagement(bot))
bot.add_cog(Utils(bot))
bot.run(config["token"])