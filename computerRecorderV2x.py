import pyautogui, sys
import pynput
from tkinter import *
from tkinter import Button as tk_Button
from pynput import mouse
from pynput.keyboard import Key, Listener
from pynput.mouse import Button, Controller
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.keyboard import Key
import threading
import Xlib.threaded
import time
import pandas
from tkinter import font
from datetime import datetime
from pathlib import Path
from ast import literal_eval
#import schedule
import speech_recognition #A lot of imports and dependencies. Only popular packages here that can be installed with pip. Ample docs online for these modules

L_SYS = []
STOPPER = True
SAVE_FILE = 'defaultRecordingName'
SAFE_MODE_ENABLED = False
CORNERS = ['CORNERS']

def checkTime():
	now = datetime.now()  
	current_time = now.strftime("%H:%M:%S.%f")[:-3] #straightforward function. I need the current time often
	return current_time
	
def getTimeStamp():
	now = datetime.now() #again, basically the same as checkTime(), just not formatted
	return now
	
def checkSTOPPER():
	global STOPPER #this might seem silly but I think it makes the code more readable. Plus I can't forget if this somehow fixed a bug
	return STOPPER


def onPress(key):
	global L_SYS
	if not checkSTOPPER(): #In the GUI you can hit 'Stop' in order to 
		return False #returning False to a pynput Listener kills the Listener thread
	L_SYS.append(['place','place',key,getTimeStamp(),True]) #here, it should append the time difference only #otherwise, we add to our rows of data. L_SYS stands for L system
	
def onRelease(key):
	global L_SYS
	if not checkSTOPPER():
		return False
	if key == Key.esc:
		print(L_SYS) #you could alter this print statement to return False, then pressing esc would kill your recording without you needing to click stop
	L_SYS.append(['place','place',key,getTimeStamp(),False]) #here we add a row with key events
		
def on_move(x, y):
	global L_SYS
	global STOPPER
	if not checkSTOPPER():
		return False
	L_SYS.append([x,y,'place',getTimeStamp(),'place']) #here we get cursor position, adding a row, not sure how to change the rate this updates at
	
def on_scroll(x,y,dx,dy):
	global L_SYS
	global STOPPER
	if not checkSTOPPER(): #this function is just grabbing scroll wheel data
		return False
	L_SYS.append([x,y,'place',getTimeStamp(),dy])

def on_click(x, y, button, pressed):
	global STOPPER #every time you press or release any mouse button including scroll wheel, after you've hit record and before you've hit stop, this function is called
	global L_SYS
	if not checkSTOPPER(): #checkSTOPPER will be True and will trigger this line if you've clicked the stop button
		return False #in which case, returning False kills the mouse Listener
	L_SYS.append([x,y,button,getTimeStamp(),pressed]) #otherwise, we append to L_SYS various information that will be useful in replaying our recorded events
	if not pressed:
		L_SYS.append([x,y,button,getTimeStamp(),pressed]) #realizing now this line probably creates a bug that I fixed elsewhere, in safer(). But the question is why did i include this line in the first place
	
def recordScript(process):
	if process == '0':
		checkMouse() #this function is clunky and unneccessary. But it works, and is readable
	elif process == '1':
		checkKeys()


def checkKeys():
	with Listener(on_press=onPress,on_release=onRelease) as listener: #creates a pynput keyboard Listener
		listener.join()
		
		
def checkMouse():
	with mouse.Listener(on_move=on_move,on_click=on_click,on_scroll=on_scroll) as listener: #creates a pynput mouse Listener
		listener.join()


def beginRecording():
	x = threading.Thread(target = recordScript, args=('0')).start() #this starts two threads, the first thread listens for mouse events 
	y = threading.Thread(target = recordScript, args=('1')).start() #this one listens for keyboard events
	
	
def checkBool(string):
	if string == 'True':
		return True
	elif string == 'False': #i dont think this does anything, ignore this, never called
		return False #some of these functions, I'm not sure if I ever use them. But I'll leave them here for now and figure it out later
	else:
		return string	
		
def checkClick(string):
	if string == 'Button.left':
		return MouseButton.left #i dont think this does anything, ignore this, never called
	elif string == 'Button.right':
		return MouseButton.right
		
def checkInt(string):
	try:
		int_obj = int(string) #i dont think this does anything, ignore this, never called
		return int_obj
	except:
		return string
		
