from glob import glob
import tkinter as tk
import json
from tello import Tello
from os.path import exists
from PIL import ImageTk, Image
import cv2
from tkinter import messagebox
from os import makedirs
from datetime import datetime
import threading
from time import sleep
import pyttsx3
import sys
import os
import psutil

frame_resolution=None
settings_window_open=False
settingsWindow=None
tello_connected=False
default_tello_ip='192.168.10.1'
settings_data=None
drone=None
lmain = None
tello_status=None
settings_data=None

unlock_password = "12345"
keyboard_is_unlocked = False
unlock_input = ""
flip_image = True


imgbox=None
		
recording=False
direction=0
recording_label=None
recording_label_text = None
move_step=0
angle_step=0
upd_bat_level=False

root = None
path_pictures="./media/pictures/"
path_videos="./media/videos/"

recording=False
recording_label=None
recording_label_text = None

path_pictures="./media/pictures/"
path_videos="./media/videos/"

tts_engine=pyttsx3.init()
tts_engine.setProperty('rate',120)
tts_engine.setProperty('voice', 'english_rp+f3')

def on_settings_closing():
	global root
	global settingsWindow
	global settings_window_open
	settings_window_open=False
	settingsWindow.destroy()
	
	
def on_root_closing():
	global root
	global upd_bat_level
	upd_bat_level=False
	root.destroy()


def read_settings():
	global settings_data
	if (exists('settings.json')):
		with open('settings.json') as json_file:
			settings_data = json.loads(json_file.read())
		return True
	else:
		return False

def write_settings(data):
	# Using a JSON string
	json_string = json.dumps(data)
	with open('settings.json', 'w') as outfile:
		outfile.write(json_string)

def create_media_folder():
	global path_pictures
	global path_videos
	
	if not exists(path_pictures):
		makedirs(path_pictures)
	
	if not exists(path_videos):
		makedirs(path_videos)


def connect_to_tello(tello_ip_value):
	
	global drone
	global frame_resolution
	res = False
	try:
		if (tello_ip_value=="192.168.10.1"):
			drone=Tello()
		else:
			drone=Tello(tello_ip=tello_ip_value)

		res= drone.send_command("command")
		
		
		if res == True:
			drone.connect()
			drone.stream_on()
			frame_resolution=(960,720)
			drone.send_command("downvision 0")
	except:
		
		drone = None
		res = False
	return res
		
		
		
def take_picture():
	global drone
	global path_pictures
	while drone.read_frame() is not None:
		frame=drone.read_frame()
		#frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
		if flip_image:
			frame = cv2.flip(frame,0)
		write_image(path_pictures,frame)
		#messagebox.showinfo('Jetson Tools', 'Took image!')
		speak("I took a photo")
		break
		
		
def start_video():
	global recording
	global recording_label
	
	recording_label_text.set("Recording...")
	recording=True
	threading.Thread(target=record_frames).start()

def start_video_i():
	global recording
	speak("Recording started")
	recording=True
	threading.Thread(target=record_frames).start()

def record_frames():
	global img_array
	global path_videos
	global recording
	global frame_resolution
	now = datetime.now() # current date and time
	video_file='video_'+now.strftime("%Y%d%m%H%M%S")+'.avi'
	out = cv2.VideoWriter(path_videos+video_file,cv2.VideoWriter_fourcc(*'DIVX'),30,frame_resolution)
	while drone.read_frame() is not None:
		frame=drone.read_frame()
		#frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
		if flip_image:
			frame = cv2.flip(frame,0)
		out.write(frame)
		sleep(0.01)
		if not recording:
			out.release()
			break

def stop_video():
	global recording
	global recording_label
	recording=False
	recording_label_text.set("")

def stop_video_i():
	global recording
	recording=False
	speak("Recording finished")
	
