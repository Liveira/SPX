import asyncio
from io import BytesIO
from logging import exception
from ntpath import join
from typing import Type
import typing
import discord,pymongo,json,osuapi,requests,re,os,osuapi
from discord.errors import HTTPException
from discord.ext import tasks
from PIL import Image as img, ImageDraw
from PIL import ImageFont as imgfont
from PIL import ImageDraw as imgdraw
from PIL import ImageOps, ImageSequence
from discord.flags import Intents
from discord.ext.commands.errors import CommandInvokeError, CommandNotFound
from discord.ext import commands
import time,random
from mal import AnimeSearch
enc = open("config.json","r",encoding="utf-8")
config = json.load(enc)
osuapi.OsuApi(config["osu"],connector=osuapi.ReqConnector())


mongo = pymongo.MongoClient(config["mongo"])

osu = osuapi.OsuApi(config['osu'], connector=osuapi.ReqConnector())

avatar = [
    "https://cdn.discordapp.com/attachments/850535990102982696/850722579299303424/1f97a.png"
    ,"https://cdn.discordapp.com/attachments/850535990102982696/850722698359603220/1f640.png"
    ,"https://cdn.discordapp.com/attachments/850535990102982696/850719817484861450/1f631.png",
    "https://cdn.discordapp.com/attachments/850535990102982696/850742760301396028/1f60e.png",
    "https://cdn.discordapp.com/attachments/850535990102982696/850742778363510814/1f60f.png",
    "https://cdn.discordapp.com/attachments/850535990102982696/850742912534577162/1f62d.png",
    "https://cdn.discordapp.com/attachments/850535990102982696/850742943022186526/1f622.png",
    "https://cdn.discordapp.com/attachments/850535990102982696/850743044726849586/1f914.png",
    "https://cdn.discordapp.com/attachments/850535990102982696/850743075759194152/1f644.png"
]

SPX = mongo["Usuarios"]
SPXU = SPX["SPXUSERS"]
SPXS = SPX["SPXSERVERS"]
SPXB = SPX["SPXBL"]

avatarcont = 0

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
        SPXU.insert_one({"_id":user.id,'nome':user.name,'mar':0,'desc':'Eu sou uma pessoa misteriosa, mas eu posso mudar minha descri????o usando .desc','rep':0,"xp_time":0,'money':0,'gold':0,'inventory':{"Padr??o": {"name": "Padr??o","desc": "Background padr??o","tip": "BackGround Profile","use": True,"cont": 0,"onetime": True,"preview": "https://media.discordapp.net/attachments/776197504378732555/795800876383338496/default.png?width=642&height=459","tipte": "back-pf","author": "SPX Team"}},'profile':{'back-pf':{'url':'https://media.discordapp.net/attachments/776197504378732555/795800876383338496/default.png?width=642&height=459','name':"Padr??o"}}})

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

@tasks.loop(seconds=300)
async def change_avatar() -> None:
    global avatarcont
    if avatarcont == 0:
        avatarcont += 1
        return
    await bot.user.edit(avatar=requests.get(random.choice(avatar)).content)

async def send_stuff(file=None) -> discord.Message:
    return await bot.get_channel(850535990102982696).send(file=file)

@bot.event
async def on_ready() -> None:
    print("~~ SPX est?? ligado ~~" )
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
    change_avatar.start()

@bot.event
async def on_message(message: discord.Message) -> None:
    if message.content in [f"<@!{bot.user.id}>",f"<@{bot.user.id}>"]:
        await message.channel.send(f"Ol??! Voc?? me chamou? Use `{get_prefix(message.guild.id)}help` para saber meus comandos!")
    await bot.process_commands(message)