def convert(string):
	try:
		string =  string.split(':')[0].replace('<','') #here we're just altering the pynput event object after its been saved in a csv file
	except:
		pass
	return string
	
def checkBut(entry):
	if len(entry) > 1:
		return eval(entry) #if the event is something like 'Button.left' for a left mouse click, this happens
	else:
		return entry #otherwise, the event must be a key press, which can simply be returned as 'j' or 'k'
		
def typeToInt(screen_dim):
	try:
		return(int(screen_dim)) #forget what this does but it probably fixed a bug
		
	except:
		return(screen_dim.item())

def replay(file_name):
	global APP #refer to the function'safeReplay()' below for documentation, these functions are similar
	screen_width = APP.winfo_screenwidth()
	screen_height = APP.winfo_screenheight()
	different_screen = False
	instruction_list = []
	df = pandas.read_csv(file_name)
	df_screen_width = df['X_loc'].iloc[0]
	df_screen_height = df['Y_loc'].iloc[0]
	df_screen_width = typeToInt(df_screen_width)
	df_screen_height = typeToInt(df_screen_height)
	width_ratio = float(screen_width)/float(df_screen_width)
	height_ratio = float(screen_height)/float(df_screen_height)
	if width_ratio != 1.0 or height_ratio != 1.0:
		different_screen = True
		print('Calculating different screen dimensions')
	instruction_list = df['INSTRUCTION'].to_list()  
	mouse = Controller()
	keyboard = KeyboardController()
	for row in instruction_list[2:]:
		row = literal_eval(row)
		print(row)
		try:
			if different_screen == True:
				mouse.position = int(round(width_ratio * float(row[0]))),int(round(height_ratio * float(row[1])))
			else:
				mouse.position = int(row[0]),int(row[1])
		except:
			pass
		if row[3] == 'True':
			try:
				print(eval(row[2]))
				mouse.press(eval(row[2]))
			except:
				print(row[2])
				keyboard.press(checkBut(row[2]))
		if row[3] == 'False':
			try:
				print(eval(row[2]))
				mouse.release(eval(row[2]))
			except:
				print(row[2])
				keyboard.release(checkBut(row[2]))
		try:
			dy = int(row[3])
			mouse.scroll(0,dy)  ##the scrolling part could be tested in an automated script. Get the scroll right until on a wikipedia page you get the same word copied and pasted twice
		except:
			pass
				
		
				
		time.sleep(row[-1])
		
def continuePrompt1(button_str): #ignore this, never called
	print("The following action is about to occur: " + str(button_str)) #this works, but makes replays innaccurate because you have to go into the command line and type
	go_str = input("Enter 'go' in order to proceed, or any other input to abort sequence: ")
	return go_str != 'go'
	
def continuePrompt(button_str):
	popup = Tk() #ignore this, never called
	button_str_label = Label(popup, text=button_str, font=('bold', 12))
	button_str_label.pack()
	instruction_label = Label(popup, text='Click continue to proceed with, or exit to abort the sequence', font=('bold', 8))
	instruction_label.pack()
	continue_btn = tk_Button(popup, text='Continue', width=12, command=lambda:setTrue(popup)) #ignore this, would be used to make GUI for SAFE_MODE_ENABLED if you don't want to use microphone
	continue_btn.pack()
	exit_btn = tk_Button(popup, text='Exit', width=12, command=lambda:setFalse(popup))
	exit_btn.pack()
	print('Click Continue or Exit')
	popup.mainloop()

	
def setFalse(popup):
	global CONTINUE_CHECK  #ignore this, never called
	popup.destroy()
	CONTINUE_CHECK = 'Exit'
	print('Exited')
	
def setTrue(popup):
	global CONTINUE_CHECK #ignore this, never called
	popup.destroy()
	CONTINUE_CHECK = 'Continue'
	print('Continuing')
	
def checkDecision(button_str):
	global CONTINUE_CHECK
	if CONTINUE_CHECK == 'Continue': #ignore this, never called
		return True
	elif CONTINUE_CHECK == 'Exit':
		return False
		
