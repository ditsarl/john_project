from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from extended_choices import Choices
from django.contrib.auth.models import User, BaseUserManager, AbstractBaseUser, PermissionsMixin

from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=User)
def create_auth_token(sender,instance=None,created=False,**kwargs):
	if created:
		Token.objects.create(user=instance)

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
	('RESTAURANT',9,'Restaurant'),
)

class Abonnement(models.Model):
	TYPEPERSONNE = (
		(1, 'Personne physique'),
		(2, 'Personne morale'),
	)
	SEXE = (
		('F', 'Feminin'),
		('M', 'Masculin'),
	)

	typepersonne = models.PositiveSmallIntegerField(
		choices=TYPEPERSONNE,
		default=1,
		)
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
	nom = models.CharField(max_length=50, verbose_name='Noms ou Raison Sociale')
	sexe = models.CharField(choices=SEXE, max_length=1, null=True, blank=True, verbose_name='Sexe')
	sigle = models.CharField(max_length=15, null=True, blank=True, verbose_name='Sigle')
	nomContact = models.CharField(max_length=50, null=True, blank=True, verbose_name='Noms Contact')
	fonctionContact = models.CharField(max_length=25, null=True, blank=True, verbose_name="Secteur d'activité")
	adresse = models.CharField(max_length=100, verbose_name='Adresse')
	contact = models.CharField(max_length=15, verbose_name='Téléphone 1')
	contact2 = models.CharField(max_length=15, blank=True, null=True, verbose_name='Téléphone 2')
	contact3 = models.CharField(max_length=15, blank=True, null=True, verbose_name='Téléphone 3')
	email = models.CharField(max_length=25, blank=True, null=True, verbose_name='Email')
	actif = models.BooleanField(default=True)
	code = models.CharField(max_length=6, blank=True, null=True)
	annuaire = models.BooleanField(default=False, verbose_name="Dans l'annuaire ?")
	dateEnr = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
	dateEdit = models.DateTimeField(auto_now=True, verbose_name='Date de modification')

	def __str__(self):
		return self.nom

	class Meta:
		verbose_name = "Abonnement"
		ordering = ('nom',)

class Pays(models.Model):
	codePays = models.IntegerField(verbose_name="Code de l'ambassade")
	nomPays = models.CharField(max_length=50, verbose_name="Nom de l'ambassade")
	facilities = models.BooleanField(default=False)

	def __str__(self):
		return self.nomPays

	class Meta:
		verbose_name_plural = "Ambassades"
		ordering = ('nomPays',)

class Visa(models.Model):
	NBRIN = (
		(1, 'Une entrée'),
		(2, 'Deux entrées'),
		(3, 'Plusieurs entrées'),
	)

	TYPEDOCUMENT = (
		(1, 'Passeport ordinaire'),
		(2, 'Passeport diplomatique'),
		(3, 'Passeport de service'),
		(4, 'Passeport officiel'),
		(5, 'Passeport spécial'),
		(6, 'Autre document'),
	)

	OBJETVOYAGE = (
		(1, 'Tourisme'),
		(2, 'Affaires'),
		(3, 'Visite à la famille ou à des amis'),
		(4, 'Culture'),
		(5, 'Sports'),
		(6, 'Visite officielle'),
		(7, 'Raisons médicales'),
		(8, 'Etudes'),
		(9, 'Transit aéroportuaire'),
		(10, 'Autre'),
	) 

	FINANCE = (
		(1, 'Par vous-même'),
		(2, 'Par un garant'),
	) 


	client = models.ForeignKey('Abonnement', on_delete=None)
	pays = models.ForeignKey('Pays', on_delete=None)
	nbrVisa = models.IntegerField(verbose_name='Nombre de Visa')
	nbreIn = models.PositiveSmallIntegerField(
		choices=NBRIN,
		default=1, verbose_name="Nombre d'entrées"
		)
	dateIn = models.DateField(verbose_name="Date d'entrée prévue")
	dateOut = models.DateField(verbose_name="Date de sortie prévue")
	typeDoc = models.PositiveSmallIntegerField(
		choices=TYPEDOCUMENT,
		default=1, verbose_name="Type Document de voyage"
		)
	nomContact = models.CharField(max_length=50, verbose_name="Nom du (de la) demandeur(euse")
	dateNais = models.DateField(verbose_name="Date de naissance du (de la) demandeur(euse)")
	nation = models.CharField(max_length=50, verbose_name="Nationalité du (de la) demandeur(euse)")
	adresse = models.CharField(max_length=100, verbose_name="Adresse du (de la) demandeur(euse)")
	email = models.CharField(max_length=50, verbose_name="Email du (de la) demandeur(euse)")
	contact = models.CharField(max_length=15, verbose_name='Téléphone')
	profession = models.CharField(max_length=25, verbose_name="Profession actuelle")
	objet = models.PositiveSmallIntegerField(
		choices=OBJETVOYAGE,
		default=1, verbose_name="Objet du voyage"
		)
	info = models.CharField(max_length=200, null=True, blank=True, verbose_name="Informations complémentaires")
	hote = models.CharField(max_length=100, null=True, blank=True, verbose_name="Nom de l'hôte (Personne ou Hôtel)")
	adresseHote = models.CharField(max_length=100, null=True, blank=True, verbose_name="Adresse de l'hôte")
	emailHote = models.CharField(max_length=50, null=True, blank=True, verbose_name="Email de l'hôte")
	contactHote = models.CharField(max_length=15, null=True, blank=True, verbose_name="Téléphone de l'hôte")
	finance = models.PositiveSmallIntegerField(
		choices=FINANCE, null=True, blank=True,
		default=1, verbose_name="Financement du voyage"
		)
	numdemande = models.CharField(max_length=25, verbose_name="Numéro demande")
	statutvisa = models.PositiveSmallIntegerField(
		choices=STATUTVISA, null=True, blank=True,
		default=1, verbose_name="Status du visa"
		)
	dateEnr = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
	dateEdit = models.DateTimeField(auto_now=True, verbose_name='Date de modification')


	def __str__(self):
		return self.numdemande

	class Meta:
		verbose_name_plural = "Demandes de Visa"
		ordering = ('numdemande',)

