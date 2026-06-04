# CS416P-Aleatoric
Heidi Green   
## aleatoric.py   
Generates a random song and performs it using sawtooth wave synthesis. To be aleatoric, the song structure, chord loops, key, and tempo are all randomly chosen. There are 3 options for song structure, 10 possible chord loops, the range for key is A3-A4 inclusively, and the range for tempo is between 80-160 beats per minute. The melody is built from eighth notes. Chord tones are selected with a 0.8 probability and major scale tones for the other 20%. Adding harmony and drums are other optional choices. The performance is played on the computer directly, unless an output filename is specified using --output FILENAME.wav. In that case, the performance is saved as a 48000sps mono 16-bit WAV file.

## Build Instructions/Setup:   
**The following libraries need to be installed:**   
sounddevice   
numpy   
scipy      
**Can be done by the following command:**   
pip install -r requirements.txt   

## Running:   
**The script can be run directly from your terminal with the following command:**   
python aleatoric.py  

**To specify a filename for the output:**   
python aleatoric.py --output FILENAME.wav    

**Command line option for adding drums:**   
python aleatoric.py --drums    

**Command line option for adding harmony:**   
python aleatoric.py --harmony  

**For command line argument options and usage:**   
python aleatoric.py --help

# Reflection   
**What I Did:**   
I created a program that creates music based on the concept of aleatoric composition and either performs it directly or writes it to an output file. I implemented additional options for adding harmony, drums, or both, to the output as well.

**How It Went:**    
Overall, the process went well. It was a little challenging to design for expanding here, just because I had never made something like this before. That being said, I really enjoyed experimenting with different things within the program and being able to hear the effect on the generated music.

**What's Still to be Done:**   
There is definitely still room to expand this program. Adding options for using bass and rhythm could make the generated music sound better. Then the next step from there would be to make the program act as a MIDI controller. Additionally, adding an official argparse would also make the program more complete.