import discord
from discord.ext import commands
import requests
import os
import re

intents = discord.Intents.default()
intents.message_content = True

TOKEN = os.getenv("TOKEN")
bot = commands.Bot(command_prefix="$", intents=intents, case_insensitive=True)

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

@bot.command()
async def stands(ctx, *, stand: str):
    try:
        search_url = "https://jojowiki.com/api.php"
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": stand,
            "format": "json"
        }
        search_res = requests.get(search_url, params=search_params)
        search_data = search_res.json()
        search_results = search_data.get("query", {}).get("search", [])

        if not search_results:
            await ctx.send(f"No hay información de ese stand: {stand}")
            return

        page_title = None
        snippet = ""
        for result in search_results:
            if stand.lower() in result["title"].lower():
                page_title = result["title"]
                snippet = result.get("snippet", "")
                break
        if not page_title:
            page_title = search_results[0]["title"]
            snippet = search_results[0].get("snippet", "")

        detail_params = {
            "action": "query",
            "prop": "extracts|pageimages",
            "exintro": True,
            "explaintext": True,
            "titles": page_title,
            "pithumbsize": 500,
            "format": "json"
        }
        detail_res = requests.get(search_url, params=detail_params)
        detail_data = detail_res.json()
        pages = detail_data.get("query", {}).get("pages", {})
        page = next(iter(pages.values()))

        titulo = page.get("title", "Desconocido")
        desc = page.get("extract", "")
        imagen = page.get("thumbnail", {}).get("source", None)
        
        url = f"https://jojowiki.com/wiki/{titulo.replace(' ', '_')}"

        if not desc or desc.strip() == "":
            snippet_clean = clean_html(snippet)
            if snippet_clean:
                embed = discord.Embed(
                    title=titulo,
                    description=f"{snippet_clean}\n\nConsulta el artículo aquí:\n{url}",
                    color=discord.Color.purple()
                )
            else:
                embed = discord.Embed(
                    title=titulo,
                    description=f"No se encontró descripción. Puedes consultar el artículo aquí:\n{url}",
                    color=discord.Color.purple()
                )
        else:
            embed = discord.Embed(
                title=titulo,
                description=desc,
                color=discord.Color.purple()
            )

        if imagen and "Logo" not in imagen:
            embed.set_image(url=imagen)

        await ctx.send(embed=embed)

    except Exception as e:
        print("Error: ", e)

@bot.event
async def on_ready():
    print(f"{bot.user}")

bot.run(TOKEN)