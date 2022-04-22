from __future__ import absolute_import, unicode_literals
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

#from twilio.twiml.messaging_response import MessagingResponse
from rapidsms.router import send, lookup_connections

from django.utils.crypto import get_random_string
from .models import Abonnement, Marketing, Mobilier, Gift, Gift_Gain, Meeting, Taxi, Reservation_Taxi, Visa, Carnet, Aircraft, Voyage, Horaire, Tarif_Aircraft, Aircraft_Available, Aircraft_Reservation, Pays, Filiale, Facilities, Reservation_Restaurant, Cout_Service, Taux, Cash_Book
from datetime import date
import datetime
import unicodedata
from django.utils.timezone import datetime, timedelta

from extended_choices import Choices
from django.utils.crypto import get_random_string

from ussdrouter.ussdrouting import *
from ussdrouter.searchPage import *

from rest_framework import viewsets
from rest_framework import permissions
from .serializers import UserSerializer, GroupSerializer, AuthTokenSerializer, AbonnementSerializer
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework import generics

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

class UserViewSet(viewsets.ModelViewSet):

	queryset = User.objects.all().order_by('-date_joined')
	serializer_class = UserSerializer

class CreateUserView(generics.CreateAPIView):
	serializer_class = UserSerializer
	http_method_names = ['post',]

	def perform_create(self, serializer):
		instance = serializer.save()
		instance.set_password(instance.password)
		instance.save()

		abonnement = Abonnement.objects.get(code=self.request.data.get("code"))
		user = User.objects.get(username=self.request.data.get("username"))
		abonnement.user = user
		abonnement.save()


class GroupViewSet(viewsets.ModelViewSet):

	queryset = Group.objects.all()
	serializer_class = GroupSerializer

class AbonnementViewSet(viewsets.ModelViewSet):

	queryset = Abonnement.objects.all()
	serializer_class = AbonnementSerializer

class LoginView(ObtainAuthToken):

    serializer_class = AuthTokenSerializer

    def post(self, request, *args,**kwargs):
        serializers = self.serializer_class(data=request.data,context={'request':request})
        serializers.is_valid(raise_exception=True)
        user = serializers.validated_data['user']
        token,created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
			'code': user.abonnement.code,
            'user_id': user.id
        })


#from ussd-router import *

TYPEVILLA = Choices(
	('TERRAIN',1, 'Terrain'),
	('VILLA',2, 'Villa'),
	('APPARTEMENT',3, 'Appartement'),
	('IMMEUBLE',4, 'Immeuble'),
	('AUTRE',5, 'Autre'),
)

PIECE = Choices(
	('1 x 1',1, '1 x 1'),
	('2 x 1',2, '2 x 1'),
	('3 x 1',3, '3 x 1'),
	('4 x 1',4, '4 x 1'),
	('AUTRE',5, 'Autre'),
)

COMMUNE = Choices(
	('BANDALUNGWA',1, 'Bandalungwa'),
	('BARUMBU',2, 'Barumbu'),
	('BUMBU',3, 'Bumbu'),
	('GOMBE',4, 'Gombe'),
	('KALAMU',5, 'Kalamu'),
	('KASA-VUBU',6, 'Kasa-Vubu'),
	('KIMBANSEKE',7, 'Kimbanseke'),
	('KINSHASA',8, 'Kinshasa'),
	('KINTAMBO',9, 'Kintambo'),
	('KISENSO',10, 'Kisenso'),
	('LEMBA',11, 'Lemba'),
	('LIMETE',12, 'Limete'),
	('LINGWALA',13, 'Lingwala'),
	('MAKALA',14, 'Makala'),
	('MALUKU',15, 'Maluku'),
	('MASINA',16, 'Masina'),
	('MATETE',17, 'Matete'),
	('MONT-NGAFULA',18, 'Mont-Ngafula'),
	('NDJILI',19, 'Ndjili'),
	('NGABA',20, 'Ngaba'),
	('NGALIEMA',21, 'Ngaliema'),
	('NGIRI-NGIRI',22, 'Ngiri-Ngiri'),
	('NSELE',23, 'Nsele'),
	('SELEMBAO',24, 'Selembao'),
)

STATUTVISA = Choices(
	('NOUVEAU',1, 'Nouveau'),
	('EN COURS',2, 'En cours de traitement'),
	('ACCEPTE',3, 'Accepté'),
	('REFUS',4, 'Refusé'),
)

JOUR = Choices(
	('DIMANCHE',1,'Dimanche'),
	('LUNDI',2,'Lundi'),
	('MARDI',3,'Mardi'),
	('MERCREDI',4,'Mercredi'),
	('JEUDI',5,'Jeudi'),
	('VENDREDI',6,'Vendredi'),
	('SAMEDI',7,'Samedi'),
)

PASSAGER = Choices(
	('ALDULTE',1,'Adulte'),
	('ENFANT',2,'Enfant'),
	('BEBE',3,'Bébé'),
)
CLASSE = Choices(
	('PREMIERE',1,'Primière'),
	('BUSINESS',2,'Business'),
	('ECONOMIQUE',3,'Economique'),
	('AUTRE',4,'Autre'),
)

STATUTRESERVATION = Choices(
	('NOUVEAU',1, 'Nouveau'),
	('EN COURS',2, 'En cours de traitement'),
	('CONFIRMEE',3, 'Confirmée'),
	('ANNULEE',4, 'Annulée'),
)

MOTIF = Choices(
	('AFFAIRES',1,'Affaires'),
	('ETUDES',2,'Etudes'),
	('SANTE',3,'Santé'),
	('TOURISME',4,'Tourisme'),
)

SERVICE = Choices(
	('ABONNEMENT',1,'Abonnement'),
	('VISA',2,'Visa'),
	('VOYAGE',3,'Voyage'),
	('MARKETING',4,'Marketing'),
	('TAXI SIMPLE',5,'Taxi Simple'),
	('TAXI CLIM',6,'Taxi Clim'),
	('TAXI VIP',7,'Taxi VIP'),
	('MOBILIER',8,'Mobilier'),
	('MUTUELLE DE SANTE',8,'Mutuelle'),
)

