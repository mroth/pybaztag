#!/usr/bin/python
from xml.dom import minidom
import urllib

apiurl 	= "http://api.nabaztag.com/vl/FR/api.jsp"
sn 		= "***"
token 	= "***"

class Nabaztag:
	def __init__(self, sn, token):
		self.sn = sn
		self.token = token
	
	def buildQuery(self, params):
		"""Prep a message for sending (add extra stuff)"""
		pre = [("sn", self.sn), ("token", self.token)]
		query = pre + params
		return query

	def command(self, cmd):
		"""Simple syntax to send a single command, used manually from prompt."""
		(k,v) = cmd.split("=")
		rsp = self.sendCommands( [ (k,v), ])
		return rsp
		
	def cmd(self, cmd):
		"""Simple syntax to send a single command, used manually from prompt and show results."""
		rsp = self.command( cmd )
		xmldoc = minidom.parseString( rsp )
		print xmldoc.toprettyxml()
	
	def sendCommands(self, params):
		"""Gimmie a list of key,value tuples"""
		query = self.buildQuery( params )
		queryurl = apiurl + "?" + urllib.urlencode(query)
		queryurl = urllib.unquote(queryurl)
		rsp = urllib.urlopen( queryurl ).read()
		
		#TODO: check rsp <message> for common error conditions
		#	...ABUSESENDING, NOGOODTOKENORSERIAL, NOTV2RABBIT
		
		return rsp
	
	def sendChor(self, chor):
		"""Send a choreography command."""
		#strip out any extra crap so we can past stuff in from handy formats
		chor = chor.strip()
		chor = chor.replace("\n","")
		rsp = self.sendCommands( [ ("chor", chor), ])
		#TODO: check for CHORSEND response
		return rsp
	
	def sendTTS(self, text):
		"""Send text for text to speech."""
		rsp = self.sendCommands( [ ("tts", text), ])
		#TODO: check for *** response
		return rsp
	
	def setEarLeft(self, pos):
		"""Set the position of the left ear."""
		rsp = self.sendCommands( [ ("posleft", pos), ] )
		#TODO: check for EARSEND response
		return rsp
	
	def setEarRight(self, pos):
		"""Set the position of the right ear."""
		rsp = self.sendCommands( [ ("posright", pos),  ] )
		#TODO: check for EARSEND response
		return rsp
				
	def setEars(self, left, right):
		"""Sets the position of both ears simultaneously."""
		#we don't simply call setEarRight and setEarLeft because we want this done as a single action
		rsp = self.sendCommands( [ ("posleft", left), ("posright", right), ] )
		return rsp
	
	def setSleep(self, status):
		"""Set rabbit sleep status to True or False."""
		if (status == True):
			actNum = 13
		elif (status == False):
			actNum = 14
		#more sanity checking here?
		self.sendCommands( [ ("action", actNum ) ] )
		#TODO: check for COMMANDSEND response
		#	...return true/false based on this
	
	def statusSleep(self):
		"""Is the rabbit sleeping?"""
		rsp = self.sendCommands( [ ("action", "7") ])
		xmldoc = minidom.parseString( rsp )
		answer = xmldoc.getElementsByTagName("rabbitSleep")[0].firstChild.data
		if answer == 'NO':
			return False
		else:
			return True
	
	def statusEars(self):
		"""Return a tuple with the current position of the ears (left, right)."""
		rsp = self.sendCommands( [ ("ears", "ok") ])
		xmldoc = minidom.parseString( rsp )
		left = int(xmldoc.getElementsByTagName("leftposition")[0].firstChild.data)
		right = int(xmldoc.getElementsByTagName("rightposition")[0].firstChild.data)
		return (left,right)
		
	def statusFriends(self):
		"""Returns a list of the nabaztag's friends."""
		rsp = self.sendCommands( [ ("action", "2") ])
		xmldoc = minidom.parseString( rsp )
		#TODO: handle
		pass
		
	def statusTimezone(self):
		"""Returns the nabaztag's timezone."""
		rsp = self.sendCommands( [ ("action", "4") ])
		xmldoc = minidom.parseString( rsp )
		answer = xmldoc.getElementsByTagName("timezone")[0].firstChild.data
		#TODO: parse answer string into some sort of format python understands natively?
		return answer
	
	def newComplexCommand(self):
		return NabaztagComplexCommand( self )


class NabaztagComplexCommand( Nabaztag ):
	commandQueue = []
	
	def __init__(self, parentNabaztag):
		#we dont actually want to call the parents init, since we can proxy cmds back to it...
		self.parentNabaztag = parentNabaztag
		
	def sendCommands(self, params):
		#lets override this bitch!
		self.addCommand( params )
		return "Added to command queue."
	
	def clearQueue(self):
		self.commandQueue = []
	
	def addCommand(self, params):
		#TODO: check commandQueue to see if a command of that type already exists
		#	...if so... override?  throw an exception?  what happens in NB API in this case?
		self.commandQueue += params
		#TODO: return some sort of status
	
	def cmd(self, cmd):
		#Hey idiot, you dont actually want results in realtime since you're building a complex command.  
		# 	...default to command() instead."""
		return self.command(cmd)
	
	def sendNow(self):
		"""Send out the queued up commands as a single query."""
		rsp = self.parentNabaztag.sendCommands( self.commandQueue )
		return rsp
	
	def statusSleep(self):
		#TODO: throw some sort of exception msg for all status queries, since they are instant....
		pass

if __name__ == "__main__":
	nb = Nabaztag(sn,token)
	nbc = nb.newComplexCommand()
