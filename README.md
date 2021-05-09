# pi-snake
Crappy snake game in python for 32x8 neopixel array. It now actually works, and is surprisingly diverting to play.

# Hardware

* Pi zero
* Pair of push-switches between pins 17 and 27 and ground for inputs
* neopixel array with the data line hooked up to pin 18
* Things installed as per imports.
* Python3
* Root access

# Known issues

* It's possible for a treat to appear inside a snake.
* Only works for a single player.
* There appears to be an obscure bug with snake reverses such that if the head is located in the last position the tail was in before consuming the treat, something goes quite wrong and the snake can end up with a junction in it - it looks like there's a bug in the collision detection mechanic.

# TODO

* Fix known issues
* Add 2-player mode