def write_image(image_path, image):
	now = datetime.now() # current date and time
	image_file='image_'+now.strftime("%Y%d%m%H%M%S")+'.jpg'
	cv2.imwrite(image_path+image_file,image)


def settings_on_save(data):
	global settingsWindow
	global settings_window_open
	data_to_save={}
	try:
		data_to_save["tello_ip"]=data["tello_ip"].get()
		
		if (data["move_step"].get().strip()==""):
			data_to_save["move_step"]=0
		else:
			data_to_save["move_step"]=int(data["move_step"].get().strip())
		
		if (data["angle_step"].get().strip()==""):
			data_to_save["angle_step"]=0
		else:
			data_to_save["angle_step"]=int(data["angle_step"].get().strip())
		
		write_settings(data_to_save)
		#messagebox.showinfo('Jetson Tools', 'Settings saved!')
		speak("I saved settings")
	
	except Exception as e:
		print(e)
		#messagebox.showerror('Jetson Tools', 'Couldn\'t save settings')
		speak("I could not save settings")


def onControlPanel():
	global root
	global recording_label
	global recording_label_text
	recording_label_text = tk.StringVar()
	
	# Toplevel object which will
	# be treated as a new window
	controlWindow = tk.Toplevel(root)

	# sets the title of the
	# Toplevel widget
	controlWindow.title("Control Panel")

	# sets the geometry of toplevel
	controlWindow.geometry("750x270")
	
	up_button = tk.Button(controlWindow, text="Up", command=lambda: send_command("up"))
	up_button.grid(column=1, row=0, sticky=tk.NW, padx=5, pady=5)
	
	forward_button = tk.Button(controlWindow, text="Forward", command=lambda: send_command("forward"))
	forward_button.grid(column=5, row=0, sticky=tk.NW, padx=5, pady=5)
	
	left_button = tk.Button(controlWindow, text="Left", command=lambda: send_command("left"))
	left_button.grid(column=0, row=1, sticky=tk.NW, padx=5, pady=5)
	
	to_button = tk.Button(controlWindow, text="Take off", command=lambda: send_command("takeoff"))
	#to_button = tk.Button(controlWindow, text="Take off")
	#to_button.bind("<t>",send_command("takeoff"))
	to_button.grid(column=1, row=1, sticky=tk.NW, padx=5, pady=5)
	
	right_button = tk.Button(controlWindow, text="Right", command=lambda: send_command("right"))
	right_button.grid(column=2, row=1, sticky=tk.NW, padx=5, pady=5)
	
	change_camera_button = tk.Button(controlWindow, text="Change Camera", command=lambda: send_command("cc"))
	change_camera_button.grid(column=3, row=1, sticky=tk.NW, padx=5, pady=5)
	
	lw_button = tk.Button(controlWindow, text="Move left", command=lambda: send_command("move_left"))
	lw_button.grid(column=4, row=1, sticky=tk.NW, padx=5, pady=5)
	
	land_button = tk.Button(controlWindow, text="Land", command=lambda: send_command("land"))
	#land_button = tk.Button(controlWindow, text="Land")
	#land_button.bind("<l>",send_command("land"))
	land_button.grid(column=5, row=1, sticky=tk.NW, padx=5, pady=5)
	
	rw_button = tk.Button(controlWindow, text="Move right", command=lambda: send_command("move_right"))
	rw_button.grid(column=6, row=1, sticky=tk.NW, padx=5, pady=5)
	
	down_button = tk.Button(controlWindow, text="Down", command=lambda: send_command("down"))
	down_button.grid(column=1, row=2, sticky=tk.NW, padx=5, pady=5)
	
	back_button = tk.Button(controlWindow, text="Back", command=lambda: send_command("back"))
	back_button.grid(column=5, row=2, sticky=tk.NW, padx=5, pady=5)
	
	
	#################################
	
	flip_forward_button = tk.Button(controlWindow, text="Flip Forward", command=lambda: send_command("flip_f"))
	flip_forward_button.grid(column=1, row=3, sticky=tk.NW, padx=5, pady=5)
	
	flip_left_button = tk.Button(controlWindow, text="Flip left", command=lambda: send_command("flip_l"))
	flip_left_button.grid(column=0, row=4, sticky=tk.NW, padx=5, pady=5)
	
	flip_right_button = tk.Button(controlWindow, text="Flip right", command=lambda: send_command("flip_r"))
	flip_right_button.grid(column=2, row=4, sticky=tk.NW, padx=5, pady=5)
		
	flip_backward_button = tk.Button(controlWindow, text="Flip Backward", command=lambda: send_command("flip_b"))
	flip_backward_button.grid(column=1, row=5, sticky=tk.NW, padx=5, pady=5)
	
	################################
	
	take_picture_button = tk.Button(controlWindow, text="Take Picture", command=lambda: send_command("take_pic"))
	take_picture_button.grid(column=3, row=3, sticky=tk.NW, padx=5, pady=5)
	
	start_video_button = tk.Button(controlWindow, text="Start Video", command=lambda: send_command("video_start"))
	start_video_button.grid(column=3, row=4, sticky=tk.NW, padx=5, pady=5)
	
	stop_video_button = tk.Button(controlWindow, text="Stop Video", command=lambda: send_command("video_stop"))
	stop_video_button.grid(column=3, row=5, sticky=tk.NW, padx=5, pady=5)
	
	#################################
	
	recording_label = tk.Label(controlWindow, fg='red', textvariable=recording_label_text)
	recording_label.grid(column=4, row=5, sticky=tk.NW, padx=5, pady=5)
	
	controlWindow.bind("<Key>", hotkey_listener)
	
	img3 = tk.PhotoImage(file='./assets/logo3.png')
	controlWindow.tk.call('wm', 'iconphoto', controlWindow._w, img3)

