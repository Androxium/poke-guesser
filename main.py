import os
from numpy import uint8, arange, delete
from numpy.random import randint, choice
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
# from threading import Timer
# from throttler import throttle


POKEMON_URL = 'https://pokeapi.co/api/v2/pokemon/'
MAX_POKEDEX_INDEX = 898
SIGMA = 25

# global variables
pokemon_name = ''
generation = ''
types = []
hint_option = 0
has_been_revealed = False
size = 0
x_axis = {'min': -1, 'max': -1}
y_axis = {'min': -1, 'max': -1}
num_of_crops = 0
is_crop_mode = False
not_seen_pokemon = []


def reset_guessed_pokemon():
	global not_seen_pokemon

	not_seen_pokemon = arange(1, MAX_POKEDEX_INDEX+1)


def get_random_url():
	global not_seen_pokemon

	remaining_pokemon = len(not_seen_pokemon)
	if remaining_pokemon == 0:
		reset_guessed_pokemon()
	p_id_idx = randint(0,len(not_seen_pokemon))
	p_id = not_seen_pokemon[p_id_idx]
	not_seen_pokemon = delete(not_seen_pokemon, p_id_idx)
	random_url = POKEMON_URL + str(p_id)
	return random_url


def apply_gaussian_blur(image_url, name):
	# read and display original image
	image = skimage.io.imread(fname=image_url)
	skimage.io.imsave('pokemon.png', image)
	# apply Gaussian blur, creating a new image
	blurred = skimage.filters.gaussian(
	    image, sigma=(SIGMA, SIGMA), truncate=3.5, multichannel=True)
	skimage.io.imsave('whos-that-pokemon.png', blurred)


'''
	Returns the cartesian quadrant crop center is in
'''
def which_quadrant(center_x, center_y, x, y):
	if x >= center_x and y <= center_y:
		return 1
	elif x < center_x and y <= center_y:
		return 2
	elif x < center_x and y > center_y:
		return 3
	else:
		return 4


def update_samplable_image_regions(quadrant, x, y):
	global x_axis
	global y_axis
	global size

	if quadrant == 1:
		x_axis['max'] = x
		y_axis['min'] = y
	elif quadrant == 2:
		x_axis['min'] = x
		y_axis['min'] = y
	elif quadrant == 3:
		x_axis['min'] = x
		y_axis['max'] = y
	else:
		x_axis['max'] = x
		y_axis['max'] = y



def resample_crop_and_zoom():
	global size
	global x_axis
	global y_axis

	image = Image.open('pokemon.png')
	width, height = image.size
	x = randint(x_axis['min'], x_axis['max']+1)
	y = randint(y_axis['min'], y_axis['max']+1)
	quadrant = which_quadrant(width//2, height//2, x, y)

	update_samplable_image_regions(quadrant, x, y)
	cropped_image = image.crop((x-size, y-size, x+size, y+size))\
			.resize((width,height), Image.ANTIALIAS)
	cropped_image.save('whos-that-pokemon.png')


def apply_zoom_and_crop(image_url, name):
	global size
	global x_axis
	global y_axis
	global num_of_crops

	image = Image.open(requests.get(image_url, stream=True).raw)
	image.save('pokemon.png')

	width, height = image.size
	min_dimension = min(width, height)
	size = randint(min_dimension//12, min_dimension//9+1)
	x_axis = {'min': size, 'max': width-size}
	y_axis = {'min': size, 'max': height-size}
	num_of_crops = 0

	resample_crop_and_zoom()


def get_new_pokemon():
	global pokemon_name
	global generation
	global types
	global hint_option
	global has_been_revealed
	global is_crop_mode

	# make the get request to the pokeAPI
	random_url = get_random_url()
	r = requests.get(url = random_url)
	data = r.json()

	image_url = data['sprites']['other']['official-artwork']['front_default']
	name = data['name']

	print(name)

	hint_option = 0
	generation = data['game_indices'][0]['version']['name'] if len(data['game_indices']) > 0 else '???'
	pokemon_name = name.lower()
	has_been_revealed = False
	types.clear()
	for t in data['types']:
		types.append(t['type']['name'].title())
	

	action = choice([True, False])
	if action:
		is_crop_mode = True
		apply_zoom_and_crop(image_url, name)
	else:
		is_crop_mode = False
		apply_gaussian_blur(image_url, name)

	
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='?')
client = discord.Client()


@bot.event
async def on_ready():
	global not_seen_pokemon
	global MAX_POKEDEX_INDEX

	reset_guessed_pokemon()

	print(f'{bot.user.name} is connected')


@bot.command(name='reset')
async def reset_guessed(ctx):
	reset_guessed_pokemon()
	await ctx.send('{} reseting all guessed Pokemon'.format(ctx.message.author.mention))


@bot.command(name='again')
async def again(ctx):
	global num_of_crops
	global is_crop_mode

	if is_crop_mode:
		if num_of_crops < 3:
			num_of_crops += 1
			resample_crop_and_zoom()
			await ctx.send('{} here\'s another crop'.format(ctx.message.author.mention),\
				file=discord.File('whos-that-pokemon.png'))
		else:
			await ctx.send('{} no more!'\
				.format(ctx.message.author.mention))


@bot.command(name='hint')
async def hint(ctx):
	global hint_option

	if hint_option == 0:
		await ctx.send('{} this Pokemon first appeared in Pokemon {}'\
			.format(ctx.message.author.mention, generation.title()))
	elif hint_option == 1:
		await ctx.send('{} this Pokemon is a {} type'\
			.format(ctx.message.author.mention, ', '.join(types)))
	elif hint_option == 2:
		await ctx.send('{} the first letter is "{}"'\
			.format(ctx.message.author.mention, pokemon_name[0].title()))
	else:
		await ctx.send('{} no more hints!'\
			.format(ctx.message.author.mention))

	hint_option += 1


@bot.command(name='play')
async def play(ctx, *args):
	if len(args) > 0:
		await guess(ctx, args[0])
	elif has_been_revealed or not pokemon_name:
		get_new_pokemon()
		await ctx.send('Who\'s that Pokemon?', file=discord.File('whos-that-pokemon.png'))
	else:
		await ctx.send('{} guess the Pokemon first or reveal to move on'\
			.format(ctx.message.author.mention))


@bot.command(name='reveal')
async def reveal(ctx):
	# print(pokemon_name)
	global has_been_revealed
	has_been_revealed = True
	await ctx.send('It\'s {}!'.format(pokemon_name.title()),file=discord.File('pokemon.png'))


@bot.command(name='guess')
async def guess(ctx, arg):
	global has_been_revealed
	arg = arg.strip().lower()
	# print(arg + ", " + pokemon_name)
	if arg == pokemon_name:
		has_been_revealed = True
		await ctx.send('{} guessed right! It\'s {}!'\
			.format(ctx.message.author.mention, pokemon_name.title()),\
		 	file=discord.File('pokemon.png'))
	else:
		await ctx.send('{} nope, try again!'.format(ctx.message.author.mention))


bot.run(TOKEN)