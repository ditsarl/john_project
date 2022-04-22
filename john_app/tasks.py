from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Meeting, Reservation_Taxi, Taxi, Abonnement, Marketing, Marketing_Data, Cash_Book, Cout_Service, Taux
import os

#from twilio.rest import Client
from rapidsms.router import send, lookup_connections
import datetime, time
from dateutil.relativedelta import relativedelta
from django.utils.timezone import datetime, timedelta

from django.utils.crypto import get_random_string




# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
#account_sid = "ACc31b3172384961d8deb00d58f3066de5"
#auth_token = "b9be6d7a4081ac5be290a78fedf6cf82"
#client = Client(account_sid, auth_token)

@shared_task()
def send_Meeting():

	for meeting in Meeting.objects.filter(effectif=True):

		deadline_date = meeting.deadline_date
		deadline_time = meeting.deadline_time
		code = meeting.code

		deadline_date = deadline_date.strftime("%d/%m/%Y")
		deadline_time = deadline_time.strftime("%H:%M")
		now = datetime.now()
		current_date = now.strftime("%d/%m/%Y")
		current_time = now.strftime("%H:%M")

		if deadline_date == current_date:

			if current_time < deadline_time:

				meeting_pass = Meeting.objects.get(code=code)
				meeting_pass.effectif = True
				meeting_pass.save()

			elif current_time == deadline_time:

				personne = meeting.personne
				contact = meeting.contact
				lieu = meeting.lieu
				lameeting_date = meeting.meeting_date
				lemeeting_time = meeting.meeting_time

				meeting_date = lameeting_date.strftime("%d/%m/%Y")
				meeting_time = lemeeting_time.strftime("%H:%M")
				remarque = meeting.remarque

				client_john = meeting.client.contact

				sms_texte = "VOUS AVEZ RENDEZ-VOUS AVEC %s, LE %s A %s. \n LIEU: %s \n CONTACT: %s" % (personne, meeting_date, meeting_time, lieu, contact)
				connections = lookup_connections(backend="message_tester",identities=[contact])
				send(sms_texte, connections=connections)
				#message = client.messages.create(
                #     	#body="Join Earth's mightiest heroes. Like Kevin Bacon.",
                #     	body=sms_texte,
                #     	from_='+12815328452',
                #     	to='+243815098438'
                #)
                

			else:
			
				meeting_pass = Meeting.objects.get(code=code)
				meeting_pass.effectif = False
				meeting_pass.save()

		else:
			
			meeting_pass = Meeting.objects.get(code=code)
			meeting_pass.effectif = False
			meeting_pass.save()

	return 0

@shared_task()
def send_Reservation():

	for reservation in Reservation_Taxi.objects.filter(active=False, cancel=False):

		deadline_date = reservation.date_taxi
		deadline_time = reservation.heure_taxi
		code = reservation.code_reservation

		deadline_date = deadline_date.strftime("%d/%m/%Y")
		deadline_time = deadline_time.strftime("%H:%M")
		now = datetime.now()
		current_date = now.strftime("%d/%m/%Y")
		#current_time = datetime.strptime(str(now), '%H:%M')
		current_time = now + timedelta(minutes=30)
		current_time = current_time.strftime("%H:%M")


		#diff = abs(deadline_time - current_time)

		if deadline_date == current_date:

			if deadline_time == current_time:

				client = reservation.client.nom
				contact_client = reservation.client.contact

				contact_taxi = reservation.Taxi.contact
				marque = reservation.Taxi.marque
				matricule = reservation.Taxi.matricule

				origine = reservation.origine
				destination = reservation.destination
				code = reservation.code_reservation
				cout = reservation.cout

				sms_texte = "VOUS AVEZ RESERVE LE TAXI DE MARQUE %s IMMATRICULE %s POUR LA COURSE DE %s VERS %s. DEPART LE %s A %s. CODE : %s. CONTACT TAXI: %s. COUT : USD %s" % (marque, matricule, origine, destination, deadline_date, deadline_time, code, contact_taxi, cout)
				connections = lookup_connections(backend="message_tester",identities=[contact_client])
				send(sms_texte, connections=connections)

				sms_texte = "VOUS AVEZ ACCEPTE LA RESERVERVATION %s POUR LA COURSE DE %s VERS %s. DEPART LE %s A %s. CONTACT CLIENT: %s. COUT : USD %s" % (code, origine, destination, deadline_date, deadline_time, contact_client, cout)
				connections = lookup_connections(backend="message_tester",identities=[contact_taxi])
				send(sms_texte, connections=connections)
	                

	return 0

@shared_task()
def send_Message():

	for message in Marketing.objects.filter(moderation=True):

		date_deadline = message.date_deadline
		date_deadline = date_deadline.strftime("%d/%m/%Y")
		
		now = datetime.now()
		current_date = now.strftime("%d/%m/%Y")
		current_time = now.strftime("%H:%M")

		sms_texte = message.texte
		bdd = message.source
		client = message.client

		if current_date < date_deadline :

			if current_time == '12:00':

				if bdd == 2:

					for abonnement in Abonnement.objects.filter():

						contact = abonnement.contact

						connections = lookup_connections(backend="message_tester",identities=[contact])
						send(sms_texte, connections=connections)

				else:

					for abonnement in Marketing_Data.objects.filter(client=client):

						contact = abonnement.contact

						connections = lookup_connections(backend="message_tester",identities=[contact])
						send(sms_texte, connections=connections)

	return 0