def hotkey_listener2(event):
	print(event.keycode)

def hotkey_listener(event):
	global root
	global keyboard_is_unlocked
	global unlock_password
	global unlock_input
	global flip_image

	# w 87
	# a 65
	# s 83
	# d 68
	# t 84
	# f 70
	# left 37
	# up 38
	# right 39
	# down 40
	# l 76
	# c 67
	# 1 49
	# 2 50
	# 3 51
	# 4 52
	# 5 53
	# 6 54
	# 7 55
	# q 81
	# r 82
	# 8 56
	# 9 57
	# F1 112
	# F2 113
	# F3 114
	# F4 115
	# F5 116
	# F6 117
	# F7 118
	# F8 119
	# F9 120


	match event.keycode:
		case 87:
			clear_unlock_pass()
			send_command_with_lock_check("up")
		case 65:
			clear_unlock_pass()
			send_command_with_lock_check("left")
		case 83:
			clear_unlock_pass()
			send_command_with_lock_check("down")
		case 68:
			clear_unlock_pass()
			send_command_with_lock_check("right")
		case 84:
			clear_unlock_pass()
			send_command_with_lock_check("takeoff")
		case 37:
			clear_unlock_pass()
			send_command_with_lock_check("move_left")
		case 38:
			clear_unlock_pass()
			send_command_with_lock_check("forward")
		case 39:
			clear_unlock_pass()
			send_command_with_lock_check("move_right")
		case 40:
			clear_unlock_pass()
			send_command_with_lock_check("back")
		case 70:
			clear_unlock_pass()
			if keyboard_is_unlocked:
				flip_image = not flip_image
			else:
				speak("Keyboard is locked")
		case 76:
			clear_unlock_pass()
			send_command_with_lock_check("land")
		case 67:
			clear_unlock_pass()
			send_command_with_lock_check("cc")
		case 112:
			clear_unlock_pass()
			send_command_with_lock_check("flip_f")
		case 113:
			clear_unlock_pass()
			send_command_with_lock_check("flip_l")
		case 114:
			clear_unlock_pass()
			send_command_with_lock_check("flip_r")
		case 115:
			clear_unlock_pass()
			send_command_with_lock_check("flip_b")
		case 116:
			clear_unlock_pass()
			send_command_with_lock_check("take_pic")
		case 117:
			clear_unlock_pass()
			send_command_with_lock_check("video_start_i")
		case 118:
			clear_unlock_pass()
			send_command_with_lock_check("video_stop_i")
		case 81:
			clear_unlock_pass()
			send_command_with_lock_check("land")
			sleep(5)
			root.destroy()
		case 82:
			clear_unlock_pass()
			if keyboard_is_unlocked:
				onRestart()
			else:
				speak("Keyboard is locked")
		case 119:
			clear_unlock_pass()
			if keyboard_is_unlocked:
				onControlPanel()
			else:
				speak("Keyboard is locked!")
		case 120:
			clear_unlock_pass()
			if keyboard_is_unlocked:
				onSettings()
			else:
				speak("Keyboard is locked")
		case 49:
			unlock_input = unlock_input + "1"
			check_unlock_input()
		case 50:
			unlock_input = unlock_input + "2"
			check_unlock_input()
		case 51:
			unlock_input = unlock_input + "3"
			check_unlock_input()
		case 52:
			unlock_input = unlock_input + "4"
			check_unlock_input()
		case 53:
			unlock_input = unlock_input + "5"
			check_unlock_input()

		case _:
			clear_unlock_pass()