class Marketing(models.Model):
	BDD_SOURCE = (
		(1, 'Client'),
		(2, 'Chez John'),
	)

	texte = models.TextField(verbose_name='Texte du message')
	dateEnr = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
	source = models.PositiveSmallIntegerField(
		choices=BDD_SOURCE,
		default=2,
		)
	frequence = models.IntegerField(default=1, verbose_name='Fréquence')
	date_deadline = models.DateField(verbose_name="Deadline")
	client = models.ForeignKey('Abonnement', on_delete=None)
	moderation = models.BooleanField(default=False)

	def __str__(self):
		return self.client.nom + "-" + str(self.dateEnr)

class Mobilier(models.Model):

	typevilla = models.PositiveSmallIntegerField(
		choices=TYPEVILLA,
		default=2
		)
	piece = models.PositiveSmallIntegerField(
		choices=PIECE,
		default=5, blank=True, null=True
		)
	etage = models.IntegerField(blank=True, null=True)
	superficie = models.IntegerField(blank=True, null=True)
	cout = models.IntegerField(default=0)
	garanty = models.IntegerField(default=3

		)
	vente = models.BooleanField(default=False)
	commune = models.PositiveSmallIntegerField(
		choices=COMMUNE,
		default=1, blank=True, null=True
		)
	client = models.ForeignKey('Abonnement', on_delete=models.CASCADE)
	adresseUrl = models.CharField(max_length=100, default="", blank=True, null=True)
	actif = models.BooleanField(default=False)
	dateEnr = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")

	def __str__(self):
		return self.client.nom + '-' + str(self.dateEnr) + '-' + str(TYPEVILLA.for_value(self.typevilla).display) + '-' + str(PIECE.for_value(self.piece).display) + '/' + str(COMMUNE.for_value(self.commune).display)

class Gift(models.Model):
	nom = models.CharField(max_length=150)
	code = models.CharField(max_length=10, null=True, blank=True)
	actif = models.BooleanField(default=False)
	dateEnr = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
	dateGain = models.DateTimeField(auto_now=True, verbose_name="Date de gain")

	def __str__(self):
		return self.nom + " - " + str(self.code)

class Gift_Gain(models.Model):
	client = models.ForeignKey('Abonnement', on_delete=None)
	gift = models.ForeignKey('Gift', on_delete=None)
	codeGift = models.CharField(max_length=10, null=True, blank=True)
	dateGain = models.DateTimeField(auto_now_add=True, verbose_name="Date de gain")
	livraison = models.BooleanField(default=False)

	def __str__(self):
		return str(self.codeGift) + " : " + str(self.gift.nom)