def popupMsg(row_list):
	global popup #we set the popup global so we can destroy the popup from the listenForCommand() function
	text_str = ', '.join(row_list)
	'''
	popup = Toplevel(APP)
	button_str_label = Label(popup, text=text_str, font=('bold', 12))
	button_str_label.pack()
	instruction_label = Label(popup, text='Say anything to continue, say nothing to abort sequence', font=('bold', 8))
	instruction_label.pack() #simple GUI that didn't work
	popup.after(5000, lambda: popup.destroy())
	popup.mainloop()
	'''
	popup = Tk()
	popup_label = Label(popup, text=row_list).pack() #here we display a Label that is a list of all the events about to occur
	pb = ttk.Progressbar(popup, length=200, mode='indeterminate') #this is a fail, doesn't update
	pb.pack()
	pb.start()   
	popup.update()
		
def listenForCommand(row_list):
	global popup #the continue prompt is a voice command. If it was GUI with buttons or keys, then the replay would be different from the recording
	popupMsg(row_list) #this message displays information about what button(s) is/are about to be pressed
	recognizer = speech_recognition.Recognizer() #creating this object to activate your mic
	popup.update() #this fails to update the loading bar. I'd like to see the loading bar move but it doesn't
	with speech_recognition.Microphone() as src:
		try:
			audio = recognizer.adjust_for_ambient_noise(src)
			print("Threshold Value After calibration:" + str(recognizer.energy_threshold))
			print("Please speak:")
			audio = recognizer.listen(src) #so now we're listening in using mic. The continue prompt does this because any key presses or mouse clicks defeat the purpose of replaying a recorded event sequence
			speech_to_txt = recognizer.recognize_google(audio).lower()
			print(speech_to_txt)
			if len(speech_to_txt)>0: #if you say anything at all and it is successfully recognized
				popup.withdraw() #the popup message closes
				return True #listenForCommand() returns True, which allows the replay to continue
		except Exception as ex:
			print("Sorry. Could not understand.") #if you say nothing, the popup closes and you exit the replay
			popup.withdraw() #this is a good safety feature because you might replay a friend's or stranger's event sequence 
			return False #listenForCommand() returns False, which ends the replay
			
		
		
def safeReplay(file_name):
	screen_width = APP.winfo_screenwidth() #this is the function called when you've toggled into safe mode and you hit replay
	screen_height = APP.winfo_screenheight() #first we load in your current screen dimensions
	different_screen = False
	instruction_list = []
	df = pandas.read_csv(file_name) #this is the file you selected for replay
	df_screen_width = df['X_loc'].iloc[0]
	df_screen_height = df['Y_loc'].iloc[0]
	df_screen_width = typeToInt(df_screen_width) #these are the screen dimensions read in from the loaded DataFrame you chose
	df_screen_height = typeToInt(df_screen_height)
	width_ratio = float(screen_width)/float(df_screen_width)
	height_ratio = float(screen_height)/float(df_screen_height)
	if width_ratio != 1.0 or height_ratio != 1.0:
		different_screen = True #now we check if the csv you're replaying has different screen dimensions
		print('Calculating different screen dimensions')
	instruction_list = df['INSTRUCTION'].to_list()  
	mouse = Controller() #here we're using pynput to create Controller() and KeyboardController() objects
	keyboard = KeyboardController()
	safe_instruction_list = []
	for row in instruction_list[2:-2]: #we need this here, check your csv to see why
		literal_row = literal_eval(row) #this turns the INSTRUCTION column string entry back into a list, because csv files can't denote something as a python list
		x = literal_row[0]
		y = literal_row[1] #loading in mouse coordinates
		if different_screen == True:
			try:
				x = int(round(width_ratio * float(row[0]))) #here, if the screen is different, we preprocess the INSTRUCTION column to fit your screen
				y = int(round(height_ratio * float(row[1])))
			except:
				pass
		else:
			try:
				x = int(x) #otherwise, we can just use the INSTRUCTION list as is
				y = int(y)
			except:
				pass
		btn = literal_row[2]
		boolean = literal_row[3]
		time_sleep = literal_row[4] #loading in various other values, all from the INSTRUCTION column of the DataFrame you selected
		safe_instruction_list.append([x,y,btn,boolean,time_sleep]) #now, another list of these rows but simply adjusted for your screen dimensions
	prompts = []
	for row in safe_instruction_list:
		info_list = safer(row,safe_instruction_list) #here we pass in the row and the list the row came from, this function will usually return that no prompt is needed
		prompts.append(info_list)
	for row in prompts:
		if row != ('no prompt') and (prompts[prompts.index(row)-1] == 'no prompt') : #but, if there's an upcoming event, then the function safer() returns all the information neccessary to trigger a prompt just before the event
			index = safe_instruction_list.index(row[0]) #above we check if the previous row == 'no prompt' because this solves a bug where prompts would be triggered consecutively
			safe_instruction_list.insert(index,row[1]) #here, importantly, we insert into our new instruction list our prompts. There should be as many prompts as there are events
		else:
			pass
	for row in safe_instruction_list:
		print(row)
	for row in safe_instruction_list:
		if row[0] == 'continue prompt': #so now, if our instruction list includes an event, the preceeding row will trigger this line True
			decision = listenForCommand(row[1]) #and now, we pass in a list of the buttons about to be pressed to this function, which will prompt the user to continue
			if decision == True:
				pass #the user makes a decision, to either continue
			elif decision == False:
				homeReset() #or, they can simply reset to home screen if they don't trust what button is about to be pressed
				print('Exiting')
				return None
				
		print('Proceeding to the next row')
		
		#if there's no continue prompt, we proceed below. If there was a continue prompt and the user prompted to continue, we proceed below
			
		
		if row[0] != 'continue prompt':	#if a row has no events, we can continue below and go about our business. Everything below is made to communicate with the pynput module
			try:
				mouse.position = row[0], row[1] #here we move the mouse
			except:
				pass
			if row[3] == 'True': #row[3] hold either True, False, or a placeholder. True means a button should be pressed, False a button released, and the placeholder means no buttons did anything
				try:
					mouse.press(eval(row[2]))
				except:
					keyboard.press(checkBut(row[2]))
			if row[3] == 'False':
				try:
					mouse.release(eval(row[2]))
				except:
					keyboard.release(checkBut(row[2]))
			try:
				dy = int(row[3])
				mouse.scroll(0,dy)  
			except:
				pass	
			time.sleep(row[-1]) #and here we sleep. This code where we communicate with the pynput module is present elsewhere in this script
		else:
			pass 

			

	
		
