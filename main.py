from numpy.random import random_integers
# this import is for image cropping
from PIL import Image
# this import is for Gaussian blurring
import skimage
# from skimage.viewer import ImageViewer
import requests
# from io import BytesIO

POKEMON_URL = 'https://pokeapi.co/api/v2/pokemon/'
MAX_POKEDEX_INDEX = 898
SIGMA = 25

def get_random_url():
	p_id = random_integers(1,MAX_POKEDEX_INDEX)
	random_url = POKEMON_URL + str(p_id)
	return random_url

# make the get request to the pokeAPI
random_url = get_random_url()
r = requests.get(url = random_url)
data = r.json()

image_url = data['sprites']['other']['official-artwork']['front_default']
name = data['name']

def apply_gaussian_blur(image_url, name):
	# read and display original image
	image = skimage.io.imread(fname=image_url)
	# apply Gaussian blur, creating a new image
	blurred = skimage.filters.gaussian(
	    image, sigma=(SIGMA, SIGMA), truncate=3.5, multichannel=True)
	# # display blurred image
	# viewer = ImageViewer(blurred)
	# viewer.show()
	skimage.io.imsave("test-image.png", blurred)


def apply_zoom_and_crop(image_url, name):
	image = Image.open(requests.get(image_url, stream=True).raw)
	image.save(name + "-og-image.png")
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
	cropped_image.save(name + "-cropped.png")

apply_zoom_and_crop(image_url, name)