class Utilidade(commands.Cog):
    
    @commands.command(name='help', description="Comando de ajuda",aliases=["ajuda","h","a","ajd","ajudinhaae"], help="Exemplos:\n\nMostra uma ajuda completa do comando selecionado\n`!!help ping`")
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
                embed = discord.Embed(title=f'{command.name.title()} \ {command.cog_name}',description=command.description if command.description != '' or command.description != None else "Esse comando n??o tem nenhuma descri????o :/")
                embed.color = p
                embed.add_field(name='Como usar?',value=f'{command.help.replace("!!",get_prefix(ctx.guild.id)) if command.help != None else "Esse comando n??o tem ajuda..."}')
                embed.add_field(name='Alternativas',value=', '.join(command.aliases) if command.aliases != None or command.aliases != [] else "Esse comando n??o tem alternativas")
                embed.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.send(embed=embed) 
            except Exception as ex:
                await ctx.send(f"**:warning: | O comando n??o existe...**  {ex.args}")

    @commands.command(name="avatar", description="Veja o seu avatar ou o do seus amigos",aliases=['av','pfp'],help='Exemplos:\n\nVeja o avatar de uma pessoa\n`!!avatar @darky#0000`')
    @commands.cooldown(1,5,commands.BucketType.user)
    @blacklist()
    async def avatar(self,ctx:commands.Context,user:discord.User=None) -> None:
        user = user or ctx.author
        embed = discord.Embed(title=f'Avatar de {user.name}',description=f"Link: [Avatar Link]({user.avatar_url})")
        embed.set_image(url=user.avatar_url)
        embed.colour = p
        await ctx.send(embed=embed)

    @commands.command(name="ping", description="Veja a latencia do bot, caso esteja lento em seus comandos.",aliases=['pong','<@!660193448711946262>','<@660193448711946262>',"latency","latencia"],help="Exemplos:\n\nVeja a latencia do bot caso ele esteja demorando para responder algum comando\n`!!ping`\n\n!Aviso! Caso o ping esteja alto, voc?? pode avisar a n??s no nosso servidor de suporte!")
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
        await a.edit(content=f":ping_pong: | **Latencia da API: {int(bot.latency * 1000)}ms**\n????????????-> **Latencia do BOT: {int(ping)}ms**\n????????????-> **Latencia do Banco de dados: {int(ping_db)}ms**\n{status}")
  
    @commands.command(name="wheater", description="Veja o clima da sua cidade",aliases=["clima","temperatura","temp","tempo"],help="Exemplos:\n\nVeja o clima da sua cidade\n`!!wheater <nome da cidade>`")
    @commands.cooldown(1,5,commands.BucketType.user)
    @blacklist()
    async def weather(self,ctx:commands.Context,*,cidade) -> None:
        req = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={cidade.replace(' ','%20')}&appid={config['wheater']}&units=metric")
        if req.status_code != 200:
            await ctx.send("Aconteceu um erro no REQUEST! Pode ter sido que voc?? colocou o nome errado")
            return
        data = req.json()
        embed=discord.Embed(title=f'Temperatura de {cidade}')
        embed.color = p
        embed.set_thumbnail(url=f'https://openweathermap.org/img/wn/{data["weather"][0]["icon"]}@2x.png')
        embed.add_field(name='Temperatura',value=f"{round(data['main']['temp'])}??C")
        embed.add_field(name='Sensa????o T??rmica',value=f"{round(data['main']['feels_like'])}??C")
        await ctx.send(embed=embed)
        
    @commands.command(name="recanime", description="Deixe o bot recomendar um anime para voc??!",aliases=['recomendar_anime','ranime'],help=f"Exemplos:\n\nDeixe o bot recomendar um anime para voc??!\n`!!recanime`")
    @commands.cooldown(1,5,commands.BucketType.user)
    @blacklist()
    async def recanime(self,ctx):
        m = await ctx.send("Pesquisando... :mag_right:")
        url = "https://animechan.vercel.app/api/random"
        json = requests.get(url).json()
        a = AnimeSearch(json["anime"])
        anime = a.results[0]
        embed = discord.Embed(title=json["anime"],description=f"{anime.synopsis} Quer saber mais? [Clique aqui!]({anime.url})")
        embed.set_thumbnail(url=anime.image_url)
        embed.color = p
        embed.set_footer(text="Quer mais informa????es? Reaja ???")
        await m.edit(content="Pronto!... ",embed=embed)
        await m.add_reaction("???")
        def checkr(reaction,user):
            return user == ctx.message.author and reaction.emoji == "???" and ctx.channel == reaction.message.channel
        try:
            reac,user = await bot.wait_for('reaction_add',check=checkr,timeout=60)
            embed.add_field(name="Avalia????o",value=f"{anime.score} :star:")
            embed.add_field(name="Numero de episodios",value=f"{anime.episodes}")
            embed.add_field(name="Tipo do anime",value=f"{anime.type}")
            embed.set_footer(text=f"")
            await m.edit(embed=embed)
            await m.clear_reactions()
        except asyncio.TimeoutError:
            await m.clear_reactions()

    @commands.command(name="osu", description="Veja informa????es do seu perfil no osu", help="Exemplos\n\nVeja informa????es do seu perfil no osu\n`!!osu Darky`")
    @commands.cooldown(1,5,commands.BucketType.user)
    @blacklist()
    async def osu(self,ctx,*,user):
        try:
            user = osu.get_user(user)[0]
            embed = discord.Embed(title=user.username) 
            embed.add_field(name='Perfomance/Ranking',value=f"PP: **{round(user.pp_raw)}**\nRanking: #**{user.pp_rank}** || Pa??s: #**{user.pp_country_rank}**\nPrecis??o: **{int(user.accuracy)}%**\nTotal de partidas: **{user.playcount}** (LV{int(user.level)})\nTempo de jogo: {user.total_seconds_played // 3600 // 24} Dias {user.total_seconds_played // 3600 % 24} Horas (Total de {user.total_seconds_played // 3600} Horas)")
            embed.add_field(name='Contagem de Rankings',value=f"\n<:SSH:851124299791859772> {user.count_rank_ssh}\n<:SS:851124299574149202> {user.count_rank_ss}\n<:SH:851124299817549855> {user.count_rank_sh}\n<:rankingS:851124299653447710> {user.count_rank_s}\n<:rankingA:851124299535614013> {user.count_rank_a}")
            try:
                best = osu.get_user_best(user,limit=5)
                a = ""
                cont = 0
                for i in best:
                    cont += 1
                    beat = osu.get_beatmaps(beatmap_id=i.beatmap_id,limit=1)[0]
                    a += f"{cont}. {beat.title}\n**{round(i.pp)}**PP | Mods: +{i.enabled_mods.shortname if i.enabled_mods.shortname != '' else 'NM'}\n\n"
                embed.add_field(name='Melhores Pontua????es',value=a,inline=False)
            except:
                embed.add_field(name='Melhores Pontua????es',value="Algum erro aconteceu e n??o consegui carregar a pontua????o.",inline=False)
            embed.color = p
            embed.set_thumbnail(url=user.profile_image)
            await ctx.send(embed=embed)
        except: 
                await ctx.send("N??o consegui encontrar o seu perfil")
                return
