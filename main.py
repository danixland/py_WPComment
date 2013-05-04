#!/usr/bin/env python

#	py_WPComment - manage comments on your WordPress blog
#	Copyright 2013 - danilo 'danix' macri - http://danixland.net

#	This program is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; either version 2 of the License.
#	
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#	
#	You should have received a copy of the GNU General Public License
#	along with this program; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#	License: license.txt
#	program_uri: http://danixland.net/?p=3339

import xmlrpclib, time, pickle, base64, os, pygtk
pygtk.require('2.0')
import gtk

default_settings = {"server": "", "username": "", "password": ""}
settings_file = os.getenv("HOME") + "/.py_wpcomment.dat"
pyWPC_version = "0.1"
pyWPC_author = ['danix - http://danixland.net']
pyWPC_license = open("license.txt")

def encryptPass(password):
	return base64.b64encode(password)

def decryptPass(password):
	return base64.b64decode(password)

def checkComm(old_commCount):
	if os.path.isfile(settings_file) and os.access(settings_file, os.R_OK):
		settings = pickle.load(open(settings_file))

	server_uri = settings['server'] + "/xmlrpc.php"
	server_admin = settings['username']
	admin_pass = decryptPass(settings['password'])
	filters={'post_id': '', 'status': 'hold', 'number': '', 'offset': ''}
	
	server = xmlrpclib.ServerProxy(server_uri); # connect to WP server
	comments = server.wp.getComments("", server_admin, admin_pass, filters); # fetch comments
	new_commCount = len(comments);
	if new_commCount > old_commCount:
		old_commCount = new_commCount
		return True # there are new comments
	else:
		return False # no new comments so far


class WPComment:
	
	# close the window and quit
	def delete_event(self, widget, event, data=None):
		gtk.main_quit()
		return False

	# __init__ function - this handles the status icon and the main window
	def __init__(self):
		
		# Create a status icon
		self.statusicon = gtk.StatusIcon()
		self.statusicon.set_from_file("icons/wpmini-grey.png")
		self.statusicon.connect("popup-menu", self.right_click_event)
		self.statusicon.connect("activate", self.left_click_event)
		self.statusicon.set_tooltip("No new comments")

		# Create the main program window
		self.main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.main_window.set_title("py_WPComment") 
		self.main_window.set_icon_from_file("icons/wpmini-grey.png")
		self.main_window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
		self.main_window.set_size_request(500, 350)
		self.main_window.connect("delete_event", self.delete_event)
		self.main_window.set_visible(False) # set this to True to show the main window at startup. Leave False to start minimized in the systray

		# Create the popup window
		self.popup_window = gtk.Window(gtk.WINDOW_POPUP)
		self.label = gtk.Label("py_WPC_notify")
		self.eventbox = gtk.EventBox()
		self.eventbox.add(self.label)
		self.popup_window.set_icon_from_file("icons/wpmini-grey.png")
		self.popup_window.set_size_request(500, 150)
		self.popup_window.connect("delete_event", self.delete_event)
		self.popup_window.add(self.eventbox)
		# little hack to get the exact position to give to the popup window
		sr = self.popup_window.get_screen()
		sr_h_pos = sr.get_width() - 525
		sr_v_pos = 25
		self.popup_window.move(sr_h_pos, sr_v_pos)
		self.popup_window.set_visible(False)

	def left_click_event(self, button):
		if self.main_window.get_visible():
			self.main_window.hide()
		else:
			self.main_window.show()

	def right_click_event(self, icon, button, time):
		menu = gtk.Menu()

		show_window = gtk.MenuItem("Show/Hide window")
		options = gtk.MenuItem("Settings")
		about = gtk.MenuItem("About")
		quit = gtk.MenuItem("Quit")

		show_window.connect("activate", self.left_click_event)
		options.connect("activate", self.show_settings_dialog)		  
		about.connect("activate", self.show_about_dialog)
		quit.connect("activate", gtk.main_quit)

		menu.append(show_window)
		menu.append(options)
		menu.append(about)
		menu.append(quit)
		     
		menu.show_all()
		     
		menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusicon)

	# the about dialog callback
	def show_about_dialog(self, widget):
		about_dialog = gtk.AboutDialog()
		
		about_dialog.set_destroy_with_parent(True)
		about_dialog.set_name("py_WPComment")
		about_dialog.set_comments("A simple application that allows the user to manage comments on a WordPress based website")
		about_dialog.set_website("http://danixland.net/?p=3339")
		about_dialog.set_website_label("visit author's website")
		about_dialog.set_license(pyWPC_license.read())
		about_dialog.set_wrap_license(True)
		about_dialog.set_version(pyWPC_version)
		about_dialog.set_authors(pyWPC_author)
		     		
		about_dialog.run()
		about_dialog.destroy()

	# the settings dialog callback
	def show_settings_dialog(self, widget):
		if os.path.isfile(settings_file) and os.access(settings_file, os.R_OK):
			old_settings = pickle.load(open(settings_file))
		else:
			old_settings = default_settings
		settings = gtk.Dialog("Settings", self.popup_window, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
		settings.set_default_size(250, 300)
		
		title = gtk.VBox(False, 5) # box containing the label of the settings
		title_container = gtk.HBox(False, 5) 
		label = gtk.Label("Queste impostazioni verranno salvate in un file di testo nella tua home.")

		main_options = gtk.VBox(False, 5) # Vertical box containing the main settings (ServerAddress, UserName, Password)
		server_box = gtk.HBox(False, 5) # Horiz box containing the label and entry for the server address
		server_label = gtk.Label("Server Address")
		server = gtk.Entry()
		server.set_text(old_settings['server'])
		username_box = gtk.HBox(False, 5) # Horiz box containing the label and entry for the username
		username_label = gtk.Label("User Name")
		username = gtk.Entry()
		username.set_text(old_settings['username'])
		password_box = gtk.HBox(False, 5) # Horiz box containing the label and entry for the password
		password_label = gtk.Label("Password")
		password = gtk.Entry()
		password.set_visibility(False)
		password.set_text(decryptPass(old_settings['password']))


		title.pack_start(title_container, True, True, 0)
		title_container.pack_start(label, True, True, 0)

		server_box.pack_start(server_label, True, True, 0)
		server_box.pack_start(server, True, True, 0)
		username_box.pack_start(username_label, True, True, 0)
		username_box.pack_start(username, True, True, 0)
		password_box.pack_start(password_label, True, True, 0)
		password_box.pack_start(password, True, True, 0)

		main_options.pack_start(server_box, True, True, 0)
		main_options.pack_start(username_box, True, True, 0)
		main_options.pack_start(password_box, True, True, 0)

		settings.vbox.pack_start(title, True, True, 0)
		settings.vbox.pack_start(main_options, True, True, 0)

		settings.show_all()
		
		response = settings.run()
		if response == gtk.RESPONSE_OK:
			print "The OK button was clicked" # when in production this can be removed
			new_settings = {"server": server.get_text(), "username": username.get_text(), "password": encryptPass(password.get_text())}
			pickle.dump(new_settings, open(settings_file, "w"))
		elif response == gtk.RESPONSE_CANCEL:
			print "The Cancel button was clicked" # when in production this can be removed
		
		settings.destroy()

		

def main():
	gtk.main()

if __name__ == "__main__":
	WPComment()
	main()