class Meeting(models.Model):
	client = models.ForeignKey('Abonnement', on_delete=None)
	personne = models.CharField(max_length=50)
	contact = models.CharField(max_length=15)
	lieu = models.CharField(max_length=200)
	meeting_date = models.DateField()
	meeting_time = models.TimeField()
	deadline_date = models.DateField()
	deadline_time = models.TimeField()
	dateEnr = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
	dateEdit = models.DateTimeField(auto_now=True, verbose_name='Date de modification')
	code = models.CharField(max_length=10)
	annuler = models.BooleanField(default=False)
	effectif = models.BooleanField(default=True)
	remarque = models.TextField(null=True, blank=True)

	def __str__(self):
		return self.code

class Taxi(models.Model):
	client = models.ForeignKey('Abonnement', on_delete=None)
	matricule = models.CharField(max_length=15)
	marque = models.CharField(max_length=50)
	climatisation = models.BooleanField(default=True)
	contact = models.CharField(max_length=15)
	vip = models.BooleanField(default=False)
	actif = models.BooleanField(default=False)

	def __str__(self):
		return self.matricule

class Reservation_Taxi(models.Model):
	client = models.ForeignKey('Abonnement', on_delete=None)
	Taxi = models.ForeignKey('Taxi', on_delete=None, blank=True, null=True)
	date_taxi = models.DateField()
	heure_taxi = models.TimeField()
	origine = models.CharField(max_length=200)
	destination = models.CharField(max_length=200)
	vip = models.BooleanField(default=False)
	climatisation = models.BooleanField(default=True)
	code_reservation = models.CharField(max_length=10)
	cout = models.IntegerField(default=10)
	cancel = models.BooleanField(default=False)
	active = models.BooleanField(default=True)
	dateEnr = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
	
	def __str__(self):
		return self.code_reservation

class Carnet(models.Model):
	client = models.ForeignKey('Abonnement', on_delete=None)
	noms = models.CharField(max_length=50)
	adresse = models.CharField(max_length=200)
	contact = models.CharField(max_length=15)
	dateEnr = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")

	def __str__(self):
		return str(self.client.nom)

class Aircraft(models.Model):
	code = models.CharField(max_length=4)
	nom = models.CharField(max_length=25)

	def __str__(self):
		return self.nom

class Voyage(models.Model):

	origine = models.CharField(max_length=40)
	destination = models.CharField(max_length=40)

	def __str__(self):
		return self.origine + " - " + self.destination

class Horaire(models.Model):

	jour = models.PositiveSmallIntegerField(
		choices=JOUR,
		default=2, blank=True, null=True
		)

	voyage = models.ForeignKey('Voyage', on_delete=None)
	aircraft = models.ForeignKey('Aircraft', on_delete=None)
	heure_departure = models.TimeField()
	heure_arrival = models.TimeField()
	numvol = models.CharField(max_length=6)
	escale = models.CharField(max_length=40)
	dateEnr = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
	dateEdit = models.DateTimeField(auto_now=True, verbose_name='Date de modification')

	def __str__(self):
		return str(self.voyage) + " : " + str(JOUR.for_value(self.jour).display) + "/" + str(self.aircraft)

class Tarif_Aircraft(models.Model):
	passager = models.PositiveSmallIntegerField(
		choices=PASSAGER,
		default=1, blank=True, null=True
		)
	voyage = models.ForeignKey('Voyage', on_delete=None)
	aircraft = models.ForeignKey('Aircraft', on_delete=None)
	classe = models.PositiveSmallIntegerField(
		choices=CLASSE,
		default=3, blank=True, null=True
		)
	tarif = models.FloatField(default=0)
	dateEnr = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
	dateEdit = models.DateTimeField(auto_now=True, verbose_name='Date de modification')

	def __str__(self):
		return str(self.voyage) + " : " + str(CLASSE.for_value(self.classe).display) + "/" + str(PASSAGER.for_value(self.passager).display) + "/" + str(self.aircraft)

class Aircraft_Available(models.Model):
	voyage = models.ForeignKey('Voyage', on_delete=None)
	aircraft = models.ForeignKey('Aircraft', on_delete=None)
	classe = models.PositiveSmallIntegerField(
		choices=CLASSE,
		default=3, blank=True, null=True
		)
	numvol = models.CharField(max_length=6)
	dateVoyage = models.DateField()	
	nombre = models.IntegerField(default=0)
	dateEnr = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
	dateEdit = models.DateTimeField(auto_now=True, verbose_name='Date de modification')


	def __str__(self):
		return str(self.voyage) + " : " + str(CLASSE.for_value(self.classe).display) + "/" + str(self.aircraft)

