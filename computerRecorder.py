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
import schedule
import speech_recognition


L_SYS = []
STOPPER = True
SAVE_FILE = 'defaultRecordingName'
SAFE_MODE_ENABLED = False
CORNERS = ['CORNERS']

#and finally, a share routine, which contains a screenshot of the beginning screen as well as the instructions to be fed
#after database rework, I want to add the screenshotting and have that appear when you select your file before you hit replay, and then also a safe mode
def checkTime():
	now = datetime.now()  
	current_time = now.strftime("%H:%M:%S.%f")[:-3]
	return current_time
	
def getTimeStamp():
	now = datetime.now()
	return now
	
def checkSTOPPER():
	global STOPPER
	return STOPPER


def onPress(key):
	global L_SYS
	if not checkSTOPPER():
		return False
	L_SYS.append(['place','place',key,getTimeStamp(),True]) #here, it should append the time difference only
	
def onRelease(key):
	global L_SYS
	if not checkSTOPPER():
		return False
	if key == Key.esc:
		print(L_SYS)
	L_SYS.append(['place','place',key,getTimeStamp(),False])
		
def on_move(x, y):
	global L_SYS
	global STOPPER
	if not checkSTOPPER():
		return False
	L_SYS.append([x,y,'place',getTimeStamp(),'place'])
	
def on_scroll(x,y,dx,dy):
	global L_SYS
	global STOPPER
	if not checkSTOPPER():
		return False
	L_SYS.append([x,y,'place',getTimeStamp(),dy])

def on_click(x, y, button, pressed):
	global STOPPER
	global L_SYS
	if not checkSTOPPER():
		return False
	L_SYS.append([x,y,button,getTimeStamp(),pressed]) #replace 'place' here with button, and find a solution for the Button.click problem here and two lines below, need right click
	if not pressed:
		L_SYS.append([x,y,button,getTimeStamp(),pressed])
	
def recordScript(process):
	if process == '0':
		checkMouse()
	elif process == '1':
		checkKeys()


def checkKeys():
	with Listener(on_press=onPress,on_release=onRelease) as listener:
		listener.join()
		
		
def checkMouse():
	with mouse.Listener(on_move=on_move,on_click=on_click,on_scroll=on_scroll) as listener:
		listener.join()


def beginRecording():
	x = threading.Thread(target = recordScript, args=('0')).start()
	y = threading.Thread(target = recordScript, args=('1')).start()
	
	
def checkBool(string):
	if string == 'True':
		return True
	elif string == 'False':
		return False
	else:
		return string	
		
def checkClick(string):
	if string == 'Button.left':
		return MouseButton.left
	elif string == 'Button.right':
		return MouseButton.right
		
def checkInt(string):
	try:
		int_obj = int(string)
		return int_obj
	except:
		return string
		
def convert(string):
	try:
		string =  string.split(':')[0].replace('<','')
	except:
		pass
	return string
	
def checkBut(entry):
	if len(entry) > 1:
		return eval(entry)
	else:
		return entry
		
def typeToInt(screen_dim):
	try:
		return(int(screen_dim))
		
	except:
		return(screen_dim.item())

def replay(file_name):
	global APP
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
		
def continuePrompt1(button_str):
	print("The following action is about to occur: " + str(button_str))
	go_str = input("Enter 'go' in order to proceed, or any other input to abort sequence: ")
	return go_str != 'go'
	
def continuePrompt(button_str):
	popup = Tk()
	button_str_label = Label(popup, text=button_str, font=('bold', 12))
	button_str_label.pack()
	instruction_label = Label(popup, text='Click continue to proceed with, or exit to abort the sequence', font=('bold', 8))
	instruction_label.pack()
	continue_btn = tk_Button(popup, text='Continue', width=12, command=lambda:setTrue(popup))
	continue_btn.pack()
	exit_btn = tk_Button(popup, text='Exit', width=12, command=lambda:setFalse(popup))
	exit_btn.pack()
	print('Click Continue or Exit')
	popup.mainloop()

	
def setFalse(popup):
	global CONTINUE_CHECK 
	popup.destroy()
	CONTINUE_CHECK = 'Exit'
	print('Exited')
	
def setTrue(popup):
	global CONTINUE_CHECK
	popup.destroy()
	CONTINUE_CHECK = 'Continue'
	print('Continuing')
	