def safer(row,safe_instruction_list):
	if row[3] == 'True': #each row in the safe_instruction_list is passed through this functions, row[3] will be True when a prompt is needed, as in a button will be pressed or clicked
		button_press_list = []
		button_press_list.append(row[2]) #we know for sure the button in the same row as the True value will be pressed
		row_button = row[2]
		index = safe_instruction_list.index(row) #we get the index in the list using the entire row, which will almost surely not bug, but could potentially if the time's match up
		slice_safe_instruction_list = safe_instruction_list[index+1:] #now we look at the instruction list past the current event
		for slice_row in slice_safe_instruction_list:
			if slice_row[3] == 'place':
				pass
			elif slice_row[3] == 'False' and slice_row[2] == row_button: #here we are checking if there is another event before the current event is over, as in, ctrl-alt-delete, where ctrl is held down first and released last
				x = [row,['continue prompt',button_press_list]]
				return x #here we will always stop iterating once the first current event button is released, returning the row of the first button, a 'continue prompt' tag, and a list of all buttons pressed throughout this event
			elif slice_row[3] == 'True': #it is possible that before the first button pressed is released, another button will be pressed
				button_press_list.append(slice_row[2]) #this happens, for example, when typing an uppercase letter
		print('exited loop')
	else:
		return 'no prompt' #most of the time, there is no event in the row and we quickly return 'no prompt'