@csrf_exempt
def index(request):
	if request.method == 'POST':
		session_id = request.POST.get('sessionId')
		service_code = request.POST.get('serviceCode')
		phone_number = request.POST.get('phoneNumber')

		#text = ussdRouter(text)
		texte = request.POST.get('text')
		#text = text.strip()
		page = Page(texte)
		texte = ussdRouter(texte)
		
		level = texte.split('*')
		#texte = ussdRouter(texte)


		response = ""

		if texte == "" :
			response = "CON BIENVENU(E) CHEZ DISCOVERY FACILITIES SERVICES (DFS). \n VEUILLEZ TAPER LE CHIFFRE CORRESPONDANT A VOTRE CHOIX \n \n"
			# response .= "1. My Account \n"
			#response += "1. ENREGISTRER UN HOPITAL \n"
			#response += "2. DECLARER UNE NAISSANCE \n"
			#response += "3. DECLARER UN ENFANT A LA COMMUNE"
			response += "1. Abonnement \n"
			response += "2. Annuaire \n"
			response += "3. Mass marketing (ENVOYEZ-NOUS VOTRE BDD DE NUMEROS AU FORMAT CSV OU EXCEL A L'ADRESSE:support@di-data-dfs.com) \n"
			response += "4. Carnet d'adresses \n"
			response += "5. Immobilier \n"
			response += "6. Services VISA \n"
			response += "7. Agence de voyage \n"
			response += "8. Cadeau surprise \n"
			response += "9. Rendez-vous \n"
			response += "10. Taxi express \n"
			response += "11. Mutuelle de santé \n"
			response += "12. Quitter"

		#elif text == "1":
			#response = "END My Phone number is {0}".format(phone_number)
		#	response = "END My Phone number is %s" % session_id

		#elif text == "2":
		#	a = text
		#	response = "END VOUS AVEZ TAPE %s" % level[0]

		else:

			try:
				level[1]

				try:
					level[2]

					try:
						level[3]

						try:
							level[4]

							try:
								level[5]

								try:
									level[6]

									try:
										level[7]

										try:
											level[8]

											try:
												level[9]

												try:
													level[10]

													try:
														level[11]

														try:
															level[12]

															try:
																level[13]

																try:
																	level[14]

																	try:
																		level[15]

																		try:
																			level[16]																				

																		except:

																			if level[0] == "6":

																				if level[1] == "1":

																					client = Abonnement.objects.get(contact=phone_number)
																					pays = Pays.objects.get(codePays=level[2])
																					nbrVisa = level[3]
																					nbreIn = level[4]

																					anIn = level[5][-4:]
																					jourIn = level[5][:2]
																					moisIn = level[5][:5]
																					lemoisIn = moisIn[-2:]

																					#dateIn = datetime.date(int(anIn), int(lemoisIn), int(jourIn))
																					dateIn = datetime.strptime(level[5], '%d/%m/%Y')

																					anOut = level[6][-4:]
																					jourOut = level[6][:2]
																					moisOut = level[6][:5]
																					lemoisOut = moisOut[-2:]

																					#dateOut = datetime.date(int(anOut), int(lemoisOut), int(jourOut))
																					dateOut = datetime.strptime(level[6], '%d/%m/%Y')

																					typeDoc = level[7]
																					nomContact = level[8].upper()

																					an = level[9][-4:]
																					jour = level[9][:2]
																					mois = level[9][:5]
																					lemois = mois[-2:]

																					#dateNais = datetime.date(int(an), int(lemois), int(jour))
																					dateNais = datetime.strptime(level[9], '%d/%m/%Y')

																					nation = level[10].upper()
																					adresse = level[11].upper()
																					email = level[12].lower()

																					contact = phone_number
																					profession = level[13].upper()
																					objet = level[14].upper()
																					info = level[15].upper()

																					numdemande = get_random_string(length=8, allowed_chars='0123456789')

																					if Visa.objects.filter(numdemande=numdemande):
																						numdemande = get_random_string(length=8, allowed_chars='0123456789')

																					Visa.objects.create(client=client, pays=pays, nbrVisa=nbrVisa, nbreIn=nbreIn, dateIn=dateIn, dateOut=dateOut, typeDoc=typeDoc, nomContact=nomContact, dateNais=dateNais, nation=nation, adresse=adresse, email=email, contact=contact, profession=profession, objet=objet, info=info, numdemande=numdemande)

																					response = "END L'enregistrement de votre demande de visa a abouti. Son code est  : %s. Veuillez continuer en indiquant les informations de votre hote." % (numdemande)

																					cashNumber = get_random_string(length=15, allowed_chars='0123456789')
																					taux = Taux.objects.get(actif=True).taux

																					service_cout = Cout_Service.objects.get(service=2)

																					cout = service_cout.cout
																					pourcentageDFS = service_cout.pourcentageDFS
																					pourcentagePartenaire = service_cout.pourcentagePartenaire
																					service = service_cout.service

																					gainDFS_USD = cout * pourcentageDFS
																					gainDFS_CDF = gainDFS_USD * taux
																					gainDFS_USD = round(gainDFS_USD,2)
																					gainDFS_CDF = round(gainDFS_CDF)
																					gainPartenaire_USD = cout * pourcentagePartenaire
																					gainPartenaire_CDF = gainPartenaire_USD * taux
																					gainPartenaire_USD = round(gainPartenaire_USD,2)
																					gainPartenaire_CDF = round(gainPartenaire_CDF)
																					Cash_Book.objects.create(client=client,service=service,reference=numdemande,cashNumber=cashNumber, gainDFS_USD=gainDFS_USD, gainDFS_CDF=gainDFS_CDF, gainPartenaire_USD=gainPartenaire_USD, gainPartenaire_CDF=gainPartenaire_CDF)
																										

																	except:

																		if level[0] == "6":

																			if level[1] == "1":

																				response = "CON Autres informations (Vous pouvez ici l'objet concret du voyage ou le type de document s'il ne figure pas sur la liste):"

																except:

																	if level[0] == "6":

																		if level[1] == "1":

																			response = "CON Taper l'objet du voyage : \n 1. TOURISME \n 2. AFFAIRES \n 3. VISITE A LA FAMILLE OU A DES AMIS \n 4. CULTURE \n 5. SPORTS \n 6. VISITE OFFICIELLE \n 7. RAISONS MEDICALES \n 8. ETUDES \n 9. TRANSIT AEROPORTUAIRE \n 10. AUTRE"

															except:

																if level[0] == "6":

																	if level[1] == "1":
																		response = "CON Taper la profession du (de la) demandeur(euse) :"

														except:

															if level[0] == "6":
																if level[1] == "1":
																	response = "CON Taper l'adresse email du (de la) demandeur(euse) :"

													except:
														if level[0] == "1":
															if level[1] == "2":
																if level[10] == "1":
																	code = get_random_string(length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

																	response = "END Merci d'avoir souscrit aux services de DFS. Veuillez bien nous contacter au 01515 avant d'utiliser nos services. \n Nous osons croire qu'ils vous serons très utiles. Merci de nous faire confiance."
																	Abonnement.objects.create(typepersonne=level[1], nom=level[2].upper(), nomContact=level[4].upper(),fonctionContact=level[5].upper(), sigle=level[3].upper(), adresse=level[6].upper(), contact=phone_number, contact2=level[7], contact3=level[8], email=level[9].lower(), code=code)
																	sms_texte = "Merci d'avoir souscrit aux services de DFS. Votre IDENTIFIANT est %s. Gardez-le jalousement. \nVous pouvez consulter vos DONNEES en ligne sur https://www.di-data-dfs.com/"

																	connections = lookup_connections(backend="message_tester",identities=[phone_number])
																	send(sms_texte, connections=connections)
																	
																else:
																	response = "END Merci de votre visite chez DFS. Vous pouvez nous appeler AU 01515 pour des plus amples informations ou consulter notre site https://www.di-data-dfs.com/"


														if level[0] == "6":
															response = "CON Taper l'adresse physique du (de la) demandeur(euse) :"
															
												except:
													if level[0] == "1":
														if level[1] == "2":
															response = "CON Voulez-vous vraiment vous abonner chez DFS ? \n Taper 1 POUR ACCEPTER (COUT DE L'ABONNEMENT 25 UNITES/JOUR) ou 2 POUR ANNULER."

													elif level[0] == "6":
														try:
															ladateNais = datetime.strptime(level[9], '%d/%m/%Y')

															response = "CON Taper le pays d'origine du (de la) demandeur(euse) :"
														except:
															response = "CON Format date de naissance incorrect.\n Taper 00 pour revenir au menu d'avant OU 0 pour le menu principal."

													elif level[0] == "9":

														client = Abonnement.objects.get(contact=phone_number, actif=True)
														if level[1] == "1":

															slug = get_random_string(length=10, allowed_chars='0123456789')

															an_meeting = level[4][-4:]
															jour_meeting = level[4][:2]
															mois_meeting = level[4][:5]
															lemois_meeting = mois_meeting[-2:]

															an_deadline = level[6][-4:]
															jour_deadline = level[6][:2]
															mois_deadline = level[6][:5]
															lemois_deadline = mois_deadline[-2:]

															#meeting_date = datetime.date(int(an_meeting), int(lemois_meeting), int(jour_meeting))
															meeting_date = datetime.strptime(level[4], '%d/%m/%Y')
															meeting_time = datetime.strptime(level[5], '%H:%M')

															#deadline_date = datetime.date(int(an_deadline), int(lemois_deadline), int(jour_deadline))
															deadline_date = datetime.strptime(level[6], '%d/%m/%Y')
															deadline_time = datetime.strptime(level[7], '%H:%M')

															if level[8][:4] != "+243":
																contact = "+243" + level[8][-9:]
															else:
																contact = level[8]

															Meeting.objects.create(client=client, personne=level[2].upper(), lieu=level[3].upper(), meeting_date=meeting_date,meeting_time=meeting_time,deadline_date=deadline_date, deadline_time=deadline_time, contact=contact, code=slug, remarque=level[9].upper())
															response = "END Votre rendez-vous est bien pris en compte. Vous recevrez un rappel le %s %s" % (level[6], level[7])													
#																			

											except:

												if level[0] == "1":
													if level[1] == "1":
														if level[8] == "1":
															code = get_random_string(length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
															response = "END Bienvenu(e) chez DFS %s ! \n Vous pouvez maintenant utiliser nos services OU apeller au 01515 pour tout renseignement. \n Merci pour votre confiance. " % (level[2].upper())
															Abonnement.objects.create(typepersonne=level[1], nom=level[2].upper(), sexe=level[3].upper(), adresse=level[4].upper(), contact=phone_number, contact2=level[5], contact3=level[6], email=level[7].lower(), code=code)
															sms_texte = "Merci d'avoir souscrit aux services de DFS. Votre identifiant est %s. Gardez-le jalousement." % (code)

															connections = lookup_connections(backend="message_tester",identities=[phone_number])
															send(sms_texte, connections=connections)

															service = 1

															cout = Cout_Service.objects.get(service=service).cout
															pourcentageDFS = Cout_Service.objects.get(service=service).pourcentageDFS
															pourcentagePartenaire = Cout_Service.objects.get(service=service).pourcentagePartenaire

															cashNumber = get_random_string(length=15, allowed_chars='0123456789')
															taux = Taux.objects.get(actif=True).taux

															gainDFS_USD = cout * pourcentageDFS
															gainDFS_CDF = gainDFS_USD * taux
															gainDFS_USD = round(gainDFS_USD,2)
															gainDFS_CDF = round(gainDFS_CDF)
															gainPartenaire_USD = cout * pourcentagePartenaire
															gainPartenaire_CDF = gainPartenaire_USD * taux
															gainPartenaire_USD = round(gainPartenaire_USD,2)
															gainPartenaire_CDF = round(gainPartenaire_CDF)

															client = Abonnement.objects.get(contact=phone_number)
															reference = code

															if phone_number[:6] == "+24381" or phone_number[:6] == "+24382":
																partenaire = Abonnement.objects.get(nom='VODACOM')
															elif phone_number[:6] == "+24389" or phone_number[:6] == "+24385" or phone_number[:6] == "+24384":
																partenaire = Abonnement.objects.get(nom='ORANGE')
															elif phone_number[:6] == "+24397" or phone_number[:6] == "+24398" or phone_number[:6] == "+24399":
																partenaire = Abonnement.objects.get(nom='AIRTEL')
															else:
																partenaire = Abonnement.objects.get(nom='AFRICELL')

															Cash_Book.objects.create(client=client,service=service,reference=reference,cashNumber=cashNumber, gainDFS_USD=gainDFS_USD, gainDFS_CDF=gainDFS_CDF, gainPartenaire_USD=gainPartenaire_USD, gainPartenaire_CDF=gainPartenaire_CDF, partenaire=partenaire)

														else:
															response = "END Merci de votre visite chez DFS. Vous pouvez nous appeler AU 01515 pour des plus amples informations ou consulter notre site https://www.di-data-dfs.com/"
													else:
														response = "CON Taper votre adresse e-mail (laissez vide si vous n'en avez pas):"
												elif level[0] == "6":

													response = "CON Taper la date de naissance du (de la) demandeur(euse) :"

												elif level[0] == "7":
													if level[1] == "3":
														slug = get_random_string(length=10, allowed_chars='0123456789')
														client = Abonnement.objects.get(contact=phone_number, actif=True)
														aircraft = Aircraft.objects.get(code=level[2].upper())
														an_vol = level[4][-4:]
														jour_vol = level[4][:2]
														mois_vol = level[4][:5]
														lemois_vol = mois_vol[-2:]
														date_vol = datetime.date(int(an_vol), int(lemois_vol), int(jour_vol))
										

														Aircraft_Reservation.objects.create(client=client,aircraft=aircraft,numvol=level[3].upper(),dateVoyage=date_vol,classe=level[5],adulte=level[6],child=level[7],infant=level[8],code=slug)
														sms_texte = "Merci d'utiliser les services e DFS. Votre code de reservation est %s" % (code)

														connections = lookup_connections(backend="message_tester",identities=[phone_number])
														send(sms_texte, connections=connections)

														response = "END Votre demande de reservation est bien prise en compte. Votre code de demande est : %s Nous reviendrons vers vous pour tout autre information." % (slug)
												elif level[0] == "9":
													response = "CON Taper une remarque ou laisser vide :"

												elif level[0] == "10":
													client = Abonnement.objects.get(contact=phone_number, actif=True)
													if level[1] == "2":
														slug = get_random_string(length=10, allowed_chars='0123456789')

														an_taxi = level[2][-4:]
														jour_taxi = level[2][:2]
														mois_taxi = level[2][:5]
														lemois_taxi = mois_taxi[-2:]

														#date_taxi = datetime.date(int(an_taxi), int(lemois_taxi), int(jour_taxi))
														date_taxi = datetime.strptime(level[2], '%d/%m/%Y')
														heure_taxi = datetime.strptime(level[3], '%H:%M')

														if level[7] == "1":
															vip = True
														else:
															vip = False

														if level[6] == "1":
															climatisation = True
														else:
															climatisation = False

														if level[7] == "1":
															cout = Cout_Service.objects.get(service=7).cout
															service = 7
															pourcentageDFS = Cout_Service.objects.get(service=7).pourcentageDFS
															pourcentagePartenaire = Cout_Service.objects.get(service=7).pourcentagePartenaire
														elif level[6] == "1" and level[7] == "1":
															cout = Cout_Service.objects.get(service=7).cout
															service = 7
															pourcentageDFS = Cout_Service.objects.get(service=7).pourcentageDFS
															pourcentagePartenaire = Cout_Service.objects.get(service=7).pourcentagePartenaire
														elif level[6] == "1" and level[7] != "1":
															cout = Cout_Service.objects.get(service=6).cout
															service = 6
															pourcentageDFS = Cout_Service.objects.get(service=6).pourcentageDFS
															pourcentagePartenaire = Cout_Service.objects.get(service=6).pourcentagePartenaire
														else:
															cout = Cout_Service.objects.get(service=5).cout
															service = 5
															pourcentageDFS = Cout_Service.objects.get(service=5).pourcentageDFS
															pourcentagePartenaire = Cout_Service.objects.get(service=5).pourcentagePartenaire

														if level[8] == "1":
															if Taxi.objects.filter(actif=True, vip=vip) :
																Reservation_Taxi.objects.create(client=client,date_taxi=date_taxi,heure_taxi=heure_taxi,origine=level[4].upper(),destination=level[5].upper(),vip=vip,climatisation=climatisation,code_reservation=slug, cout=cout)

																response = "END Votre reservation est bien prise en compte. Vous recevrez une notification avec le contact de votre taxi dans les prochaines minutes. En cas de problème, contactez-nous AU 01515.\n Code de reservation: %s \n montant de la course : USD %s (PAYABLE PAR MONNAIE ELECTRONIQUE)." % (slug, cout)

																for taxi in Taxi.objects.filter(actif=True, vip=vip):
																	contact = taxi.contact

																	if climatisation == True:
																		clim = "AVEC CLIMATISATION"
																	else:
																		clim = "SANS CLIMATISATION"
																	date = date_taxi.strftime("%d/%m/%Y")
																	heure = heure_taxi.strftime("%H:%M")

																	sms_texte = "Le client %s a besoin d'un taxi pour la course %s - %s. Depart: le %s %s. Contact: %s. Option: %s. Montant de la course: USD %s. Si ceci vous interesse, accepter la reservation en indiquant le code suivant: %s" % (client.nom, level[4].upper(), level[5].upper(), date, heure, contact, clim, cout, slug)

																	connections = lookup_connections(backend="message_tester",identities=[contact])
																	send(sms_texte, connections=connections)

																	# Cash Book
																cashNumber = get_random_string(length=15, allowed_chars='0123456789')
																taux = Taux.objects.get(actif=True).taux

																gainDFS_USD = cout * pourcentageDFS
																gainDFS_CDF = gainDFS_USD * taux
																gainDFS_USD = round(gainDFS_USD,2)
																gainDFS_CDF = round(gainDFS_CDF)
																gainPartenaire_USD = cout * pourcentagePartenaire
																gainPartenaire_CDF = gainPartenaire_USD * taux
																gainPartenaire_USD = round(gainPartenaire_USD,2)
																gainPartenaire_CDF = round(gainPartenaire_CDF)
																Cash_Book.objects.create(client=client,service=service,reference=slug,cashNumber=cashNumber, gainDFS_USD=gainDFS_USD, gainDFS_CDF=gainDFS_CDF, gainPartenaire_USD=gainPartenaire_USD, gainPartenaire_CDF=gainPartenaire_CDF)

															else:
																response = "END Aucun taxi n'est disponible pour l'instant."
														else:
															response = "CON Reservation non prise en compte ! Contactez-nous AU 01515 pour toute information.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

										except:

											if level[0] == "1":
												if level[1] == "1":
													response = "CON Voulez-vous vraiment vous abonner chez DFS ? \n Taper 1 POUR ACCEPTER (COUT DE L'ABONNEMENT 25 UNITES/JOUR) ou 2 POUR ANNULER."
												else:
													response = "CON Taper votre 3e NUMERO de contact (laisser vide s'il n'y en a pas):"
											elif level[0] == "2":
												if level[1] == "4":
													if level[7] == "1":
														client = Abonnement.objects.get(contact=phone_number)
														restaurant = Abonnement.objects.get(id=level[2])
														nbrCouvert = level[3]
														personne = level[4].upper()

														an_reservation = level[5][-4:]
														jour_reservation = level[5][:2]
														mois_reservation = level[5][:5]
														lemois_reservation = mois_reservation[-2:]

														date_reservation = datetime.strptime(level[5], '%d/%m/%Y')
														heure_reservation = datetime.strptime(level[6], '%H:%M')

														slug = get_random_string(length=10, allowed_chars='0123456789')
														
														Reservation_Restaurant.objects.create(client=client, restaurant=restaurant,nbrCouvert=nbrCouvert, personne=personne, date_reservation=date_reservation, heure_reservation=heure_reservation, code_reservation=slug)
														#date_reservation = datetime.strptime(date_reservation, '%d/%m/%Y')
														date_reservation = date_reservation.strftime("%d/%m/%Y")
														heure_reservation = heure_reservation.strftime("%H:%M")

														response = "END Votre reservation est bien prise en compte. Le code de reservation est %s. Vous reevrez un sms de confirmation ou de rappel." % (slug)

														sms_texte = "Demande de reservation %s pour une table de %s couvert(s) au nom de %s le %s %s. Contact: %s" % (slug, nbrCouvert, personne, date_reservation, heure_reservation, client.contact)

														contact = restaurant.contact

														connections = lookup_connections(backend="message_tester",identities=[contact])
														send(sms_texte, connections=connections)

														cashNumber = get_random_string(length=15, allowed_chars='0123456789')
														taux = Taux.objects.get(actif=True).taux

														service_cout = Cout_Service.objects.get(service=9)

														cout = service_cout.cout
														pourcentageDFS = service_cout.pourcentageDFS
														pourcentagePartenaire = service_cout.pourcentagePartenaire
														partenaire = restaurant
														service = service_cout.service

														gainDFS_USD = cout * pourcentageDFS
														gainDFS_CDF = gainDFS_USD * taux
														gainDFS_USD = round(gainDFS_USD,2)
														gainDFS_CDF = round(gainDFS_CDF)
														gainPartenaire_USD = cout * pourcentagePartenaire
														gainPartenaire_CDF = gainPartenaire_USD * taux
														gainPartenaire_USD = round(gainPartenaire_USD,2)
														gainPartenaire_CDF = round(gainPartenaire_CDF)
														Cash_Book.objects.create(client=client,service=service,reference=slug,cashNumber=cashNumber, gainDFS_USD=gainDFS_USD, gainDFS_CDF=gainDFS_CDF, gainPartenaire_USD=gainPartenaire_USD, gainPartenaire_CDF=gainPartenaire_CDF, partenaire=partenaire)


													else:
														response = "CON Merci pour votre visite. Vous pouvez nous appeler au 01515 pour de plus amples informations.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
											elif level[0] == "6":
												if level[1] == "1":
													response = "CON Taper les noms du (de la) demandeur(euse) du VISA :"
												else:
													visa = Visa.objects.get(numdemande=level[2])

													visa.hote = level[3].upper()
													visa.adresseHote = level[4].upper()
													visa.contactHote = level[5]
													visa.emailHote = level[6].lower()
													visa.finance = level[7]

													visa.save()

													response = "END Votre dossier de demande est bien rempli. Nous vous contacterons pour tout autre infromation et vous informerons sur l'avancement du dossier."

											elif level[0] == "7":
												if level[1] == "3":
													response = "CON Taper le nombre de BEBES (ENFANT DE MOINS DE 2 ANS) :"
											
											elif level[0] == "9":
												try:
													time_rappel = datetime.strptime(level[7], '%H:%M')
													response = "CON Taper le NUMERO de contact :"
												except:
													response = "CON Format heure incorrect. Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

											elif level[0] == "10":
												client = Abonnement.objects.get(contact=phone_number, actif=True)
												contact = client.contact
												email = client.email
												if level[1] == "2":
													if level[7] == "1":
														cout = Cout_Service.objects.get(service=7).cout
														response = "CON Le montant de la course est USD %s. Taper 1 POUR VALIDER ou 2 POUR ANNULER LA RESERVATION :" % (cout)
													elif level[7] == "1" and level[6] == "1":
														cout = Cout_Service.objects.get(service=7).cout
														response = "CON Le montant de la course est USD %s. Taper 1 POUR VALIDER ou 2 POUR ANNULER LA RESERVATION :" % (cout)
													elif level[7] != "1" and level[6] == "1":
														cout = Cout_Service.objects.get(service=6).cout
														response = "CON Le montant de la course est USD %s. Taper 1 POUR VALIDER ou 2 POUR ANNULER LA RESERVATION :" % (cout)													
													else:
														cout = Cout_Service.objects.get(service=5).cout
														response = "CON Le montant de la course est USD %s. Taper 1 POUR VALIDER ou 2 POUR ANNULER LA RESERVATION :" % (cout)


									except:

										if level[0] == "1":
											if level[1] == "2":
												response = "CON Taper votre second NUMERO de contact (laisser vide s'il n'y en a pas):"												
											else:
												response = "CON Taper votre adresse e-mail (laisser vide s'il n'y en a pas):"
										elif level[0] == "2":
											if level[1] == "4":
												try:
													heureReservation = datetime.strptime(level[6], '%H:%M')
													response = "CON Voulez-vous vraiment reserver une table ? Taper 1 pour accepter et 2 pour annuler:"
												except:
													response = "CON Format heure incorrect.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

										elif level[0] == "5":
											client = Abonnement.objects.get(contact=phone_number, actif=True, annuaire=True)
											contact = client.contact
											email = client.email
											if level[1] == "1":										
												if level[2] == "1":

													if level[3] == "1":
														Mobilier.objects.create(typevilla=level[3], commune=level[4], superficie=level[5], cout=level[6],vente=True,client=client)
													elif level[3] == "2" or level[3] == "3":
														Mobilier.objects.create(typevilla=level[3], commune=level[4], piece=level[5], cout=level[6],vente=True,client=client)
													else:
														Mobilier.objects.create(typevilla=level[3], commune=level[4], etage=level[5], cout=level[6],vente=True,client=client)
													response = "END Votre bien est bien pris en compte. Veuillez bien nous contacter au 01515 pour la mise en vente."

											else:

												if level[2] == "1":

													if level[3] == "1":
														Mobilier.objects.create(typevilla=level[3], commune=level[4], superficie=level[5], cout=level[6],vente=False,client=client)
													elif level[3] == "2" or level[3] == "3":
														Mobilier.objects.create(typevilla=level[3], commune=level[4], piece=level[5], cout=level[6],vente=False,client=client)
													else:
														Mobilier.objects.create(typevilla=level[3], commune=level[4], etage=level[5], cout=level[6],vente=False,client=client)
													response = "END Votre bien est bien pris en compte. Veuillez bien nous contacter au 01515 pour la mise en vente."
											
										elif level[0] == "6":
											if level[1] == "1":

												try:
													ladateOut = datetime.strptime(level[6], '%d/%m/%Y')

													response = "CON Taper le type de document de voyage :\n 1. PASSEPORT ORDINAIRE \n 2. PASSEPORT DIPLOMATIQUE \n 3. PASSEPORT DE SERVICE \n 4. PASSEPORT OFFICIEL \n 5. PASSEPORT SPECIAL \n 6. AUTRE DOCUMENT"
												#else:
												#	response = "END FORMAT DATE DE SORTIE INCORRECT."

												except:
													response = "CON Format date de sortie incorrect.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

											else:
												response = "CON Taper le mode de financement de votre voyage :\n  1. PAR VOUS-MEME \n 2. PAR UN GARANT"												


										elif level[0] == "7":
											if level[1] == "3":
												response = "CON Taper le nombre d'ENFANTS (2 ANS OU PLUS) :"
											elif level[1] == "8":
												if level[2] == "1":
													client = Abonnement.objects.get(contact=phone_number, actif=True)
													pays = Pays.objects.get(codePays=level[3])
													if level[5] == "":
														level[5] = 0
													filiale = Filiale.objects.get(code=level[5])
													motif = level[4]
													observation = level[6].upper()

													slug = get_random_string(length=15, allowed_chars='0123456789')

													Facilities.objects.create(client=client, pays=pays, filiale=filiale, motif=motif, observation=observation, numdemande=slug)
													response = "END Votre demande est bien prise en compte. Nous vous contacterons pour tout autre information. Votre code de demande est %s" % (slug)
										
										elif level[0] == "9":
											try:
												rappel_meeting = datetime.strptime(level[6], '%d/%m/%Y')
												date_meeting = datetime.strptime(level[4], '%d/%m/%Y')

												if rappel_meeting > date_meeting:
													response = "CON Veuillez revoir la date de rappel. Elle est SUPERIEURE A LA DATE de rendez-vous. Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
												else:
													response = "CON Taper l'heure de rappel :"
											except:
												response = "CON Format de date incorrect. Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
										elif level[0] == "10":
											if level[1] == "2":
												response = "CON Avez-vous besoin d'un taxi VIP ? (TAPER 1 POUR OUI OU 2 POUR NON) :"
								except:

									if level[0] == "1":
										if level[1] == "2":
											response = "CON Taper votre adresse :"
										else:
											response = "CON Taper votre 3e NUMERO de contact (laisser vide s'il n'y en a pas):"
									elif level[0] == "2":
										if level[1] == "4":
											try:
												ladateOut = datetime.strptime(level[5], '%d/%m/%Y')
												response = "CON Taper l'heure pour la reservation :"
											except:
												response = "CON Format date incorrect.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

									elif level[0] == "5":
										if level[2] == "1":
											response = "CON Taper le montant du bien mis en vente ou le montant du loyer (EN USD)"
										else:
											message = {}
											n = 0
											messages = ""

											if level[1] == "1":												

												if Mobilier.objects.filter(typevilla=level[3], commune=level[4], cout__lte=int(level[5]), vente=True, actif=True) :

													nbr_records = Mobilier.objects.filter(typevilla=level[3], commune=level[4], cout__lte=int(level[5]), vente=True, actif=True).count()

													for mobilier in Mobilier.objects.filter(typevilla=level[3], commune=level[4], cout__lte=int(level[5]), vente=True, actif=True).order_by('cout')[((page-1)*2):(page*2)]:

														typevilla = TYPEVILLA.for_value(mobilier.typevilla).display
														piece = PIECE.for_value(mobilier.piece).display
														etage = mobilier.etage
														superficie = mobilier.superficie
														commune = COMMUNE.for_value(mobilier.commune).display
														cout = mobilier.cout
														contact = "01515"
														email = "info@di-data-dfs.com"
														url = mobilier.adresseUrl

														n += 1

														if typevilla == "Villa" or typevilla == "Appartement":
															type_immeuble = piece
														elif typevilla == "Immeuble":
															type_immeuble = "R+" + str(etage)
														elif typevilla == "Terrain":
															type_immeuble = str(superficie) + " m2"
														else:
															type_immeuble = ""

														if url == None:
															url = ""


														message["number"] = n
														message["typevilla"] = typevilla
														message["type_immeuble"] = type_immeuble
														message["commune"] = commune
														message["cout"] = str(cout)
														message["contact"] = contact
														message["email"] = email
														message["url"] = url

														messages = messages + "%s. \n %s %s à %s pour USD %s. \n Contact: %s \n %s \n %s " % (message["number"], message["typevilla"], message["type_immeuble"], message["commune"], message["cout"], message["contact"], message["email"], message["url"])

													response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/2), page, messages)

												else:
													response = "CON Aucun bien correspondant n'est pas mis en vente. Recommendez la recherche ou contactez-nous au 01515.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
											else:

												if Mobilier.objects.filter(typevilla=level[3], commune=level[4], cout__lte=int(level[5]), vente=False, actif=True) :

													for mobilier in Mobilier.objects.filter(typevilla=level[3], commune=level[4], cout__lte=int(level[5]), vente=False, actif=True).order_by('cout'):

														typevilla = TYPEVILLA.for_value(mobilier.typevilla).display
														piece = PIECE.for_value(mobilier.piece).display
														etage = mobilier.etage
														superficie = mobilier.superficie
														commune = COMMUNE.for_value(mobilier.commune).display
														cout = mobilier.cout
														contact = "01515"
														email = "info@di-data-dfs.com"
														url = mobilier.adresseUrl

														n += 1

														if piece != "Autre":
															type_immeuble = piece
														elif etage != None:
															type_immeuble = "R+ " + str(etage)
														else:
															type_immeuble = str(superficie) + " m2"

														if url == None:
															url = ""


														message["number"] = n
														message["typevilla"] = typevilla
														message["type_immeuble"] = type_immeuble
														message["commune"] = commune
														message["cout"] = str(cout)
														message["contact"] = contact
														message["email"] = email
														message["url"] = url

														messages = messages + "%s. \n %s %s à %s pour USD %s. \n Contact: %s \n %s \n %s " % (message["number"], message["typevilla"], message["type_immeuble"], message["commune"], message["cout"], message["contact"], message["email"], message["url"])

													response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/2), page, messages)

												else:
													response = "CON Aucun bien correspondant n'est pas mis en location. Recommendez la recherche ou contactez-nous au 01515.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."												

									elif level[0] == "6":

										if level[1] == "1":

											try:
												ladateIn = datetime.strptime(level[5], '%d/%m/%Y')

												response = "CON TAPER LA DATE DE SORTIE PREVUE :"
											#else:
											#	response = "END FORMAT DATE D'ENTREE INCORRECT."

											except:
												response = "CON Format date incorrect.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

										else:
											response = "CON Taper l'adresse e-mail de votre HOTE :"

									elif level[0] == "7":
										message = {}
										n = 0
										messages = ""
										if level[1] == "3":
											response = "CON Taper le nombre D'ADULTES :"
										elif level[1] == "4":
											voyage = Voyage.objects.get(origine=level[3].upper().strip(), destination=level[4].upper().strip())
											aircraft = Aircraft.objects.get(code=level[2].upper())

											if Tarif_Aircraft.objects.filter(aircraft=aircraft, voyage=voyage, classe=level[5]):

												nbr_records = Tarif_Aircraft.objects.filter(aircraft=aircraft, voyage=voyage, classe=level[5]).count()

												for tarif in Tarif_Aircraft.objects.filter(aircraft=aircraft, voyage=voyage, classe=level[5]).order_by('passager')[((page-1)*2):(page*2)]:

													passager = PASSAGER.for_value(tarif.passager).display
													montant = tarif.tarif

													n += 1

													message["number"] = n
													message["passager"] = passager
													message["montant"] = montant

													messages = messages + "%s. %s: %s USD \n" % (message["number"], message["passager"], message["montant"])

												response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/2), page, messages)

											else:
												response = "CON Il n'y a aucun tarif pour ce vol pour l'instant. Veuillez essayer plus tard.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
										elif level[1] == "8":
											if level[2] == "1":
												if level[5] == "":
													level[5] = 0
												if Filiale.objects.filter(code=level[5]):
													response = "CON taper d'autres informations ou laissez vide."
												else:
													response = "CON Veuillez indiquer une filiale.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
									

									elif level[0] == "9":
										try:
											time_meeting = datetime.strptime(level[5], '%H:%M')
											response = "CON Taper la date de rappel :"
										except:
											response = "CON Format heure incorrect. Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
									elif level[0] == "10":
										if level[1] == "1":
											client = Abonnement.objects.get(contact=phone_number, actif=True, annuaire=True)
											contact = client.contact
											if level[4] == "1":
												climatisation=True
											else:
												climatisation=False
										
											if level[5] == "1":
												Taxi.objects.create(client=client,matricule=level[3].upper(),marque=level[2].upper(),climatisation=climatisation,contact=contact)
												response = "END Votre taxi est pris en compte DFS. Veuillez nous contater AU 01515 pour signature de contrat."
											else:
												response = "CON Enregistrement non pris en compte !. Contactez-nous au 01515 pour toute information.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
										elif level[1] == "2":
											response = "CON Avez-vous besoin d'un taxi avec climatisation ? (TAPER 1 POUR OUI OU 2 POUR NON) :"
							except:		

								if level[0]=="1" :
									if level[1] == "1":
										response = "CON Taper votre second NUMERO de contact (laisser vide s'il n'y en a pas):"
									else:
										response = "CON Taper votre SECTEUR D'ACTIVITE :"
								elif level[0] == "2":
									if level[1] == "4":
										if level[4] != "":
											response = "CON Taper la date de reservation :"
										else:
											response = "CON Veuillez indiquer le nom du contact pour la reservation.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

								elif level[0] == "3":
									if level[4] == "1":
										client = Abonnement.objects.get(contact=phone_number, actif=True, annuaire=True)
										contact = client.contact
										email = client.email

										date_deadline = datetime.today() + timedelta(int(level[3])+1)

										texte = level[1] + "\n Message de %s. Contact: %s, email: %s" % (client, contact, email)
										Marketing.objects.create(texte=texte.upper(), source=level[2], frequence=level[3], date_deadline=date_deadline, client=client)
										#date_deadline = datetime.today().strftime("%d/%m/%Y")
										response = "END Votre message est bien pris en compte. Nous allons l'envoyer pendant %s jours A PARTIR D'AUJOURD'HUI A 12H00 ET 18H00." % (level[3])
									else:
										response = "CON Merci de votre visite chez DFS. Vous pouvez nous appeler AU 01515 pour des plus amples informations ou consulter notre site https://www.di-data-dfs.com/"
								elif level[0] == "4":
									client = Abonnement.objects.get(contact=phone_number, actif=True)
									if level[1] == "1":
										Carnet.objects.create(client=client,noms=level[2].upper(),adresse=level[3].upper(),contact=level[4])
										response = "END Votre contact est bien pris en compte !"
								elif level[0] == "5":
									if level[2] == "1":
										if level[3] == "2" or level[3] == "3":
											response = "CON Taper le nombre de PIECES (CHAMBRE x SALON) :\n 1. 1 x 1\n 2. 2 x 1\n 3. 3 x 1\n 4. 4 x 1 \n 5. AUTRE"
										elif level[3] == "4":
											response = "CON Taper le nombre d'ETAGES"
										else:
											response = "CON Taper la SUPERFICIE DU TERRAIN EN METRE CARRE"
									else:
										response = "CON Taper votre ENVELOPPE (CAPACITE FINANCIERE POUR L'ACHAT OU LA LOCATION EN USD)"
								elif level[0] == "6":
									if level[1] == "1":
										response = "CON Taper la date d'ENTREE PREVUE :"
									else:
										response = "CON Taper le NUMERO de TELEPHONE de votre HOTE :"
								
								elif level[0] == "7":
									message = {}
									n = 0
									messages = ""
									if level[1] != "3" and level[1] != "5" and Voyage.objects.filter(origine=level[3].upper().strip(), destination=level[4].upper().strip()):
										voyage = Voyage.objects.get(origine=level[3].upper().strip(), destination=level[4].upper().strip())
										aircraft = Aircraft.objects.get(code=level[2].upper())
										if level[1] == "1":
											if Horaire.objects.filter(aircraft=aircraft, voyage=voyage):

												nbr_records = Horaire.objects.filter(aircraft=aircraft, voyage=voyage).count()

												for horaire in Horaire.objects.filter(aircraft=aircraft, voyage=voyage).order_by('jour')[((page-1)*2):(page*2)]:

													jour = JOUR.for_value(horaire.jour).display
													numvol = horaire.numvol
													heure_departure = horaire.heure_departure
													heure_arrival = horaire.heure_arrival
													escale = horaire.escale

													if escale != "DIRECT":
														escale = "via " + escale

													n += 1

													message["number"] = n
													message["jour"] = jour
													message["numvol"] = numvol
													message["heure_departure"] = heure_departure
													message["heure_arrival"] = heure_arrival
													message["escale"] = escale

													messages = messages + "%s. %s: %s DEPART %s - ARRIVEE %s %s \n" % (message["number"], message["jour"], message["numvol"], message["heure_departure"], message["heure_arrival"], message["escale"])

												response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/2), page, messages)

											else:
												response = "CON Il n'y a aucun horaire de vol pour ce voyage pour l'instant. Veuillez essayer plus tard.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

										elif level[1] == "4":

											response = "CON Taper la classe de votre choix : \n 1. POUR PREMIERE \n 2. POUR BUSINESS \n 3. POUR ECONOMIQUE \n 4. POUR AUTRE"

									elif level[1] == "3":
										response = "CON Taper la classe de reservation :\n 1. PREMIERE \n 2. BUSINESS \n 3. ECONOMIQUE \n 4. AUTRE"
									elif level[1] == "5":
										an_vol = level[4][-4:]
										jour_vol = level[4][:2]
										mois_vol = level[4][:5]
										lemois_vol = mois_vol[-2:]
										date_vol = datetime.date(int(an_vol), int(lemois_vol), int(jour_vol))
														
										if Aircraft_Available.objects.filter(numvol=level[3].upper(), dateVoyage=date_vol):

											for disponible in Aircraft_Available.objects.filter(numvol=level[3].upper(), dateVoyage=date_vol).order_by('classe'):

												classe = CLASSE.for_value(disponible.classe).display
												nombre = disponible.nombre

												n += 1

												message["number"] = n
												message["classe"] = classe
												message["nombre"] = nombre

												messages = messages + "%s. %s: %s disponible(s) \n" % (message["number"], message["classe"], message["nombre"])

											response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/2), page, messages)

										else:
											response = "CON Aucune place n'est disponible pour ce vol. Veuillez essayer plus tard.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."										

									else:

										response = "CON Le vol %s - %s ne figure pas dans notre base. \n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal." % (level[3].upper(), level[4].upper())

									if level[1] == "8":
										if level[2] == "1":
											if level[4] == "1" or level[4] == "2" or level[4] == "3" or level[4] == "4":
												response = "CON Si le motif est pour des raisons d'ETUDES, Taper le code de la filiale. Si non, laisser vide. (CONSULTER LA LISTE DES FILIALES):"
											else:
												response = "CON Vous n'avez saisi aucun motif.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
										


								elif level[0] == "9":
									try:
										date_meeting = datetime.strptime(level[4], '%d/%m/%Y')
										response = "CON Taper l'heure du rendez-vous :"
									except:
										response = "CON Format de date incorrect. Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
								elif level[0] == "10":
									if level[1] == "1":
										response = "CON Veuillez bien nous contacter au 01515 pour signature de contrat. \n Voulez-vous vraiment vous engager (TAPER 1 POUR OUI OU 2 POUR ANNULER) :"
									elif level[1] == "2":
										response = "CON Taper l'adresse et la destination :"																	
						except:

							if level[0] == "1":
								if level[1] == "1":
									response = "CON Taper votre adresse :"
								else:
									response = "CON Taper le nom du contact :"
							elif level[0] == "2":
								if level[1] == "4":
									if level[3] != 0 or level[3] != "":
										response = "CON Vous reservez la table pour (NOM DE LA PERSONNE CONCERNEE):"
									else:
										response = "END Veuillez indiquer le nombre de personnes."
							elif level[0] == "3":
								response = "CON Voulez-vous vraiment envoyer le message : %s \n pendant %s jours pour un montant global de %s ? \n TAPER 1 POUR CONFIRMER OU 2 POUR ANNULER." % (level[1].upper(), level[3], int(level[3])*1000)
							elif level[0] == "4":
								if level[1] == "1":
									response = "CON Taper le NUMERO de votre contact :"
							elif level[0] == "5":
								response = "CON Taper la commune du bien: \n 1.BANDALUNGWA\n 2.BARUMBU\n3.BUMBU\n4.GOMBE\n5.KALAMU\n6.KASA-VUBU\n7.KIMBANSEKE\n8.KINSHASA\n9.KINTAMBO\n10.KISENSO\n11.LEMBA\n12.LIMETE\n13.LINGWALA\n14.MAKALA\n15.MALUKU\n16.MASINA\n17.MATETE\n18.MONT-NGAFULA\n19.NDJILI\n20.NGABA\n21.NGALIEMA\n22.NGIRI-NGIRI\n23.NSELE\n24.SELEMBAO"
							elif level[0] == "6":
								if level[1] == "1":
									response = "CON Taper le nombre d'ENTREES \n 1. POUR UNE ENTREE \n 2. POUR DEUX ENTREES \n 3. POUR PLUSIEURS ENTREES"
								else:
									response = "CON Taper l'adresse physique de votre HOTE :"									
								
							elif level[0] == "7":
								if level[1] == "1" or level[1] == "4":
									response = "CON Taper la ville de destination :"
								elif level[1] == "3" or level[1] == "5":
									response = "CON Veuillez taper la date du vol :"
								elif level[1] == "8":
									if level[2] == "1":
										if Pays.objects.filter(codePays=level[3]):
											response = "CON Taper le motif de voyage : \n 1. AFFAIRES \n 2. ETUDES \n 3. SANTE \n 4. TOURISME"
										else:
											response = "CON Code pays incorrect.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
									elif level[2] == "3":
										message = {}
										n = 0
										messages = ""

										if Pays.objects.filter(codePays=level[3]):

											pays = Pays.objects.get(codePays=level[3])

											if Filiale.objects.filter():

												nbr_records = Filiale.objects.filter().count()

												for filiale in Filiale.objects.filter(pays=pays).order_by('filiale')[((page-1)*4):(page*4)]:

													filiales = filiale.filiale
													code = filiale.code

													n += 1

													message["number"] = n
													message["filiales"] = filiales
													message["code"] = code

													messages = messages + "%s. %s - %s \n" % (message["number"], message["code"], message["filiales"])

												response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : %s : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/2), page, pays.nomPays, messages)

											else:
												response = "CON Aucune filiale n'est encore disponible.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

										else:
											response = "CON Code pays incorrect.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
									elif level[2] == "4":
										response = "CON TAPER VOTRE PIN MOBILE MONEY :"

							elif level[0] == "9":
								response = "CON Taper la date du rendez-vous :"
							elif level[0] == "10":
								if level[1] == "1":
									response = "CON La climatisation est-elle disponible ? (TAPER 1 POUR OUI OU 2 POUR NON) :"
								elif level[1] == "2":
									try:
										timeIn = datetime.strptime(level[3], '%H:%M')
										response = "CON Taper l'adresse et le code d'origine :"
									except:
										response = "CON Format de l'heure incorrect.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
								elif level[1] == "3":
									if level[3] == "1":
										if Reservation_Taxi.objects.filter(code_reservation=level[2], cancel=False):
											reservation = Reservation_Taxi.objects.get(code_reservation=level[2], cancel=False)

											client = reservation.client.nom
											contact_client = reservation.client.contact

											if reservation.Taxi:

												contact_taxi = reservation.Taxi.contact
												matricule = reservation.Taxi.matricule

											origine = reservation.origine
											destination = reservation.destination
											code = reservation.code_reservation

											deadline_date = reservation.date_taxi
											deadline_time = reservation.heure_taxi

											deadline_date = deadline_date.strftime("%d/%m/%Y")
											deadline_time = deadline_time.strftime("%H:%M")

											reservation.active = False
											reservation.cancel = True

											reservation.save()

											response = "CON Votre reservation n'est pas pris en compte. Vous recevrez une notification pour ce faire.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

											sms_texte = "La reservation %s pour la course de %s vers %s, depart le %s %s n'est pas prise en compte. Contact taxi: %s." % (code, origine, destination, deadline_date, deadline_time, contact_taxi)
											connections = lookup_connections(backend="message_tester",identities=[contact_client])
											send(sms_texte, connections=connections)

											if reservation.Taxi:
												sms_texte = "La reservation %s pour la course de %s vers %s, depart le %s %s n'est pas prise en compte. Contact client: %s." % (code, origine, destination, deadline_date, deadline_time, contact_client)
												connections = lookup_connections(backend="message_tester",identities=[contact_taxi])
												send(sms_texte, connections=connections)

										else:
											response = "CON Aucune reservation ayant le code %s n'est prise en compte.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal." % (level[2])									
									else:
										response = "CON OPERATION ANNULEE. Contactez-nous au 01515 pour tout autre information.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
								elif level[1] == "4":
									taximan = Abonnement.objects.get(contact=phone_number, actif=True)
									if level[3] == "1":
										if Taxi.objects.filter(client=taximan):
											taxi = Taxi.objects.get(client=taximan)

											reservation = Reservation_Taxi.objects.get(code_reservation=level[2], active=True)
											reference = reservation.code_reservation

											origine = reservation.origine
											destination = reservation.destination
											ladate = reservation.date_taxi
											lheure = reservation.heure_taxi

											date = ladate.strftime("%d/%m/%Y")
											heure = lheure.strftime("%H:%M")
											client = reservation.client

											contact = client.contact
											contact_taxi = taxi.contact
											reservation.active = False

											reservation.Taxi = taxi
											reservation.save()

											response = "END Acceptez-vous la reservation %s. Depart le %s %s de %s vers %s. \n Contact: %s" % (level[2], date, heure, origine, destination, contact)

											sms_texte = "Le taxi de marque %s plaque %s accepte votre demande. Contact: %s %s. Code : %s. Montant de la course: %s. \n Vous recevrez un SMS d'alerte trente minutes avant le rendez-vous pour toute disposition utile." % (taxi.marque, taxi.matricule, taxi.client.nom, taxi.contact, reservation.code_reservation, reservation.cout)

											connections = lookup_connections(backend="message_tester",identities=[contact_taxi])
											send(sms_texte, connections=connections)

											cash = Cash_Book.objects.get(reference=reference)

											cash.partenaire = taximan
											cash.save()

										else:
											response = "CON Votre taxi encore n'est pris en compte.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
									else:
										response = "CON OPERATION ANNULEE. Contactez-nous au 01515 pour toute autre information.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

					except:

						if level[0] == "1" :
							if level[1] == "1":
								response = "CON Taper votre sexe :"
							else:
								response = "CON Taper votre sigle :"
						elif level[0] == "2":
							if level[1] == "1":
								if level[2] == "1":
									if Abonnement.objects.filter(contact=phone_number, actif=True) :
										if Abonnement.objects.filter(annuaire=False,contact=phone_number):
											annuaire = Abonnement.objects.get(contact=phone_number)
											annuaire.annuaire = True
											annuaire.save()
											response = "END Votre enregistrement dans l'annuaire de DFS a abouti."
										else:
											response = "CON Vous figurez dans l'annuaire de DFS.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
									elif Abonnement.objects.filter(contact2=phone_number, actif=True) :
										if Abonnement.objects.filter(annuaire=False,contact2=phone_number):
											annuaire = Abonnement.objects.get(contact2=phone_number)
											annuaire.annuaire = True
											annuaire.save()
											response = "END Votre enregistrement dans l'annuaire de DFS a abouti."
										else:
											response = "CON Vous figurez dans l'annuaire de DFS.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
									elif Abonnement.objects.filter(contact3=phone_number, actif=True):
										if Abonnement.objects.filter(annuaire=False,contact3=phone_number):
											annuaire = Abonnement.objects.get(contact3=phone_number)
											annuaire.annuaire = True
											annuaire.save()
											response = "END Votre enregistrement dans l'annuaire de DFS a abouti."
										else:
											response = "CON Vous figurez dans l'annuaire de DFS.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
									else:
										response = "CON Vous n'avez pas souscrit aux services de DFS. \n Veuillez vous abonner avant d'utiliser les services de DFS.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

								else:
									response = "CON OPERATION ANNULEE !\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

							elif level[1] == "2":
								message = {}
								n = 0
								messages = ""

								if Abonnement.objects.filter(nom__contains=level[2].upper(), actif=True, annuaire=True):

									nbr_records = Abonnement.objects.filter(nom__contains=level[2].upper(), actif=True, annuaire=True).count()

									for abonnement in Abonnement.objects.filter(nom__contains=level[2].upper(), actif=True, annuaire=True).order_by('nom')[((page-1)*2):(page*2)]:
										nom = abonnement.nom
										sexe = abonnement.sexe
										adresse = abonnement.adresse
										contact = abonnement.contact
										email = abonnement.email
										if email == None:
											email = ""
										fonction = abonnement.fonctionContact

										n += 1

										message["number"] = n
										message["nom"] = nom
										message["adresse"] = adresse
										message["contact"] = contact
										message["email"] = email
										message["fonction"] = fonction

										messages = messages + "%s. %s \n %s \n %s \n %s \n %s \n" % (message["number"], message["nom"], message["adresse"], message["contact"], message["email"], message["fonction"])

									response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/2), page, messages)

								else:

									response = "CON Aucun contact ne correspond.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

							elif level[1] == "3":
								message = {}
								n = 0
								messages = ""

								if Abonnement.objects.filter(fonctionContact__contains=level[2].upper(), actif=True, annuaire=True):

									nbr_records = Abonnement.objects.filter(fonctionContact__contains=level[2].upper(), actif=True, annuaire=True).count()

									for abonnement in Abonnement.objects.filter(fonctionContact__contains=level[2].upper(), actif=True, annuaire=True).order_by('nom')[((page-1)*2):(page*2)]:
										nom = abonnement.nom
										sexe = abonnement.sexe
										adresse = abonnement.adresse
										contact = abonnement.contact
										email = abonnement.email

										if email == None:
											email = ""
										identifiant = abonnement.id

										n += 1

										message["number"] = n
										message["nom"] = nom
										message["adresse"] = adresse
										message["contact"] = contact
										message["email"] = email
										message["identifiant"] = identifiant
										
										messages = messages + "%s. %s \n %s \n %s \n %s \n ID. : %s" % (message["number"], message["nom"], message["adresse"], message["contact"], message["email"], message["identifiant"])

									response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/2), page, messages)

								else:

									response = "CON Aucun contact ne correspond.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

							elif level[1] == "4":
								if Abonnement.objects.filter(fonctionContact__contains='RESTAU', actif=True, annuaire=True, id=level[2]):
									response = "CON Voulez-vous reserver une table pour combien de personnes ?:"
								else:
									response = "CON ID. de restaurant non reconnu.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
							elif level[1] == "5":
								client = Abonnement.objects.get(contact=phone_number)
								if Reservation_Restaurant.objects.filter(code_reservation=level[2], client = client):
									reservation = Reservation_Restaurant.objects.get(code_reservation=level[2])

									contact = reservation.restaurant.contact
									nbrCouvert = reservation.nbrCouvert
									personne = reservation.personne

									date_reservation = reservation.date_reservation
									heure_reservation = reservation.heure_reservation
									date_reservation = date_reservation.strftime("%d/%m/%Y")
									heure_reservation = heure_reservation.strftime("%H:%M")

									reservation.cancel = True
									reservation.save()

									response = "END Votre reservation n'est pas prise en compte. Le restaurant recevra un SMS pour l'annuler."

									sms_texte = "Annulation de la reservation %s pour une table de %s couverts au nom de %s le %s %s. Contact: %s" % (level[2], nbrCouvert, personne, date_reservation, heure_reservation, client.contact)


									connections = lookup_connections(backend="message_tester",identities=[contact])
									send(sms_texte, connections=connections)

								else:
									response = "CON Code de reservation incorrect ou vous n'avez le droit d'annuler cette reservation. Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

						elif level[0] == "3":
							response = "CON Pendant combien de temps devons-nous envoyer votre message ? Taper le nombre de jours en chiffres (MONTANT: 1000 UNITES/JOUR)."
						elif level[0] == "4":
							client = Abonnement.objects.get(contact=phone_number, actif=True)
							if level[1] == "1":
								response = "CON Taper l'adresse de votre contact :"
							elif level[1] == "2":
								message = {}
								n = 0
								messages = ""

								if Carnet.objects.filter(noms__contains=level[2].upper(), client=client):

									nbr_records = Carnet.objects.filter(noms__contains=level[2].upper(), client=client).count()

									for carnet in Carnet.objects.filter(noms__contains=level[2].upper(), client=client).order_by('noms')[((page-1)*2):(page*2)]:
										nom = carnet.noms
										adresse = carnet.adresse
										contact = carnet.contact

										n += 1

										message["number"] = n
										message["nom"] = nom
										message["adresse"] = adresse
										message["contact"] = contact
										
										messages = messages + "%s. %s \n %s \n %s \n" % (message["number"], message["nom"], message["adresse"], message["contact"])

									response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/2), page, messages)
								else:
									response = "CON Aucun contact ne figure dans la liste.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."							
							elif level[1] == "3":
								message = {}
								n = 0
								messages = ""

								if level[2][:4] != "+243":
									contact = "+243" + level[2][-9:]
								else:
									contact = level[2]

								if Carnet.objects.filter(contact=contact):

									nbr_records = Carnet.objects.filter(contact=contact).count()

									for carnet in Carnet.objects.filter(contact=contact).order_by('noms')[((page-1)*2):(page*2)]:
										nom = carnet.noms
										adresse = carnet.adresse
										contact = carnet.contact

										n += 1

										message["number"] = n
										message["nom"] = nom
										message["adresse"] = adresse
										message["contact"] = contact
										
										messages = messages + "%s. %s \n %s \n %s \n" % (message["number"], message["nom"], message["adresse"], message["contact"])

									response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/2), page, messages)
								else:
									response = "CON Aucun contact ne figure dans la liste.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."								
										
						elif level[0] == "5":
							if level[2] == "1":
								if Abonnement.objects.filter(contact=phone_number, actif=True, annuaire=True):
									response = "CON Taper le type de bien :\n \n 1. TERRAIN\n 2. VILLA\n 3. APPARTEMENT \n 4. IMMEUBLE \n 5. AUTRE"
								else:
									response = "CON Vous devez vous enregistrer dans l'annuaire avant d'utiliser ce service.\n Pour tout renseignement, Appeler au 01515.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
							else:
								response = "CON Taper le type de bien :\n \n 1. TERRAIN\n 2. VILLA\n 3. APPARTEMENT \n 4. IMMEUBLE \n 5. AUTRE"

						elif level[0] == "6":
							if level[1] == "1":
								if Pays.objects.filter(codePays=level[2]):
									response = "CON Taper le nombre de visas :"
								else:
									response = "CON Code AMBASSADE inconnu.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
							elif level[1] == "2":
								if Visa.objects.filter(numdemande=level[2]):

									response = "CON Taper le nom de votre HOTE (MEMBRE DE FAMILLE, AMI, ORGANISATION, HOTEL, ETC.) :"									

								else:
									response = "CON Aucune demande de visa ne correspond.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

							elif level[1] == "3":
								if Visa.objects.filter(numdemande=level[2]):
									client = Abonnement.objects.get(contact=phone_number, actif=True)
									visa = Visa.objects.get(numdemande=level[2])
									statutvisa = STATUTVISA.for_value(visa.statutvisa).display
									pays = visa.pays
									response = "END Le statut de votre demande de visa %s est : %s" % (pays, statutvisa)
								else:
									response = "CON Aucune demande de visa ne correspond.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
							elif level[1] == "5":
								response = "CON Taper votre PIN mobile MONEY :"

						elif level[0] == "7":
							if level[1] == "1" or level[1] == "4":
								if Aircraft.objects.filter(code=level[2].upper()):
									response = "CON Taper la ville de depart :"
								else:
									response = "END Ce code ne correspond a aucune compagnie d'aviation."
							elif level[1] == "3" or level[1] == "5":
								response = "CON Veuillez taper le NUMERO DE VOL (CONSULTER L'HORAIRE DES VOLS) :"
							elif level[1] == "6":
								if Aircraft_Reservation.objects.filter(code=level[2]):
									code = Aircraft_Reservation.objects.get(code=level[2])
									statutreservation = STATUTRESERVATION.for_value(code.statutreservation).display
									response = "END Le statut de votre demande de reservation est : %s" % (statutreservation)
								else:
									response = "END Aucune demande de reservation ne correspond."
							elif level[1] == "7":
								response = "CON TAPER VOTRE PIN MOBILE MONEY :"
							elif level[1] == "8":
								if level[2] == "1" or level[2] == "3":
									response = "CON Taper le code du pays (VEUILLEZ CONSULTER LA LISTE DES PAYS CONCERNES):" 
								if level[2] == "2":

									message = {}
									n = 0
									messages = ""

									if Pays.objects.filter():

										nbr_records = Pays.objects.filter(facilities=True).count()

										for ambassade in Pays.objects.filter(facilities=True).order_by('nomPays')[((page-1)*4):(page*4)]:

											nom = ambassade.nomPays
											code = ambassade.codePays

											n += 1

											message["number"] = n
											message["nom"] = nom
											message["code"] = code

											messages = messages + "%s. %s - %s \n" % (message["number"], message["code"], message["nom"])

										response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/2), page, messages)

									else:
										response = "CON Ce service n'est pas encore disponible.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
								if level[2] == "4":
									response = "CON Taper le code de la demande :"

						elif level[0] == "9":
							if level[1] == "1":
								response = "CON Veuillez le lieu du rendez-vous :"
							elif level[1] == "2":
								if Meeting.objects.filter(code=level[2]):
									response = "CON Enter le nom complet de la personne avec qui vous avez rendez-vous (VOUS POUVEZ INDIQUER SON TITRE) :" 
								else:
									response = "CON Aucun rendez-vous n'est disponible pour ce code. \n "
							elif level[1] == "3":
								if Meeting.objects.filter(code=level[2]):
									meeting = Meeting.objects.get(code=level[2])

									meeting.effectif = False
									meeting.save()

									response = "CON Votre rendez-vous n'est pas pris en compte.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
								else:
									response = "CON Code rendez-vous non reconnu. \n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
						elif level[0] == "10":
							if level[1] == "1":
								response = "CON Taper le matricule du VEHICULE :"
							elif level[1] == "2":
								try:
									ladateIn = datetime.strptime(level[2], '%d/%m/%Y')

									response = "CON Taper l'heure de depart :"

								except:
									response = "END Format date incorrect."
							elif level[1] == "3":
								response = "CON Voulez-vous vraiment annuler la reservation %s ? (TAPER 1 POUR OUI OU 2 POUR ANNULER L'OPERATION)" % (level[2])
							elif level[1] == "4":
								if Reservation_Taxi.objects.filter(code_reservation=level[2], active=True):
									reservation = Reservation_Taxi.objects.get(code_reservation=level[2])

									origine = reservation.origine
									destination = reservation.destination
									ladate = reservation.date_taxi
									lheure = reservation.heure_taxi
									cout = reservation.cout
									reference = reservation.code_reservation

									service = Cash_Book.objects.get(reference=reference).service
									pourcentagePartenaire = Cout_Service.objects.get(service=service, cout=cout).pourcentagePartenaire

									cout = cout * pourcentagePartenaire

									date = ladate.strftime("%d/%m/%Y")
									heure = lheure.strftime("%H:%M")

									response = "CON Voulez-vous vraiment accepter la reservation %s ? \n(depart de %s en date du %s %s pour %s). Montant de la course USD %s \n TAPER 1 POUR VALIDER OU 2 POUR ANNULER." % (level[2], origine, date, heure, destination, cout)
								else:
									response = "CON La reservation %s n'existe pas ou est prise en charge par un autre taxi. \n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal." % (level[2])
							elif level[1] == "5":
								response = "CON Taper votre PIN MOBILE MONEY :"

				except:

					if level[0] == "1":
						if level[1] == "1" or level[1] == "2":
							response = "CON Taper vos noms ou raison sociale :"
						else:
							response = "CON Veuillez taper 1 pour personne physique ou 2 pour personne morale. \n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
					elif level[0] == "2":
						if level[1] == "1":
							response = "CON Voulez-vous vraiment vous enregister dans l'annuaire ? \n TAPER 1 POUR OUI \n TAPER 0 POUR NON :"
						elif level[1] == "2":
							response = "CON Entrer le nom complet ou quelques mots du nom de votre contact :"
						elif level[1] == "3":
							response = "CON Entrer le secteur d'ACTIVITE :"
						elif level[1] == "4":
							response = "CON TAPER L'ID. du restaurant (VOIR ID SUR LA LISTE DE RECHERCHE):"
						elif level[1] == "5":
							response = "CON Taper le code de reservation:"

							
					elif level[0] == "3":

						response = "CON VOULEZ-VOUS UTILISER VOTRE BASE DE DONNEES OU CELLE DE DFS ? \n TAPER 1 POUR UTILISER VOTRE BASE DE DONNEES OU 2 POUR UTILISER CELLE DE DFS."
					elif level[0] == "4":
						if level[1] == "1":
							response = "CON Taper le nom complet de votre contact :"
						elif level[1] == "2":
							response = "CON Taper le nom complet ou quelques mots du nom de votre contact :"
						elif level[1] == "3":
							response = "CON Taper le NUMERO DE TELEPHONE de votre contact :"
					elif level[0] == "5":
						if level[1] == "1":
							response = "CON 1. Enregistrer un bien mis en vente \n"
							response += "2. Chercher un bien pour achat\n"
							response += "0. Menu principal\n"
							response += "00. Menu d'avant"
						else:
							response = "CON 1. Enregistrer un bien mis en location \n"
							response += "2. Chercher un bien en location\n"
							response += "0. Menu principal\n"
							response += "00. Menu d'avant"							

					elif level[0] == "6":
						if level[1] == "1":
							response = "CON Taper le code du pays :"
						elif level[1] == "2" or level[1] == "3":
							response = "CON Taper le code demande de visa :"
						elif level[1] == "4":

							message = {}
							n = 0
							messages = ""

							if Pays.objects.filter():

								nbr_records = Pays.objects.filter(facilities=False).count()

								for ambassade in Pays.objects.filter(facilities=False).order_by('nomPays')[((page-1)*4):(page*4)]:

									nom = ambassade.nomPays
									code = ambassade.codePays

									n += 1

									message["number"] = n
									message["nom"] = nom
									message["code"] = code

									messages = messages + "%s. %s - %s \n" % (message["number"], message["code"], message["nom"])

								response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/2), page, messages)

							else:
								response = "CON ce service n'est pas encore disponible.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
						elif level[1] == "5":
							response = "CON Taper le code de la demande :"						

					elif level[0] == "7":

						if level[1] == "1" or level[1] == "3" or level[1] == "4" or level[1] == "5":
							response = "CON Taper le code de la compagnie d'aviation de votre choix (VEUILLEZ CONSULTER LA LISTE) :"

						elif level[1] == "2":

							message = {}
							n = 0
							messages = ""

							if Aircraft.objects.filter():

								nbr_records = Aircraft.objects.filter().count()

								for aircraft in Aircraft.objects.filter().order_by('nom')[((page-1)*4):(page*4)]:

									nom = aircraft.nom
									code = aircraft.code

									n += 1

									message["number"] = n
									message["nom"] = nom
									message["code"] = code

									messages = messages + "%s. %s - %s \n" % (message["number"], message["code"], message["nom"])

								response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/4), page, messages)

							else:
								response = "CON Aucune compagnie d'aviation n'est disponible pour l'instant. \n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."						

						elif level[1] == "6":
							response = "CON Taper le code de la demande de reservation :"
						elif level[1] == "7":
							response = "CON Taper le code de reservation :"
						elif level[1] == "8":

							response = "CON 1. Demande de facilitation \n"
							response += "2. Consulter les pays \n"
							response += "3. Consulter les filiales\n"
							response += "4. Payer les frais \n"
							response += "0. Menu principal\n"
							response += "00. Menu d'avant"

					elif level[0] == "8":
						if level[1] == "1":
							slug = get_random_string(length=10, allowed_chars='0123456789')
							client = Abonnement.objects.get(contact=phone_number, actif=True)
							if Gift.objects.filter(code=slug):
								nom = Gift.objects.get(code=slug)
								gift = nom.nom
								code = nom.code
								if not Gift_Gain.objects.filter(client=client, gift=nom, codeGift=code, livraison=False):
									Gift_Gain.objects.create(client=client, gift=nom, codeGift=code)
								response = "CON Votre Cadeau : %s. Code : %s. Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal." % (gift, code)
							else:
								response = "CON Vous avez perdu. Essayer encore ! Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
						elif level[1] == "2":
							message = {}
							n = 0
							messages = ""

							client = Abonnement.objects.get(contact=phone_number, actif=True)
							if Gift_Gain.objects.filter(client=client, livraison=False):

								nbr_records = Gift_Gain.objects.filter(client=client, livraison=False).count()

								for gift in Gift_Gain.objects.filter(client=client, livraison=False).order_by('codeGift')[((page-1)*2):(page*2)]:

									nom = gift.gift.nom
									code = gift.codeGift

									n += 1

									message["number"] = n
									message["nom"] = nom
									message["code"] = code

									messages = messages + "%s. %s - %s \n" % (message["number"], message["code"], message["nom"])

								response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/2), page, messages)

							else:
								response = "CON Votre panier de cadeaux est vide.\n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

						elif level[1] == "3":
							message = {}
							n = 0
							messages = ""

							if Gift.objects.filter(actif=True):

								nbr_records = Gift.objects.filter(actif=True).count()

								for gift in Gift.objects.filter(actif=True).order_by('nom')[((page-1)*2):(page*2)]:

									nom = gift.nom
									code = gift.code

									n += 1

									message["number"] = n
									message["nom"] = nom
									message["code"] = code

									messages = messages + "%s. %s - %s \n" % (message["number"], message["code"], message["nom"])

								response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/2), page, messages)

							else:
								response = "CON Aucun cadeau n'est disponible pour l'instant. \n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
					
					elif level[0] == "9":
						if level[1] == "1":
							response = "CON Entrer le nom complet de la personne avec qui vous avez rendez-vous (VOUS POUVEZ INDIQUER SON TITRE) :"
						elif level[1] == "2" or level[1] == "3":
							response = "CON Taper le code du rendez-vous :"
						elif level[1] == "4":
							message = {}
							n = 0
							messages = ""
							
							if Abonnement.objects.filter(contact=phone_number, actif=True):

								client = Abonnement.objects.get(contact=phone_number, actif=True)

								if Meeting.objects.filter(client=client, effectif=True):

									nbr_records = Meeting.objects.filter(client=client, effectif=True).count()

									for meeting in Meeting.objects.filter(client=client, effectif=True)[((page-1)*2):(page*2)]:

										ladeadline_date = meeting.deadline_date
										ledeadline_time = meeting.deadline_time
										code = meeting.code

										deadline_date = ladeadline_date.strftime("%d/%m/%Y")
										deadline_time = ledeadline_time.strftime("%H:%M")
										personne = meeting.personne
										contact = meeting.contact
										lieu = meeting.lieu

										lameeting_date = meeting.meeting_date
										lemeeting_time = meeting.meeting_time

										meeting_date = lameeting_date.strftime("%d/%m/%Y")
										meeting_time = lemeeting_time.strftime("%H:%M")

										remarque = meeting.remarque

										n += 1

										message["number"] = n
										message["meeting_date"] = meeting_date
										message["meeting_time"] = meeting_time
										message["deadline_date"] = deadline_date
										message["deadline_time"] = deadline_time
										message["personne"] = personne
										message["contact"] = contact
										message["lieu"] = lieu
										message["code"] = code
										message["remarque"] = remarque

										messages = messages + "%s. Rendez-vous %s avec %s le %s %s. Lieu: %s Contact: %s. %s -\n" % (message["number"], message["code"], message["personne"], message["meeting_date"], message["meeting_time"], message["lieu"], message["contact"], message["remarque"])


									response = "CON %s RESULTAT(S) REPARTI(S) SUR %s PAGES(PAGE %s) : \n %s \n TAPER #NUMERO PAGE(EX. #2) POUR CONTINUER, 00 POUR REVENIR OU 0 MENU PRINCIPAL" % (nbr_records, round(nbr_records/2), page, messages)

								else:
									response = "CON Vous n'avez aucun rendez-vous en cours. \n Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

							else:
								response = "CON Vous devez vous abonner chez DFS avant d'utiliser ce service.\n Pour tout renseignement, appeler au 01515. Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

					elif level[0] == "10":
						if level[1] == "1":
							response = "CON Taper la marque du VEHICULE :"
						elif level[1] == "2":
							response  = "CON Taper la date de depart :"
						elif level[1] == "3" or level[1] == "4":
							response = "CON Veuillez taper le code de la reservation :"
						elif level[1] == "5":
							response = "CON Taper le code de reservation :"

			except:

				if texte == "1":
					if Abonnement.objects.filter(contact=phone_number, actif=True):
						response = "CON Vous figurez dans l'annuaire de DFS. Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
					else:
						response = "CON S'agit-il d'une personne physique ou une personne morale ? \n TAPER 1 POUR PERSONNE PHYSIQUE ET 2 POUR PERSONNE MORALE :"
				elif texte == "2":
					response = "CON 1. S'enregistrer dans l'annuaire \n"
					response += "2. Chercher par nom du contact ou raison sociale \n"
					response += "3. Chercher par secteur \n"
					response += "4. Reserver une table dans un restaurant\n"
					response += "5. Annuler la reservation de la table\n"
					response += "0. Menu principal"
				elif texte == "3":
					if Abonnement.objects.filter(contact=phone_number, actif=True, annuaire=True):
						response = "CON Taper votre annonce ou message publicitaire :"
					else:
						response = "END Vous devez vous abonner et enregistrer dans l'annuaire de DFS avant d'utiliser ce service.\n Pour tout renseignement, Appeler au 01515."
				elif texte == "4":
					response = "CON 1. Enregistrer un contact chez DFS ou envoyez-nous la liste de contact au format CSV à l'adresse support@di-data-dfs.com (VEUILLEZ MENTIONNER CONTACT COMME SUJET SUIVI DE VOTRE CODE DFS) \n"
					response += "2. Chercher un contact par nom \n"
					response += "3. Chercher un contact par NUMERO DE TELEPHONE\n"
					response += "0. Menu principal"
				elif texte == "5":
					if Abonnement.objects.filter(contact=phone_number, actif=True):
						response = "CON 1. Achat & vente \n"
						response += "2. Location\n"
						response += "0. Menu principal"
					else:
						response = "CON Vous devez vous abonner chez DFS avant d'utiliser ce service.\n Pour tout renseignement, Appeler au 01515. Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
				elif texte == "6":
					response = "CON 1. Demander un VISA \n"
					response += "2. Enregistrer les informations sur votre HOTE\n"
					response += "3. Consulter le statut du VISA\n"
					response += "4. Voir la liste des ambassades\n"
					response += "5. Payer les frais\n"
					response += "0. Menu principal"
				elif texte == "7":
					if Abonnement.objects.filter(contact=phone_number, actif=True):

						response = "CON 1. Horaire des VOLS \n"
						response += "2. Liste des compagnies d'aviation \n"
						response += "3. Demande de reservation \n"
						response += "4. Tarification (SERVICE DFS INCLUS) \n"
						response += "5. Vols disponibles \n"
						response += "6. statut de la reservation \n"
						response += "7. Achat billet \n"
						response += "8. Facilitation voyage\n"
						response += "0. Menu principal"
					else:
						response = "CON Vous devez vous abonner chez DFS avant d'utiliser ce service.\n Pour tout renseignement, Appeler au 01515. Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."


				elif texte == "8":

					if Abonnement.objects.filter(contact=phone_number, actif=True):

						if Gift.objects.filter(actif=True):
							for gift in Gift.objects.filter(actif=True, code=None).order_by('nom'):
								slug = get_random_string(length=10, allowed_chars='0123456789')
								gift.code = slug
								gift.save()						

						response = "CON 1. Jouer \n"
						response += "2. Voir mes cadeaux \n"
						response += "3. Liste de cadeaux\n"
						response += "0. Menu principal"
					else:
						response = "CON Vous devez vous abonner chez DFS avant d'utiliser ce service.\n Pour tout renseignement, Appeler au 01515. Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
				elif texte == "9":
					if Abonnement.objects.filter(contact=phone_number, actif=True):

						response = "CON 1. Enregistrer un rendez-vous \n"
						response += "2. Modifier un rendez-vous \n"
						response += "3. Annuler un rendez-vous \n"
						response += "4. Voir mes rendez-vous\n"
						response += "0. Menu principal"
					else:
						response = "CON Vous devez vous abonner chez DFS avant d'utiliser ce service.\n Pour tout renseignement, Appeler au 01515. Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."

				elif texte == "10":
					if Abonnement.objects.filter(contact=phone_number, actif=True):

						response = "CON 1. Enregistrer un taxi \n"
						response += "2. Reserver un taxi \n"
						response += "3. Annuler une reservation \n"
						response += "4. Accepter une reservation (MENU RESERVE AU TAXIMAN) \n"
						response += "5. Payer le taxi \n"
						response += "0. Menu principal"
					else:
						response = "CON Vous devez vous abonner chez DFS avant d'utiliser ce service.\n Pour tout renseignement, Appeler au 01515. Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
				elif texte == "11":
					if Abonnement.objects.filter(contact=phone_number, actif=True):

						response = "CON 1. Enregistrer un centre \n"
						response += "2. Devenir membre \n"
						response += "3. Enregistrer un membre de famille \n"
						response += "4. Consulter les DEPENSES \n"
						response += "5. Chercher un membre \n"
						response += "0. Menu principal"
					else:
						response = "CON Vous devez vous abonner chez DFS avant d'utiliser ce service.\n Pour tout renseignement, Appeler au 01515. Taper 00 pour revenir au menu d'avant ou 0 pour le menu principal."
				elif texte == "12":
					response = "END Merci de votre visite chez DFS. Vous pouvez nous appeler AU 01515 pour des plus amples informations ou consulter notre site https://www.di-data-dfs.com/"
				else:
					response = "END Merci de votre visite chez DFS. Vous pouvez nous appeler AU 01515 pour des plus amples informations ou consulter notre site https://www.di-data-dfs.com/"

		return HttpResponse(response)



#@csrf_exempt
#def sms_response(request):
#    # Start our TwiML response
#    resp = MessagingResponse()

    # Add a text message
#    msg = resp.message("Check out this sweet owl!")

#    # Add a picture message
#    msg.media("https://demo.twilio.com/owl.png")

#    return HttpResponse(str(resp))
