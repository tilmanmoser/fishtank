# Fish Tank

An aquarium application that imports self-painted fish from photo or webcam and animates them in a swarm that follows the rules of the [flocking boids algorithm](https://en.wikipedia.org/wiki/Boids). Image recognition was implemented with [opencv](https://opencv.org) and [aruco markers](https://en.wikipedia.org/wiki/ARTag).


# Installation

```
brew install ffmpeg
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

# Run

```
source .venv/bin/activate
python main.py
```

# Key bindings

- `c`: Capture drawing from webcam
- `f`: Feed fishes
- `m`: Mute/Unmute
- `w`, `a`, `s`, `d`: Move submarine

# Adding fishes to the fish tank

You can print out [temaplates](data/images/fishes/print/) and colorize them as you like. 

To import your drawings into the fish tank, make sure the programm is running and then
- place a photo of your drawing (jpg or png) into [data/inbound](data/inbound/) or
- press `c` to use the computer's camera for import



# Licence(s)

**Software / Source Code**

Copyright 2024, Tilman Moser

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

**Resources**

[Video](https://pixabay.com/de/videos/ozean-meer-unterwasser-aquarium-105322/) by KiFoKu

[Audio](https://pixabay.com/de/sound-effects/aquarium-ambience-sounds-10-min-193236/) by GioeleFazzeri

[Fishes](data/images/fishes) from [https://freesvg.org/](https://freesvg.org/) (CC0)