CONTINUE_CHECK = True	
def safeReplay1(file_name):
	global APP #you can ignore this function, its never called
	global CONTINUE_CHECK
	screen_width = APP.winfo_screenwidth()
	screen_height = APP.winfo_screenheight()
	different_screen = False
	instruction_list = []
	df = pandas.read_csv(file_name)
	df_screen_width = df['X_loc'].iloc[0]
	df_screen_height = df['Y_loc'].iloc[0]
	df_screen_width = typeToInt(df_screen_width)
	df_screen_height = typeToInt(df_screen_height)
	width_ratio = float(screen_width)/float(df_screen_width)
	height_ratio = float(screen_height)/float(df_screen_height)
	if width_ratio != 1.0 or height_ratio != 1.0:
		different_screen = True
		print('Calculating different screen dimensions')
	instruction_list = df['INSTRUCTION'].to_list()  
	mouse = Controller()
	keyboard = KeyboardController()
	for row in instruction_list[2:]:
		
		try:
			next_row = eval(instruction_list[instruction_list.index(row) + 1]) #this is just another way to figure out if a continue prompt should be shown
		except: #but its never called in the current build. Just here because its a way to forward reference your rows, which could be useful for auto speedup
			next_row = ['k','k','k','False']
			
		if next_row[3] == 'True':
			continuePrompt(next_row[2])
			decision = checkDecision(next_row[2])
			if not decision:
				return None

			
		row = literal_eval(row)
		print(row)
		try:
			if different_screen == True:
				mouse.position = int(round(width_ratio * float(row[0]))),int(round(height_ratio * float(row[1])))
			else:
				mouse.position = int(row[0]),int(row[1])
		except:
			pass
		if row[3] == 'True':
			try:
				print(eval(row[2]))
				mouse.press(eval(row[2]))
			except:
				print(row[2])
				keyboard.press(checkBut(row[2]))
		if row[3] == 'False':
			try:
				print(eval(row[2]))
				mouse.release(eval(row[2]))
			except:
				print(row[2])
				keyboard.release(checkBut(row[2]))
		try:
			dy = int(row[3])
			mouse.scroll(0,dy)  
		except:
			pass
				
		
				
		time.sleep(row[-1])
		
def toggleRecord(variable):
	global STOPPER
	global L_SYS #this function is called when you hit 'Record' on the home screen
	clearCanvas()
	TOP_BUTTON = tk_Button(CANVAS, text='STOP',  command=lambda: toggleRecord('1')) #now you just have one button, which can call this function again
	TOP_BUTTON.pack()
	if variable == '0':
		beginRecording() #this is what happens when you hit 'Record', you will end up with beginRecording()
	elif variable == '1':
		STOPPER = False #whereas, if you've hit 'Stop', you end up here. STOPPER will kill your pynput Listener threads
		enterFileName() #and now you can save your L_SYS (L system) into a csv file
		
def createINSTRUCTION(row):
	return [row['X_loc'],row['Y_loc'],transform(row['Event']),row['Mouse Drag'],row['Time Difference']] #this just creates an entry for a single column that is the entire row
		
def transform(event):
	event = event.split(':')[0].replace('<','').replace("'",'') #csv files convert everything to a string. Even a class object, the way a class object is printed in the terminal
	return event #this function fixes a bug where a saved event, when replayed, has those operators and type hinting

def saveLsys(save_file):
	global CANVAS
	global L_SYS
	global APP
	df = pandas.DataFrame(L_SYS,columns=['X_loc','Y_loc','Event','Time','Mouse Drag'])
	df['Time Difference'] = df['Time'] - df['Time'].shift(1) #we create a new column that is the 'Time' column subtracted from the 'Time' column shifted one row down
	df['Time Difference'] = df['Time Difference'].apply(lambda time_delta:time_delta.total_seconds()) #now we get the difference from the subtraction in a way that can easily be passed into time.sleep()
	df = df.loc[df['Time Difference']>.0001] #this line fixes a bug with button releases
	time_str = checkTime()
	df.to_csv(save_file + time_str + '.csv') #here we make a backup
	df = pandas.read_csv(save_file + time_str + '.csv')
	df['INSTRUCTION'] = df.apply(lambda row: createINSTRUCTION(row), axis = 1) #this is a new column for easier reading on replay
	screen_width = APP.winfo_screenwidth()
	screen_height = APP.winfo_screenheight() #we get current screen dimensions so your friends can replay your recording on their different screens
	screen_dim_df = pandas.DataFrame([[screen_width,screen_height,'this row','is to tell','screen dimension','ignore']], columns = ['X_loc','Y_loc','Event','Time','Mouse Drag','Time Difference']) #create a single row for the screen dimensions
	df = pandas.concat([screen_dim_df,df]) #each replay csv should always have screen dimensions as the first row
	del df['Unnamed: 0'] #pandas cleanup
	df.to_csv(save_file + time_str + '.csv') #and now we save it in a way that can't overwrite previous saves, but you still get to use a name you inputted
	homeReset() #saveLsys() is called after you enter your file name, so homeReset() saves you from hitting Home
	