def checkDecision(button_str):
	global CONTINUE_CHECK
	if CONTINUE_CHECK == 'Continue':
		return True
	elif CONTINUE_CHECK == 'Exit':
		return False
		
def popupMsg(row_list):
	global popup
	text_str = ', '.join(row_list)
	'''
	popup = Toplevel(APP)
	button_str_label = Label(popup, text=text_str, font=('bold', 12))
	button_str_label.pack()
	instruction_label = Label(popup, text='Say anything to continue, say nothing to abort sequence', font=('bold', 8))
	instruction_label.pack()
	popup.after(5000, lambda: popup.destroy())
	popup.mainloop()
	'''
	popup = Tk()
	popup_label = Label(popup, text=row_list).pack()
	pb = ttk.Progressbar(popup, length=200, mode='indeterminate')
	pb.pack()
	pb.start()   
	popup.update()
		
def listenForCommand(row_list):
	global popup
	popupMsg(row_list)
	recognizer = speech_recognition.Recognizer()
	popup.update()
	with speech_recognition.Microphone() as src:
		try:
			audio = recognizer.adjust_for_ambient_noise(src)
			print("Threshold Value After calibration:" + str(recognizer.energy_threshold))
			print("Please speak:")
			audio = recognizer.listen(src)
			speech_to_txt = recognizer.recognize_google(audio).lower()
			print(speech_to_txt)
			if len(speech_to_txt)>0:
				popup.withdraw()
				return True
		except Exception as ex:
			print("Sorry. Could not understand.")
			popup.withdraw()
			return False
			
		
		
def safeReplay(file_name):
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
	safe_instruction_list = []
	for row in instruction_list[2:-2]:
		literal_row = literal_eval(row)
		x = literal_row[0]
		y = literal_row[1]
		if different_screen == True:
			try:
				x = int(round(width_ratio * float(row[0])))
				y = int(round(height_ratio * float(row[1])))
			except:
				pass
		else:
			try:
				x = int(x)
				y = int(y)
			except:
				pass
		btn = literal_row[2]
		boolean = literal_row[3]
		time_sleep = literal_row[4]
		safe_instruction_list.append([x,y,btn,boolean,time_sleep])
	prompts = []
	for row in safe_instruction_list:
		info_list = safer(row,safe_instruction_list)
		prompts.append(info_list)
	for row in prompts:
		if row != ('no prompt') and (prompts[prompts.index(row)-1] == 'no prompt') :
			index = safe_instruction_list.index(row[0])
			safe_instruction_list.insert(index,row[1])
		else:
			pass
	for row in safe_instruction_list:
		print(row)
	for row in safe_instruction_list:
		if row[0] == 'continue prompt':
			decision = listenForCommand(row[1])
			if decision == True:
				pass
			elif decision == False:
				homeReset()
				print('Exiting')
				return None
				
		print('Proceeding to the next row')
		
		
			
		
		if row[0] != 'continue prompt':	
			try:
				mouse.position = row[0], row[1]
			except:
				pass
			if row[3] == 'True':
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
			time.sleep(row[-1])
		else:
			pass #go back to line 326

			

	
		
def safer(row,safe_instruction_list):
	if row[3] == 'True':
		button_press_list = []
		button_press_list.append(row[2])
		row_button = row[2]
		index = safe_instruction_list.index(row)
		slice_safe_instruction_list = safe_instruction_list[index+1:]
		for slice_row in slice_safe_instruction_list:
			if slice_row[3] == 'place':
				pass
			elif slice_row[3] == 'False' and slice_row[2] == row_button:
				x = [row,['continue prompt',button_press_list]]
				return x
			elif slice_row[3] == 'True':
				button_press_list.append(slice_row[2])
		print('exited loop')
	else:
		return 'no prompt'


			
					 

		
		
		
	