class Aircraft_Reservation(models.Model):
	client = models.ForeignKey('Abonnement', on_delete=None)
	aircraft = models.ForeignKey('Aircraft', on_delete=None)
	numvol = models.CharField(max_length=6)
	dateVoyage = models.DateField()	
	classe = models.PositiveSmallIntegerField(
		choices=CLASSE,
		default=3, blank=True, null=True
		)	
	adulte = models.IntegerField(default=1)
	child = models.IntegerField(default=0)
	infant = models.IntegerField(default=0)
	code = models.CharField(max_length=10)
	statutreservation = models.PositiveSmallIntegerField(
		choices=STATUTRESERVATION,
		default=1
		)

	dateEnr = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
	dateEdit = models.DateTimeField(auto_now=True, verbose_name='Date de modification')


	def __str__(self):
		return self.code

class Filiale(models.Model):
	pays = models.ForeignKey('Pays', on_delete=None)
	filiale = models.CharField(max_length=50)
	code = models.IntegerField(default=1)

	def __str__(self):
		return str(self.pays.nomPays) + ': ' + self.filiale

class Facilities(models.Model):
	client = models.ForeignKey('Abonnement', on_delete=None)
	pays = models.ForeignKey('Pays', on_delete=None, related_name='Country')
	filiale = models.ForeignKey('Filiale', on_delete=None, blank=True, null=True)
	motif = models.PositiveSmallIntegerField(
		choices=MOTIF,
		default=2, blank=True, null=True
		)
	numdemande = models.CharField(max_length=15, verbose_name="Numéro demande")
	observation = models.TextField(blank=True, null=True)
	def __str__(self):
		return str(self.client) + " : " + str(MOTIF.for_value(self.motif).display) + "/" + str(self.pays.nomPays)

class Reservation_Restaurant(models.Model):
	client = models.ForeignKey('Abonnement', on_delete=None, related_name='Client')
	restaurant = models.ForeignKey('Abonnement', on_delete=None, related_name='Restaurant')
	nbrCouvert = models.IntegerField()
	personne = models.CharField(max_length=50)
	date_reservation = models.DateField()
	heure_reservation = models.TimeField()
	code_reservation = models.CharField(max_length=10, blank=True, null=True)
	cancel = models.BooleanField(default=False)

	def __str__(self):
		return str(self.client.nom) + ': ' + str(self.restaurant.nom) + '/' + str(self.date_reservation)

class Marketing_Data(models.Model):
	client = models.ForeignKey('Abonnement', on_delete=None)
	contact = models.CharField(max_length=15)

	def __str__(self):
		return str(self.client) + ': ' + self.contact

class Taux(models.Model):
	de = models.DateTimeField()
	a = models.DateTimeField(blank=True, null=True)
	taux = models.FloatField()
	actif = models.BooleanField(default=False)

	def __str__(self):
		return str(self.de) + ' - ' + str(self.a) + ' : ' + str(self.taux)

class Cout_Service(models.Model):
	PERIODE = (
		(1, 'Cash'),
		(2, 'Jour'),
		(3, 'Mois'),
	)
	service = models.PositiveSmallIntegerField(
		choices=SERVICE,
		default=1
		)
	cout = models.FloatField(default=0.20)
	pourcentageDFS = models.FloatField(default=0.70)
	pourcentagePartenaire = models.FloatField(default=0.30)
	periodicity = models.PositiveSmallIntegerField(
		choices=PERIODE,
		default=2,
		)
	dateEnr = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
	dateEdit = models.DateTimeField(auto_now=True, verbose_name='Date de modification')


	def __str__(self):
		return str(self.service)

class Cash_Book(models.Model):
	cashNumber = models.CharField(max_length=15)
	client = models.ForeignKey('Abonnement', on_delete=None)
	service = models.PositiveSmallIntegerField(
		choices=SERVICE,
		default=1
		)
	gainDFS_USD = models.FloatField()
	gainDFS_CDF = models.FloatField()
	partenaire = models.ForeignKey('Abonnement', on_delete=None, blank=True, null=True, related_name='Partenaire')
	gainPartenaire_USD = models.FloatField()
	gainPartenaire_CDF = models.FloatField()
	reference = models.CharField(max_length=15, blank=True, null=True)
	paid = models.BooleanField(default=False)
	dateEnr = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
	