def loadRecordings():
	global SAFE_MODE_ENABLED
	global APP
	clearCanvas()
	small_font = font.Font(size=5)
	instruction_select_label = Label(CANVAS, text='Select the file you want to replay', font=('bold', 12))
	instruction_select_label.pack()
	listbox = Listbox(CANVAS)
	listbox.config(width=60, height=3,font=small_font) #this function is called when you hit 'Replay' on the home screen
	listbox.pack()
	scrollbar = Scrollbar(CANVAS)  
	scrollbar.pack(side = RIGHT, fill = BOTH) 
	listbox.config(yscrollcommand = scrollbar.set) 
	scrollbar.config(command = listbox.yview) 
	findSaveFiles(listbox) #all csv files in your directory are loaded
	if SAFE_MODE_ENABLED: #now we check if you toggled safe mode in the menubar. Go to safe mode if you are replaying someone else's recording
		select_button = tk_Button(CANVAS, text='Replay Routine', width=30,height=1,font=('bold', 8), command=lambda: safeReplay(listbox.get(ANCHOR)))
		select_button.pack() #if you toggled safe mode, you get a safe replay of your selected csv file when you hit the button
	else:
		select_button = tk_Button(CANVAS, text='Replay Routine', width=30,height=1,font=('bold', 8), command=lambda: replay(listbox.get(ANCHOR)))
		select_button.pack() #if you didn't toggle safe mode, you get a fairly exact replay of the sequence you recorded. Fast, risky, especially if its not your recording youre replaying
	
def findSaveFiles(list_box):
	csv_s = [pth for pth in Path.cwd().iterdir() if pth.suffix == '.csv'] #finds all '.csv' files in the current directory
	for csv in csv_s:
		list_box.insert(END, str(csv).split('/')[-1]) #inserts these files to list_box
	
	
def enterFileName():
	global SAVE_FILE
	global CANVAS
	clearCanvas()
	project_name = StringVar()
	project_name_label = Label(CANVAS, text='Enter File Name', font=('bold', 12))
	project_name_label.pack()
	project_name_entry = Entry(CANVAS, textvariable=project_name)
	project_name_entry.pack() #after you stop a recording, you are prompted to enter a filename
	confirm_save_file_btn = tk_Button(CANVAS, text='Confirm Save File', width=12, command=lambda: saveLsys(project_name.get())) #you can save the file or just hit the home button to discard the recording
	confirm_save_file_btn.pack()

	

def homeReset():
	global CANVAS
	clearCanvas()
	TOP_BUTTON = tk_Button(CANVAS, text='RECORD',  command=lambda: toggleRecord('0')) #this can be a bit confusing. As soon as you hit record, your inputs are recorded
	TOP_BUTTON.pack()
	BOTTOM_BUTTON = tk_Button(CANVAS, text='Replay', command=loadRecordings) #this takes you to more UI
	BOTTOM_BUTTON.pack()
	FURTHER_BOTTOM_BUTTON = tk_Button(CANVAS, text='Scheduler', command=scheduleINSTRUCTION) #more UI on this press
	FURTHER_BOTTOM_BUTTON.pack()
	
def clearCanvas():
	global CANVAS
	CANVAS.destroy()
	CANVAS = Canvas(APP) #this is just a clear out button
	CANVAS.pack()
	
def scheduleINSTRUCTION():
	global CANVAS
	global APP
	clearCanvas()
	small_font = font.Font(size=5)
	instruction_select_label = Label(CANVAS, text='Select the file you want to schedule', font=('bold', 12))
	instruction_select_label.pack()
	listbox = Listbox(CANVAS)
	listbox.config(width=60, height=3,font=small_font)
	listbox.pack() #simple GUI
	scrollbar = Scrollbar(CANVAS)  
	scrollbar.pack(side = RIGHT, fill = BOTH) 
	listbox.config(yscrollcommand = scrollbar.set) 
	scrollbar.config(command = listbox.yview) 
	findSaveFiles(listbox)
	select_button = tk_Button(CANVAS, text='Schedule Routine', width=30,height=1,font=('bold', 8), command=lambda: schedulerScreen(listbox.get(ANCHOR))) #execution here
	select_button.pack()
	

	