CONTINUE_CHECK = True	
def safeReplay1(file_name):
	global APP
	global CONTINUE_CHECK
	screen_width = APP.winfo_screenwidth()
	screen_height = APP.winfo_screenheight()
	different_screen = False
	instruction_list = []
	df = pandas.read_csv(file_name)
	df_screen_width = df['X_loc'].iloc[0]
	df_screen_height = df['Y_loc'].iloc[0]
	df_screen_width = typeToInt(df_screen_width)
	df_screen_height = typeToInt(df_screen_height)#up here i should process instruction list, and adjust values if neccessary, and make sure there's always a mouse position
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
			next_row = eval(instruction_list[instruction_list.index(row) + 1])
		except:
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
			mouse.scroll(0,dy)  ##the scrolling part could be tested in an automated script. Get the scroll right until on a wikipedia page you get the same word copied and pasted twice
		except:
			pass
				
		
				
		time.sleep(row[-1])
		
def toggleRecord(variable):
	global STOPPER
	global L_SYS
	clearCanvas()
	TOP_BUTTON = tk_Button(CANVAS, text='STOP',  command=lambda: toggleRecord('1'))
	TOP_BUTTON.pack()
	if variable == '0':
		beginRecording()
	elif variable == '1':
		STOPPER = False
		enterFileName()
		
def createINSTRUCTION(row):
	return [row['X_loc'],row['Y_loc'],transform(row['Event']),row['Mouse Drag'],row['Time Difference']]
		
def transform(event):
	event = event.split(':')[0].replace('<','').replace("'",'')
	return event

#add function tied to button so you can optionally record your screen
def saveLsys(save_file):
	global CANVAS
	global L_SYS
	global APP
	df = pandas.DataFrame(L_SYS,columns=['X_loc','Y_loc','Event','Time','Mouse Drag'])
	df['Time Difference'] = df['Time'] - df['Time'].shift(1)
	df['Time Difference'] = df['Time Difference'].apply(lambda time_delta:time_delta.total_seconds())
	df = df.loc[df['Time Difference']>.0001]
	time_str = checkTime()
	df.to_csv(save_file + time_str + '.csv')
	df = pandas.read_csv(save_file + time_str + '.csv')
	df['INSTRUCTION'] = df.apply(lambda row: createINSTRUCTION(row), axis = 1)
	screen_width = APP.winfo_screenwidth()
	screen_height = APP.winfo_screenheight()
	screen_dim_df = pandas.DataFrame([[screen_width,screen_height,'this row','is to tell','screen dimension','ignore']], columns = ['X_loc','Y_loc','Event','Time','Mouse Drag','Time Difference'])
	df = pandas.concat([screen_dim_df,df])
	del df['Unnamed: 0']
	df.to_csv(save_file + time_str + '.csv')
	homeReset()
	
def loadRecordings():
	global SAFE_MODE_ENABLED
	global APP
	clearCanvas()
	small_font = font.Font(size=5)
	instruction_select_label = Label(CANVAS, text='Select the file you want to replay', font=('bold', 12))
	instruction_select_label.pack()
	listbox = Listbox(CANVAS)
	listbox.config(width=60, height=3,font=small_font)
	listbox.pack()
	scrollbar = Scrollbar(CANVAS)  
	scrollbar.pack(side = RIGHT, fill = BOTH) 
	listbox.config(yscrollcommand = scrollbar.set) 
	scrollbar.config(command = listbox.yview) 
	findSaveFiles(listbox)
	if SAFE_MODE_ENABLED:
		select_button = tk_Button(CANVAS, text='Replay Routine', width=30,height=1,font=('bold', 8), command=lambda: safeReplay(listbox.get(ANCHOR)))
		select_button.pack()
	else:
		select_button = tk_Button(CANVAS, text='Replay Routine', width=30,height=1,font=('bold', 8), command=lambda: replay(listbox.get(ANCHOR)))
		select_button.pack()
	
def findSaveFiles(list_box):
	csv_s = [pth for pth in Path.cwd().iterdir() if pth.suffix == '.csv']
	for csv in csv_s:
		list_box.insert(END, str(csv).split('/')[-1])
	
	
def enterFileName():
	global SAVE_FILE
	global CANVAS
	clearCanvas()
	project_name = StringVar()
	project_name_label = Label(CANVAS, text='Enter File Name', font=('bold', 12))
	project_name_label.pack()
	project_name_entry = Entry(CANVAS, textvariable=project_name)
	project_name_entry.pack()
	confirm_save_file_btn = tk_Button(CANVAS, text='Confirm Save File', width=12, command=lambda: saveLsys(project_name.get()))
	confirm_save_file_btn.pack()

	