def check_unlock_input():
	global unlock_input
	global unlock_password
	global keyboard_is_unlocked
	possible_combinations = ["1","12","123","1234", "12345"]

	if unlock_input == unlock_password:
		if keyboard_is_unlocked:
			keyboard_is_unlocked = False
			speak("Keyboard is locked")
		else:
			keyboard_is_unlocked = True
			speak("Keyboard is unlocked")

	if unlock_input not in possible_combinations:
		unlock_input=""
		speak("Wrong combination")


def clear_unlock_pass():
	global unlock_input
	unlock_input=""	

# Settings window
def onSettings():
	global root
	global settings_data
	global default_tello_ip
	global default_tello_port
	global default_tello_udp_port
	global settingsWindow
	global settings_window_open
	
	if not settings_window_open:
		# Toplevel object which will
		# be treated as a new window
		settingsWindow = tk.Toplevel(root)

		# sets the title of the
		# Toplevel widget
		settingsWindow.title("Settings")

		# sets the geometry of toplevel
		settingsWindow.geometry("450x150")
	 
		# A Label widget to show in toplevel
		root.resizable(0, 0)

		# configure the grid
		#settingsWindow.columnconfigure(0, weight=1)
		#settingsWindow.columnconfigure(1, weight=1)

		# Tello IP
		tello_ip_label = tk.Label(settingsWindow, text="Tello IP:")
		tello_ip_label.grid(column=0, row=0, sticky=tk.NW, padx=5, pady=5)

		tello_ip_entry = tk.Entry(settingsWindow)
		tello_ip_entry.grid(column=1, row=0, sticky=tk.NW, padx=5, pady=5)
		
		move_step_label = tk.Label(settingsWindow, text="Move step (sm)")
		move_step_label.grid(column=0, row=1, sticky=tk.NW, padx=5, pady=5)

		move_step_entry = tk.Entry(settingsWindow)
		move_step_entry.grid(column=1, row=1, sticky=tk.NW, padx=5, pady=5)
		
		
		angle_step_label = tk.Label(settingsWindow, text="Angle step (deg):")
		angle_step_label.grid(column=0, row=2, sticky=tk.NW, padx=5, pady=5)

		angle_step_entry = tk.Entry(settingsWindow)
		angle_step_entry.grid(column=1, row=2, sticky=tk.NW, padx=5, pady=5)
		
		
		
		restart_reminder_label = tk.Label(settingsWindow,text="Restart app after changes", fg='red')
		restart_reminder_label.grid(column=0, row=3, sticky=tk.NW, padx=5, pady=5)
		
		entry_fields={
			"tello_ip":tello_ip_entry,
			"move_step":move_step_entry,
			"angle_step":angle_step_entry
			}
		
		
		save_button = tk.Button(settingsWindow, text="Save", command=lambda: settings_on_save(entry_fields))
		save_button.grid(column=1, row=3, sticky=tk.NW, padx=5, pady=5)
		
		restart_button = tk.Button(settingsWindow, text="Restart", command=onRestart)
		restart_button.grid(column=2, row=3, sticky=tk.NW, padx=5, pady=5)
		
		settings_read=read_settings()
			
		if not settings_read:
			# set default values
			tello_ip_entry.delete(0, tk.END)
			tello_ip_entry.insert(0, default_tello_ip)
			move_step_entry.delete(0, tk.END)
			move_step_entry.insert(0, 30)
			angle_step_entry.delete(0, tk.END)
			angle_step_entry.insert(0, 40)
		else:
			# set values from settings
			tello_ip_entry.delete(0, tk.END)
			if "tello_ip" in settings_data:
				tello_ip_entry.insert(0, settings_data["tello_ip"])
			else:
				tello_ip_entry.insert(0, default_tello_ip)
				
			move_step_entry.delete(0, tk.END)
			if "move_step" in settings_data:
				move_step_entry.insert(0, settings_data["move_step"])
			else:
				move_step_entry.insert(0, 30)
			angle_step_entry.delete(0, tk.END)
			if "angle_step" in settings_data:
				angle_step_entry.insert(0, settings_data["angle_step"])
			else:
				angle_step_entry.insert(0, 40)
		
		
		
		# set on close event
		settingsWindow.protocol("WM_DELETE_WINDOW", on_settings_closing)
		settingsWindow.grab_set() # open in modal mode
		img3 = tk.PhotoImage(file='./assets/logo3.png')
		settingsWindow.tk.call('wm', 'iconphoto', settingsWindow._w, img3)
		settings_window_open=True