def schedulerScreen(csv):
	global CANVAS
	clearCanvas()
	loop_time = StringVar()
	loop_time_label = Label(CANVAS, text='Enter Time in Seconds', font=('bold', 8))
	loop_time_label.pack()
	loop_time_entry = Entry(CANVAS, textvariable=loop_time)
	loop_time_entry.pack()
	
	loop_num = StringVar()
	loop_num_label = Label(CANVAS, text='Enter # of Loops', font=('bold', 8)) #simple GUI
	loop_num_label.pack()
	loop_num_entry = Entry(CANVAS, textvariable=loop_num)
	loop_num_entry.pack()
	confirm_loop_btn = tk_Button(CANVAS, text='Confirm Loop', width=12, command=lambda: job(csv,loop_time.get(),loop_num.get())) #execution here
	confirm_loop_btn.pack()
	
def job(csv, loop_time,num_loops):
	for loop in range(int(num_loops)): #this is just  a simple way to schedule replays, you can change the sleep time, number of loops, and what csv is replayed from the GUI
		replay(csv)
		time.sleep(int(loop_time))
		
def enableSafeMode():
	global SAFE_MODE_ENABLED
	if SAFE_MODE_ENABLED:
		SAFE_MODE_ENABLED = False #this function toggles SAFE_MODE_ENABLED when you press 'Safe' in the GUI
		print('SAFE_MODE FALSE') #the value of SAFE_MODE_ENABLED determines whether or not your replay includes continue prompts
	else:
		SAFE_MODE_ENABLED = True
		print('SAFE_MODE TRUE')
	
def loadEditScreen():
	global CANVAS
	clearCanvas()
	small_font = font.Font(size=5)
	instruction_select_label = Label(CANVAS, text='Select the file you want to edit', font=('bold', 12))
	instruction_select_label.pack()
	listbox = Listbox(CANVAS)
	listbox.config(width=60, height=3,font=small_font)
	listbox.pack() #some simple GUI here where you can select a file to be sped up on replay
	scrollbar = Scrollbar(CANVAS)  
	scrollbar.pack(side = RIGHT, fill = BOTH) 
	listbox.config(yscrollcommand = scrollbar.set) 
	scrollbar.config(command = listbox.yview) 
	findSaveFiles(listbox) #fills out the listbox
	select_button = tk_Button(CANVAS, text='Replay Routine', width=30,height=1,font=('bold', 8), command=lambda: replayEdit(listbox.get(ANCHOR))) #execution here
	select_button.pack()
	
def getCorners(x, y, button, pressed):
	global CORNERS
	if pressed == True:
		CORNERS.append(x)
		CORNERS.append(y)
	if pressed == False: #this function just gets x,y pixel coordinates when you click and drag with the mouse. That would be the screenshot box
		CORNERS.append(x)
		CORNERS.append(y)
		return False

def askForScreenshot():
	global CORNERS #the idea with this function is to ask for a screenshot region before each event in the recording. That way, on replay the program can screenshot that same
	CORNERS = [] #region, and check if the screenshot is the same as the screenshot you added as a label when asked for a screenshot. It's like wait for element in selenium
	print('Click and drag a box on the screen to indicate where to watch for updated pixels in order to trigger the next event')
	with mouse.Listener(on_move=None,on_click=getCorners,on_scroll=None) as listener:
		listener.join()
	return CORNERS
	
def replayEdit1(file_name):
	global APP
	screen_width = APP.winfo_screenwidth() #this function is irrelevant for the current build. But I'm hopeful that there are ways to auto speedup recordings on replay
	screen_height = APP.winfo_screenheight() #or at least, edit recordings. Like, if you want to speed up a segment you should be able to with a slider or dial or something
	different_screen = False
	instruction_list = []
	df = pandas.read_csv(file_name)
	df_screen_width = df['X_loc'].iloc[0]
	df_screen_height = df['Y_loc'].iloc[0]
	df_screen_width = typeToInt(df_screen_width)
	df_screen_height = typeToInt(df_screen_height)
	width_ratio = float(screen_width)/float(df_screen_width)
	height_ratio = float(screen_height)/float(df_screen_height)
	if width_ratio != 1.0 or height_ratio != 1.0:
		different_screen = True
		print('Calculating different screen dimensions')
	instruction_list = df['INSTRUCTION'].to_list()  
	mouse = Controller()
	keyboard = KeyboardController()
	fast_instruction_list = []
	for row in instruction_list[2:]:
		row = literal_eval(row)
		print(row)
		try:
			if different_screen == True:
				mouse.position = int(round(width_ratio * float(row[0]))),int(round(height_ratio * float(row[1])))
			else:
				mouse.position = int(row[0]),int(row[1])
		except:
			pass
		if row[3] == 'True':
			try:
				print(eval(row[2]))
				screenshot_coord = askForScreenshot()
				fast_instruction_list.append(screenshot_coord)
				fast_instruction_list.append(row)
				mouse.press(eval(row[2]))
			except:
				print(row[2])
				screenshot_coord = askForScreenshot()
				fast_instruction_list.append(screenshot_coord)
				fast_instruction_list.append(row)
				keyboard.press(checkBut(row[2]))
		if row[3] == 'False':
			try:
				print(eval(row[2]))# should save file name of screenshot 
				fast_instruction_list.append(row)
				mouse.release(eval(row[2]))
			except:
				print(row[2])
				fast_instruction_list.append(row)
				keyboard.release(checkBut(row[2]))
		try:
			dy = int(row[3])
			mouse.scroll(0,dy)  ##the scrolling part could be tested in an automated script. Get the scroll right until on a wikipedia page you get the same word copied and pasted twice
		except:
			pass
				
		
				
		time.sleep(row[-1])
		
	df = pandas.DataFrame(fast_instruction_list)
	df.to_csv(file_name + 'FAST.csv')
	homeReset()
	