def homeReset():
	global CANVAS
	clearCanvas()
	TOP_BUTTON = tk_Button(CANVAS, text='RECORD',  command=lambda: toggleRecord('0'))
	TOP_BUTTON.pack()
	BOTTOM_BUTTON = tk_Button(CANVAS, text='Replay', command=loadRecordings)
	BOTTOM_BUTTON.pack()
	FURTHER_BOTTOM_BUTTON = tk_Button(CANVAS, text='Scheduler', command=scheduleINSTRUCTION)
	FURTHER_BOTTOM_BUTTON.pack()
	
def clearCanvas():
	global CANVAS
	CANVAS.destroy()
	CANVAS = Canvas(APP)
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
	listbox.pack()
	scrollbar = Scrollbar(CANVAS)  
	scrollbar.pack(side = RIGHT, fill = BOTH) 
	listbox.config(yscrollcommand = scrollbar.set) 
	scrollbar.config(command = listbox.yview) 
	findSaveFiles(listbox)
	select_button = tk_Button(CANVAS, text='Schedule Routine', width=30,height=1,font=('bold', 8), command=lambda: schedulerScreen(listbox.get(ANCHOR)))
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
	loop_num_label = Label(CANVAS, text='Enter # of Loops', font=('bold', 8))
	loop_num_label.pack()
	loop_num_entry = Entry(CANVAS, textvariable=loop_num)
	loop_num_entry.pack()
	confirm_loop_btn = tk_Button(CANVAS, text='Confirm Loop', width=12, command=lambda: job(csv,loop_time.get(),loop_num.get()))
	confirm_loop_btn.pack()
	
def job(csv, loop_time,num_loops):
	for loop in range(int(num_loops)):
		replay(csv)
		time.sleep(int(loop_time))
		
def enableSafeMode():
	global SAFE_MODE_ENABLED
	if SAFE_MODE_ENABLED:
		SAFE_MODE_ENABLED = False
		print('SAFE_MODE FALSE')
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
	listbox.pack()
	scrollbar = Scrollbar(CANVAS)  
	scrollbar.pack(side = RIGHT, fill = BOTH) 
	listbox.config(yscrollcommand = scrollbar.set) 
	scrollbar.config(command = listbox.yview) 
	findSaveFiles(listbox)
	select_button = tk_Button(CANVAS, text='Replay Routine', width=30,height=1,font=('bold', 8), command=lambda: replayEdit(listbox.get(ANCHOR)))
	select_button.pack()
	
def getCorners(x, y, button, pressed):
	global CORNERS
	if pressed == True:
		CORNERS.append(x)
		CORNERS.append(y)
	if pressed == False:
		CORNERS.append(x)
		CORNERS.append(y)
		return False

def askForScreenshot():
	global CORNERS
	CORNERS = []
	print('Click and drag a box on the screen to indicate where to watch for updated pixels in order to trigger the next event')
	with mouse.Listener(on_move=None,on_click=getCorners,on_scroll=None) as listener:
		listener.join()
	return CORNERS
	
def replayEdit1(file_name):
	global APP
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
	df = df[df['Mouse Drag'] != 'place']
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
		
		
global CANVAS
global APP
APP = Tk()
CANVAS = Canvas(APP)
CANVAS.pack()
APP.title('Computer Recorder')
APP.geometry('700x130')
MENUBAR = Menu(APP)
MENUBAR.add_command(label="Home", command=homeReset)
MENUBAR.add_command(label="Safe",command=enableSafeMode)
MENUBAR.add_command(label="Edit",command=loadEditScreen)
APP.config(menu=MENUBAR)
homeReset()
APP.mainloop()


'''

def gui():
	pass
	#a gui where you can either replay recordings, or record a new script
	
def replayScript():
	pass
	#you select a script to replay, and a screenshot appears, and it asks if you're ready, you click yes and press play, then the computer takes over, replaying, asking before each input
	
def recordScript():
	pass
	#you press record new script, prompt asks if you are on the right screen, you click yes, then you hit record, the window disapears, now all your inputs are recorded
	#when you are done, you hit some kind of hotkey 'dfghjk' all at the same time and hold them for 3 seconds or something, then a window pops up, what would you like to 
	#save your recording as, and then your recording is saved in the dataframe to be called up later as a sort of L system to be read into replay script
'''