def send_command_with_lock_check(command):
	global keyboard_is_unlocked
	
	if keyboard_is_unlocked:
		send_command(command)
	else:
		speak("Keyboard is locked")


def send_command(command):
	global drone
	global move_step
	global angle_step

	
	if (command=="takeoff"):
		speak("Taking off")
		drone.takeoff()
	elif (command=="land"):
		speak("Landing")
		drone.land()
	elif (command=="up"):
		drone.move_up(move_step)
	elif (command=="down"):
		drone.move_down(move_step)
	elif (command=="left"):
		drone.rotate_counterclockwise(angle_step)
	elif (command=="right"):
		drone.rotate_clockwise(angle_step)
	elif (command=="cc"):
		switch_camera()
	elif (command=="move_left"):
		drone.move_left(move_step)
	elif (command=="move_right"):
		drone.move_right(move_step)
	elif (command=="forward"):
		drone.move_forward(move_step)
	elif (command=="back"):
		drone.move_backward(move_step)
	elif (command=="flip_f"):
		drone.flip("forward")
	elif (command=="flip_l"):
		drone.flip("left")
	elif (command=="flip_r"):
		drone.flip("right")
	elif (command=="flip_b"):
		drone.flip("backward")	
	elif (command=="take_pic"):
		take_picture()
	elif (command=="video_start"):
		start_video()
	elif (command=="video_stop"):
		stop_video()
	elif (command=="video_start_i"):
		start_video_i()
	elif (command=="video_stop_i"):
		stop_video_i()

def switch_camera():
	global direction
	global drone
	global frame_resolution
	
	direction+=1
	
	if direction%2 ==0:
		frame_resolution=(960,720)
	else:
		frame_resolution=(320,240)
	drone.send_command("downvision "+str(direction%2))