def replayEdit(file_name):
	global APP
	screen_width = APP.winfo_screenwidth()
	screen_height = APP.winfo_screenheight()
	different_screen = False
	instruction_list = []
	df = pandas.read_csv(file_name)
	df = df[df['Mouse Drag'] != 'place'] #this is the key line here. We're essentially eliminating all non eventful rows. The idea is to automatically speed up your recordings
	df_screen_width = df['X_loc'].iloc[0] #while this is a simple way of doing that, refer to the askForScreenshot() and getCorners() functions for a more complex speedup
	df_screen_height = df['Y_loc'].iloc[0]
	df_screen_width = typeToInt(df_screen_width)
	df_screen_height = typeToInt(df_screen_height)
	width_ratio = float(screen_width)/float(df_screen_width)
	height_ratio = float(screen_height)/float(df_screen_height)
	if width_ratio != 1.0 or height_ratio != 1.0:
		different_screen = True
		print('Calculating different screen dimensions')
	instruction_list = df['INSTRUCTION'].to_list()  
	mouse = Controller()
	keyboard = KeyboardController()
	for row in instruction_list[2:]:
		row = literal_eval(row)
		print(row)
		try:
			if different_screen == True: #refer to replay and safeReplay() functions
				mouse.position = int(round(width_ratio * float(row[0]))),int(round(height_ratio * float(row[1]))) #this way is very slow if you have a different screen
			else:
				mouse.position = int(row[0]),int(row[1])
		except:
			pass
		if row[3] == 'True': #this will be True on any press
			try:
				print(eval(row[2]))
				mouse.press(eval(row[2])) #so we try mouse, for the button in row[2]
			except:
				print(row[2])
				keyboard.press(checkBut(row[2])) #if not mouse it must have been a keyboard press
		if row[3] == 'False': #row[3] will be 'False' on any release
			try:
				print(eval(row[2]))  
				mouse.release(eval(row[2])) #so first, we try the button on mouse. Eval is essential here because we need a class object, not a string as the parameter
			except:
				print(row[2])
				keyboard.release(checkBut(row[2])) #if the mouse release doesn't work, it must be a button release. This actually shouldn't work but it does because when you save to a csv
                                           #your pynput button objects get converted to strings
		try:
			dy = int(row[3])
			mouse.scroll(0,dy)  #scrolling is pretty broken. It'll work if you scroll all the way to a buffer or page limit. But it's not accurate enough to scroll wikipedia and copy and paste words
		except: #I used try and excepts because they're fast and readable
			pass
				
		time.sleep(row[-1]) #pages load at different rates, apps too. This sleeps for as long as you did during recording

global CANVAS
global APP
APP = Tk()
CANVAS = Canvas(APP)
CANVAS.pack()
APP.title('Computer Recorder') #nothing but basic GUI down here
APP.geometry('700x130')
MENUBAR = Menu(APP)
MENUBAR.add_command(label="Home", command=homeReset)
MENUBAR.add_command(label="Safe",command=enableSafeMode) #arent that many buttons but they all do something meaningful, safemode is relevant when the Replay GUI is loaded
MENUBAR.add_command(label="Edit",command=loadEditScreen)
APP.config(menu=MENUBAR)
homeReset()
APP.mainloop()