class ServerManagement(commands.Cog):

    @commands.command(name="addemoji", description="Adicione um emoji no servidor f??cil!",aliases=['aemoji','adicionar_emoji'],help=f"Exemplos:\n\nAdicionar um emoji com uma imagem:\n`!!addemoji flushed <arquivo>`\n\nAdicionar um emoji com um emoji de outro servidor (Precisa de nitro):\n`!!addemoji flushed :ultraflushed:`\n\nAdicionar um emoji com a foto de perfil de algu??m:\n`!!addemoji burro @darky#0000`\n\nAdicionar um emoji com um link:\n`!!addemoji algo https:://coisas/imagem.png`\n\nFormatos aceitados: [PNG/JPEG/JPG/WEBM/GIF]")
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
            image.save(f"temp/image{emoji_ext}",
                    save_all=True,
                    append_images=list(frames),
                    loop=0
            )
        else:
            if RESIZE == True:
                image = image.resize((256,256))
            image.save(f"temp/image{emoji_ext}")
        image.close()
        arq = discord.File(open(f"temp/image{emoji_ext}",'rb'))
        a = await send_stuff(arq)
        link = a.attachments[0].url
        
        await m.edit(content="Imagem baixada :white_check_mark:")
        try:
            em = await ctx.guild.create_custom_emoji(name=emojiname.lower(),image=requests.get(link).content)
        except HTTPException:
            await ctx.send("Infelizmente n??o consegui adicionar o emoji, o emoji ?? **extremamente pesado**, mesmo tentando fazer a compress??o do arquivo n??o consegui adicionar.")
            return
        await ctx.send(f"Emoji adicionado: {str(em)}!\n{warning}")
        os.remove(f"temp/image{emoji_ext}")


    

bot.add_cog(ServerManagement(bot))
bot.add_cog(Utilidade(bot))
bot.run(config["token"])