def update_battery():        
	global drone
	global tello_status
	global upd_bat_level
	while upd_bat_level:
		bat_level=drone.get_battery()
		tello_status['text']=f'Tello connected. Battery level {bat_level}'
		sleep(5)
        
def onRestart():
	global root
	root.destroy()

	try:
		p = psutil.Process(os.getpid())
		for handler in p.get_open_files() + p.connections():
			os.close(handler.fd)
	except Exception as e:
		print(e)
	python = sys.executable
	os.execl(python, python, "main.py")

# main window function
def main():
	global lmain
	global root
	global tello_status
	global drone
	global move_step
	global angle_step
	global imgbox
	global upd_bat_level
	
	try:
		settings_read=read_settings()
		if settings_read:
			res = connect_to_tello(settings_data["tello_ip"])
			move_step = settings_data["move_step"]
			angle_step = settings_data["angle_step"]
	except:
		res=False
	
	connection_screen.destroy()
	
	root = tk.Tk()
	root.title('Jetson Tools')
	
	root.attributes('-fullscreen', 1)
	#root.geometry('960x720')
	
	menubar = tk.Menu(root)

	filemenu = tk.Menu(menubar)
	filemenu.add_command(label="Control panel",command=onControlPanel)
	filemenu.add_command(label="Settings",command=onSettings)
	filemenu.add_command(label="Restart",command=onRestart)
	filemenu.add_command(label="Exit", command=root.destroy)

	
	menubar.add_cascade(label="File", menu=filemenu)
	
	root.config(menu=menubar)
	
	# Tello Status
	tello_status = tk.Label(root, fg="green", text="")
	tello_status.pack()
		
	lmain = tk.Canvas(root, highlightthickness=0)
	lmain.pack(fill=tk.BOTH, expand=1)        
	#imgbox = lmain.create_image(277, 156, image=None, anchor='nw')
	imgbox = lmain.create_image(0, 0, image=None, anchor='nw')
	
	if not settings_read:
		tello_status.config(fg="red")
		tello_status['text']="Check settings"
	else:
		if res == False:
			tello_status.config(fg="red")
			tello_status['text']="Tello is not connected"
		else:
			
			tello_status.config(fg="green")
			bat_level=drone.get_battery()
			tello_status['text']=f'Tello connected. Battery level {bat_level}'
			upd_bat_level=True
			threading.Thread(target=update_battery).start()
			video_stream()
	
	
	root.bind("<Key>", hotkey_listener)

	img2 = tk.PhotoImage(file='./assets/logo2.png')
	root.tk.call('wm', 'iconphoto', root._w, img2)
	
	create_media_folder()
	root.protocol("WM_DELETE_WINDOW", on_root_closing)
	root.mainloop()

def speak(text):
	global tts_engine
	tts_engine.say(text)
	tts_engine.runAndWait()

# function for video streaming
def video_stream():
	global lmain
	global drone
	global imgbox
	global flip_image
	
	if drone.read_frame() is not None:
		frame = drone.read_frame()
		cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
		w, h = 1366, 768
		if flip_image:
			cv2image = cv2.flip(cv2image,0)		
		img = Image.fromarray(cv2image)
		image = ImageTk.PhotoImage(image=img.resize((w,h)))
		lmain.itemconfig(imgbox, image=image)
		lmain.image = image
	lmain.after(1, video_stream) 

connection_screen = tk.Tk()

connection_screen.title('Jetson Tools')
   
# Adjust size
connection_screen.geometry("180x20")


# Set Label
connection_label = tk.Label(connection_screen,text="Connecting to Tello..."  ,font=18)
connection_label.pack()


img = tk.PhotoImage(file='./assets/logo.png')
connection_screen.tk.call('wm', 'iconphoto', connection_screen._w, img)

# Set Interval
connection_screen.after(1000,main)


 
# Execute tkinter
tk.mainloop()



