# Author: Inamullah Taj | Email: inamu@plumgrid.com
import requests
import json


class RESTClient():
	"""
		This class makes REST calls to API Neutron in order to perform:
		- CRUD on Transit Domains (TD)
		- CRUD on Physical Attachment Points (PAP)
	"""	
	# Static Values
	port_keystone = "5000"
	port_neutron = "9696"
	base_url = "http://localhost:"
	transit_domain_url = "/v2.0/transit-domains"

	#acccess token to be used to make REST calls to Neutron
	accessToken = ""

	# OpenStack Credentials to access KeyStone/Neutron APIs
	username = "admin"
	password = "pass"

	
	# Constructor
	def __init__(self):
		
		# importing global variable
		global accessToken

		# Get Access Token in order to start making REST calls
		accessToken = self.getAccessToken()


	def getAccessToken(self):
		"""
			Function that returns Access Token from Keystone
			that is required to make REST calls to Neutron
			ARGUMENTS: none
			RETURN TYPE: String
		"""

		# Set up URL to access
		url = self.base_url + self.port_keystone + "/v2.0/tokens"
		
		# Set up Custom Headers for Request
		headers = {'accept':'application/json','content-type':'application/json'}
		
		# Set up parameters to send Authorization Details
		data = {"auth":{"passwordCredentials":{"username":self.username,"password":self.password},
						"tenantName":"admin"}}
		
		# Convert it into JSON
		dataInJson = json.dumps(data)

		# Send POST request and get RESPONSE
		response = requests.post(url, headers=headers, data=dataInJson)
		
		# Convert response in JSON
		jsonResp = response.json()

		# Extract Access Token from JSON Response
		accessToken = jsonResp['access']['token']['id']

		# Return Access Token
		return accessToken

	def createTransitDomain(self, tdName):
		"""
			REST Function to create a Transit Domain
			and return the created Transit Domain
			ARGUMENTS:
				tdName = name of transit domain
			RETURN TYPE: JSON
		"""
		
		# imported global variable
		global accessToken

		# Set up URL to be accessed
		url = self.base_url + self.port_neutron + self.transit_domain_url
		
		# Set up Custom Headers for Request
		headers = {'X-Auth-Token':accessToken,
					'accept':'application/json',
					'content-type':'application/json'}

		# Set up parameters to send Transit Domain Name
		data = {"transit_domain":{"name":tdName}}
				
		# Convert it into JSON
		dataInJson = json.dumps(data)

		# Send POST request to create Transit Domain and get RESPONSE
		response = requests.post(url, headers=headers, data=dataInJson)
		
		# Convert response in JSON
		jsonResp = response.json()

		# Return JSON of response
		return jsonResp

	def showTransitDomain(self, tdId):
		"""
			Function to return a specific Transit Domain
			ARGUMENTS:
				tdId = ID of Transit Domain (not uuid of TD)
			RETURN TYPE: JSON
		"""
		# imported global variable
		global accessToken

		# Set up URL for a specific Transit Domain to be accessed
		url = self.base_url + self.port_neutron + self.transit_domain_url + "/" + tdId
		
		# Set up Custom Headers for Request
		headers = {'X-Auth-Token':accessToken,
					'accept':'application/json',
					'content-type':'application/json'}

		# Send GET request and get RESPONSE
		response = requests.get(url, headers=headers)
		
		# Convert response in JSON
		jsonResp = response.json()

		# Return JSON of response
		return jsonResp

	def listTransitDomain(self):
		"""
			REST Function to list all (existing) Transit Domain
			ARGUMENTS: NONE
			RETURN TYPE: JSON
		"""

		# imported global variable
		global accessToken

		# Set up URL to be accessed
		url = self.base_url + self.port_neutron + self.transit_domain_url

		# Set up Custom Headers for Request
		headers = {'X-Auth-Token':accessToken,
					'accept':'application/json',
					'content-type':'application/json'}

		# Send GET request to List all TDs and get response in JSON
		response = requests.get(url, headers=headers)
		
		# Convert response in JSON
		jsonResp = response.json()

		# Return JSON of response
		return jsonResp

	def updateTransitDomain(self, tdId, tdName):
		"""
			Function to update Transit Domain with given new parameters
			ARGUMENTS:
				tdId = ID of Transit Domain (not uuid of TD) to find TD by ID
				tdName = New name of Transit Domain which is to be updated
			RETURN TYPE: JSON
		"""
		# imported global variable
		global accessToken

		# Set up URL to specific access Transit Domain
		url = self.base_url + self.port_neutron + self.transit_domain_url + "/" + tdId

		# Set up Custom Headers for Request
		headers = {'X-Auth-Token':accessToken,
					'accept':'application/json',
					'content-type':'application/json'}

		# Set up parameters to send Transit Domain Name
		data = {"transit_domain":{"name":tdName}}
				
		# Convert it into JSON
		dataInJson = json.dumps(data)

		# Send PUT request to update Transit Domain Details
		response = requests.put(url, headers=headers, data=dataInJson)

		# NOTE: response returns 200 in normal cases, therefore we extract the body
		# which comes as a String and then converts it into JSON
		jsonResp = json.loads(response.text)
		
		#return JSON Response
		return jsonResp

	def deleteTransitDomain(self, tdId):
		"""
			Function to delete Transit Domain with given ID of Transit Domain
			ARGUMENTS:
				tdId = ID of Transit Domain (not uuid of TD) to find TD by ID
			RETURN TYPE: boolean [True, False]
		"""
		# imported global variable
		global accessToken

		# Set up URL to specific access Transit Domain
		url = self.base_url + self.port_neutron + self.transit_domain_url + "/" + tdId

		# Set up Custom Headers for Request
		headers = {'X-Auth-Token':accessToken,
					'accept':'application/json',
					'content-type':'application/json'}

		# Send PUT request to delete Transit Domain Details
		response = requests.delete(url, headers=headers)
		
		# if server deleted transit domain successfully then return true
		if(response.status_code==204):
			return True
		else:
			return False

 	def _deleteAllTransitDomains(self):
 		""" Written for testing purposes"""
 		allTds = self.listTransitDomain()
 		allTds = allTds['transit_domains']

 		# Get ID of all transit domains and delete it one by one
 		for id in allTds:
 			print "Transit Domain -->", id['id']
 			print self.deleteTransitDomain(id['id'])