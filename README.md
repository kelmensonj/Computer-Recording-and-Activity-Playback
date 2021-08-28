# Computer-Recording-and-Activity-Playback
You'll need some dependencies installed. I'm on the Hirsute Hippo update for Ubuntu, from the command line I did:

```
pip3 install pyautogui
pip3 install pynput
pip3 install pandas
pip3 install SpeechRecognition
```
Now you can run the script from the terminal. When you run the script, the box in the top left appears labelled 'Computer Recorder'. Here you can click 'Record':

![alt-text](https://github.com/kelmensonj/Computer-Recording-and-Activity-Playback/blob/main/gif_2.gif)

After naming your save file (or leave the name blank to name it with a timestamp), you can then click 'Replay' in order to replay your recording:

![alt-text](https://github.com/kelmensonj/Computer-Recording-and-Activity-Playback/blob/main/gif_1.gif)

This is a basic example, but more complex examples are on the way. I downloaded a couple hundred songs from Youtube Music and an MP3 Downloader site using this method. This application could be useful if you don't know how to code, but do know how to use a desktop computer interface. Drag and drop no code software is interesting and useful, but it has limited options. Furthermore, Computer Recording and Activity Playback leverages the universality of the mouse and keyboard interface. 

Also, the code might be a little confusing because I didn't use classes. I won't make that mistake again. But it's actually pretty straightforward. I used a combination of pyautogui and pynput in order to both record and replay a list of keyboard and mouse events, and then saved the list as a csv file. A lot of the code is just for edge cases and the gui. There's also a button 'SAFE' which, when clicked, will halt the replay and ask the user if the replay should continue or not using voice command. 

Another thing you can do with this application that I think is very cool is you can share recordings. The example in the gifs above shows me using Blender3D. It's a simple example, but these sorts of tutorial videos online can get pretty lengthy, hard to follow, and also take quite a bit of bandwidth to stream. If you check the saved csv file, you'll see that the first line or so includes the dimensions of your screen. So someone using Windows 10 can make a recording of a pretty complex scene, email the compressed csv file or post it online, and then I can grab the csv file and replay the recording on Ubuntu - and as long as I have Blender3D open at the start of the replay and they had Blender3D open at the start of the recording, that csv file becomes a faster, easier, and better way to share a tutorial. 

There's also a 'Schedule' button that could be used for automated email marketing, copy and pasting stock prices, or downloading images from google. I came up with Computer Recording and Actiivty Playback before I learned how to code, and now that I can I don't really need it - but I hope someone can find a use for it. And if not, well, at least I chose a name with a good acronym. 
