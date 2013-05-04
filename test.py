#! /usr/bin/env/python

import xmlrpclib, time

server_uri="http://localhost/wp09/xmlrpc.php";
blog_id="";
server_admin="admin";
admin_pass="password";
filters={'post_id': '', 'status': 'hold', 'number': '', 'offset': ''};


def checkComm(old_commCount):
	server = xmlrpclib.ServerProxy(server_uri); # connect to WP server
	comments = server.wp.getComments(blog_id, server_admin, admin_pass, filters); # fetch comments
	new_commCount = len(comments);
	if new_commCount > old_commCount:
		print "\n"
		print "old_commCount is " + str(old_commCount)
		print "new_commCount is " + str(new_commCount)
		print "there are new comments"
	else:
		print "\n"
		print "old_commCount is " + str(old_commCount)
		print "new_commCount is " + str(new_commCount)
		print "no new comments"
	old_commCount = new_commCount
	return old_commCount

commCount = 0;
while True:
	commCount = checkComm(commCount)
	time.sleep(60)
