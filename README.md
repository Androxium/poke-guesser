# Poke-Guesser

This is a discord bot that will generate random images of Pokemon and players have to correctly guess the name of that Pokemon. This bot makes use of the pokeapi (check them out [here](https://pokeapi.co/)) to make GET requests to for the pokemon images.


## Dependencies

- [Python 3](https://www.python.org/downloads/)
- [numpy](https://numpy.org/install/)
- [Pillow](https://pypi.org/project/Pillow/)
- [skimage](https://scikit-image.org/docs/stable/install.html)
- [discord](https://pypi.org/project/discord.py/)
- [dotenv](https://pypi.org/project/python-dotenv/)

## Commands

?play -- generate a new Pokemon to guess\
?guess <your-guess> -- guess the Pokemon name, no spaces, use `-`\
?reveal -- reveals the Pokemon\
?hint -- get a hint for the Pokemon you're guessing (only a limited amount!)\
?again -- get another cropped image for cropped guesses (only a limited amount!)\
?reset -- resets all guessed Pokemon
