import os
from numpy import uint8
from numpy.random import random_integers, choice
# this import is for image cropping
from PIL import Image
# this import is for Gaussian blurring
import skimage.filters
import skimage.io
# from skimage.viewer import ImageViewer
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv


POKEMON_URL = 'https://pokeapi.co/api/v2/pokemon/'
MAX_POKEDEX_INDEX = 898
SIGMA = 25

pokemon_name = ""

def get_random_url():
	p_id = random_integers(1,MAX_POKEDEX_INDEX)
	random_url = POKEMON_URL + str(p_id)
	return random_url


def apply_gaussian_blur(image_url, name):
	# read and display original image
	image = skimage.io.imread(fname=image_url)
	skimage.io.imsave("pokemon.png", image)
	# apply Gaussian blur, creating a new image
	blurred = skimage.filters.gaussian(
	    image, sigma=(SIGMA, SIGMA), truncate=3.5, multichannel=True)
	skimage.io.imsave("whos-that-pokemon.png", blurred)


def apply_zoom_and_crop(image_url, name):
	image = Image.open(requests.get(image_url, stream=True).raw)
	image.save("pokemon.png")
	width, height = image.size
	center_x, center_y = width//2, height//2
	min_dimension = min(width, height)
	center_offset = random_integers(-min_dimension//4, min_dimension//4)
	center_x += center_offset
	center_y += center_offset
	size = random_integers(min_dimension//11, min_dimension//8)
	# top, left, right, bottom
	cropped_image = image.crop((center_x-size, center_y-size, center_x+size, center_y+size))\
			.resize((width,height), Image.ANTIALIAS)
	cropped_image.save("whos-that-pokemon.png")


def get_new_pokemon():
	global pokemon_name

	# make the get request to the pokeAPI
	random_url = get_random_url()
	r = requests.get(url = random_url)
	data = r.json()

	image_url = data['sprites']['other']['official-artwork']['front_default']
	name = data['name']
	pokemon_name = name.lower()
	print(pokemon_name)

	action = choice([True, False])
	if action:
		apply_zoom_and_crop(image_url, name)
	else:
		apply_gaussian_blur(image_url, name)

	
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='?')
client = discord.Client()


@bot.event
async def on_ready():
    # guild = discord.utils.get(client.guilds, name=GUILD)
    print(
        f'{bot.user.name} is connected'
    )


@bot.command(name='play')
async def play(ctx):
	get_new_pokemon()
	await ctx.send(file=discord.File('whos-that-pokemon.png'))


@bot.command(name='reveal')
async def reveal(ctx):
	print(pokemon_name)
	await ctx.send('It\'s {}!'.format(pokemon_name),file=discord.File('pokemon.png'))


@bot.command(name='guess')
async def guess(ctx, arg):
	arg = arg.strip().lower()
	print(arg + ", " + pokemon_name)
	if arg == pokemon_name:
		await ctx.send('You guessed right!', file=discord.File('pokemon.png'))
	else:
		await ctx.send('Nope, try again!')


bot.run(TOKEN)