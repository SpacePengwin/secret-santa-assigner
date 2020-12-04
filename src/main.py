import random
import argparse
import csv
from pprint import pprint
import logging
from datetime import datetime
from os.path import exists, expanduser
import os
import json
from twilio.rest import Client

logging.basicConfig(filename="{}.log".format(datetime.now().date()), level=logging.INFO)

def parse_opts():
	parser = argparse.ArgumentParser()
	parser.add_argument("--setup-twilio", dest="setup_twilio", default=False, action="store_true")
	parser.add_argument("--dry-run", dest="dry_run", default=False, action="store_true")
	args = parser.parse_args()

	return args

def assign_ids(participants):
	output = {}
	ids = []
	while len(ids) < participants:
		n = random.randint(0, participants)
		if n not in ids: # Need to be unique
			ids.append(n)
	with open("input.csv", "r") as f:
		reader = csv.reader(f)
		HEADER = ["name", "number"]
		for row in reader:
			if row != HEADER:
				name = row[0]
				contact = row[1]
				unique_id = random.choice(ids)
				ids.remove(unique_id) # remove from list
				output.update({unique_id: {"name": name,
											"contact_method": contact,
											"assigned_giver": False,
											"gift_assignment_id": None,
											"gift_assignment_name": None}})
		logging.log(logging.INFO, output)
		return output

def pair_ids(i):
	uids = list(i.keys())
	assigned = []
	for uid, values in i.items():
		eligible = uids
		choice = random.choice(eligible)
		while uid == choice:
			choice = random.choice(eligible)
		i[uid].update({"assigned_giver": True,
			"gift_assignment_id": choice,
			"gift_assignment_name": i[choice]["name"]})
		uids.remove(choice)
		assigned.append(choice)
	logging.log(logging.INFO, "Assigned pairs \n\n{}".format(i))


def draft_messages(output, org_title, organizer_name, dollar_limit=None):
	messages = {}
	for unique_id, data in output.items():
		contacted_username = data["name"]
		contact_method = data["contact_method"]
		assigned_name = data["gift_assignment_name"]
		assigned_id = data["gift_assignment_id"]
		msg = '''Hello {}!
You have been entered in by {} for the {} Secret Santa.
You have been assigned to give a present to: {}.
		'''.format(contacted_username, organizer_name, org_title, assigned_name)
		if dollar_limit is not None:
			if dollar_limit != "":
				msg = msg + "\nThe present is limited to: ${}".format(dollar_limit)

		log_msg = "ID: {} assigned to give gift to ID: {}".format(unique_id, assigned_id)
		logging.log(logging.INFO, log_msg)
		messages.update({output[unique_id]["contact_method"]: msg})

	return messages

def twilio_setup():
	credentials_loc = expanduser("~/.twilio_creds")
	account = input("Please enter your Twilio account: ")
	token = input("Please enter your Twilio token: ")
	number = input("Please input your Twilio phone number: ")
	auth = {"account": account,
	"token": token,
	"number": number}
	if not exists(credentials_loc):
		os.makedirs(credentials_loc)
	creds_file = credentials_loc + "/creds.json"
	with open(creds_file, "w") as f:
		json.dump(auth, f)
		f.close()
	print("Saved Twilio credentials, please re-run the program")

def get_auth():
	credentials_loc = expanduser("~/.twilio_creds/creds.json")
	try:
		with open(credentials_loc, "r") as f:
			creds = json.load(f)

			account = creds["account"]
			token = creds["token"]
			number = creds["number"]
	except FileNotFoundError:
			print("No credential file found, please follow twilio-setup below, then re-run\n")
			twilio_setup()
			exit()
	return account, token, number


def send_messages(account, token, twilio_number, messages):
	client = Client(account, token)
	for number, msg in messages.items():
		message = client.messages.create(
			from_=twilio_number,
			body=msg,
			to=number)
		if len(message.sid) > 0:
			print("Sent to {} succesfully!".format(number))
		else:
			print("Check logs...")
	logging.log(logging.INFO, message.sid)

def dry_run(messages):
	for number, msg in messages.items():
		print("---------------------------------------")
		print("Phone number: {}".format(number))
		print("MSG: {}".format(msg))
		print("---------------------------------------")


def setup():
	print("Hello! Welcome to the Secret Santa Sender!")
	sender_name = input("Please input your name so the participants know who sent this: (Press enter for 'Santa Clause') ")
	if sender_name == "":
		sender_name = "Santa Clause"
	org_title = input("Please enter the title for your Secret Santa(family name/company name): ")
	try:
		number_of_participants = int(input("What is the total number of participants?: "))
	except ValueError:
		print("Please enter a number!")
		number_of_participants = int(input("What is the total number of participants?: "))
	dollar_limit = input("What is the dollar limit of each gift?: (For no limit, press enter) ")
	return sender_name, org_title, number_of_participants, dollar_limit

def main():
	args = parse_opts()
	if args.setup_twilio:
		twilio_setup()
		exit()
	account, token, number = get_auth()
	sender_name, org_title, number_of_participants, dollar_limit = setup()
	data = assign_ids(number_of_participants)
	pair_ids(data)
	messages = draft_messages(data, org_title, sender_name, dollar_limit.replace("$", ""))
	if args.dry_run:
		dry_run(messages)
		exit()
	send_messages(account, token, number, messages)


main()


	




