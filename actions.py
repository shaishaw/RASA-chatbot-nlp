from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import pandas as pd
import json
import smtplib
import re
import smtplib

# Importing zomato CSV

ZomatoData = pd.read_csv('zomato.csv')
ZomatoData = ZomatoData.drop_duplicates().reset_index(drop=True)
WeOperate = ['New Delhi', 'Gurgaon', 'Noida', 'Faridabad', 'Allahabad', 'Bhubaneshwar', 'Mangalore', 'Mumbai', 'Ranchi', 'Patna', 'Mysore', 'Aurangabad', 'Amritsar', 'Puducherry', 'Varanasi', 'Nagpur', 'Vadodara', 'Dehradun', 'Vizag', 'Agra', 'Ludhiana', 'Kanpur', 'Lucknow', 'Surat', 'Kochi', 'Indore', 'Ahmedabad', 'Coimbatore', 'Chennai', 'Guwahati', 'Jaipur', 'Hyderabad', 'Bangalore', 'Nashik', 'Pune', 'Kolkata', 'Bhopal', 'Goa', 'Chandigarh', 'Ghaziabad', 'Ooty', 'Gangtok', 'Shimla']

def RestaurantSearch(City,Cuisine,Price):
    min_price=0
    max_price=0
    if Price == 'minimum':
        max_price=300
    elif Price == 'moderate':
        min_price=300
        max_price=700
    elif Price == 'high':
        min_price=700
        max_price=max(ZomatoData['Average Cost for two'])
    else:
        max_price=max(ZomatoData['Average Cost for two'])
	# Adding results on user filters and sorting data on aggregate rating
    restaurant_list = ZomatoData[(ZomatoData['Cuisines'].apply(lambda x: Cuisine.lower() in x.lower())) & (ZomatoData['City'].apply(lambda x: City.lower() in x.lower())) & ( (ZomatoData['Average Cost for two']>min_price) & (ZomatoData['Average Cost for two']<max_price))]
    restaurant_list = restaurant_list.sort_values(by=['Aggregate rating'],ascending=False)
    return restaurant_list[['Restaurant Name','Address','Average Cost for two','Aggregate rating']]

def sendmail(to_email,response):
	# [Mandatory] Please configure your creds for the email function to work
	gmail_user = 'XXXXXX@gmail.com' 
	gmail_password = 'XXXXXXX'
	sent_from = gmail_user
	to = to_email
	subject = 'Foodie list of restaurants search'
	body = response
	email_text = """\
	From: %s
	To: %s
	Subject: %s
	%s
	""" % (sent_from, ", ".join(to), subject, body)
	try:
		server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		server.ehlo()
		server.login(gmail_user, gmail_password)
		server.sendmail(sent_from, to, email_text)
		server.close()
		e_response="Restaurant list has been sent on Email_ID " + to_email
	except:
		e_response="Something went wrong while sending email to: " + to_email
	return e_response

class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_search_restaurants'

	def run(self, dispatcher, tracker, domain):
		#config={ "user_key":"f4924dc9ad672ee8c4f8c84743301af5"}
		regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		price = tracker.get_slot('price')
		MailID = tracker.get_slot('email')
		results = RestaurantSearch(City=loc,Cuisine=cuisine,Price=price)
		resp=""
		if results.shape[0] == 0:
			#resp= "no results"
			dispatcher.utter_message(template="utter_we_dont_operate")
		else:
			for restaurant in results.iloc[:5].iterrows():
				restaurant = restaurant[1]
				resp=resp + F"Found {restaurant['Restaurant Name']} in {restaurant['Address']} rated {restaurant['Aggregate rating']} with avg cost for 2 people: Rs{restaurant['Average Cost for two']}.00 \n\n"
			return_val = sendmail(MailID,resp)
			dispatcher.utter_message("list of restaurants:  "+resp)
			#if(re.search(regex,MailID)):
				# Sending response to email id
			#	return_val = sendmail(MailID,resp)
			#	dispatcher.utter_message(return_val+" List of restaurants sent over email "+resp)
		
		return [SlotSet('location',loc)]

# class ActionSendMail(Action):
# 	def name(self):
# 		return 'action_send_mail'

# 	def run(self, dispatcher, tracker, domain):
# 		regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
# 		MailID = tracker.get_slot('email')
# 		search_result = tracker.get_slot('search_result')
# 		if MailID == 'dummy@gmail.com':
# 			dispatcher.utter_message(template="utter_goodbye")
# 		elif(re.search(regex,MailID)):
# 			#sendmail(MailID,search_result):
# 			dispatcher.utter_message("Restuarant informations has been sent to ")
# 		else:
# 			dispatcher.utter_message(template="utter_goodbye")

# 		return [SlotSet('mail_id',MailID)]
		
