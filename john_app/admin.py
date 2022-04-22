from django.contrib import admin
from import_export import resources
from .models import Abonnement, Pays, Visa, Marketing, Mobilier, Gift, Gift_Gain, Meeting, Taxi, Reservation_Taxi, Carnet, Aircraft, Voyage, Horaire, Tarif_Aircraft, Aircraft_Available, Aircraft_Reservation, Mobilier, Filiale, Facilities, Reservation_Restaurant, Marketing_Data, Taux, Cout_Service, Cash_Book
from import_export.admin import ImportExportModelAdmin


# Abonnement

class AbonnementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'typepersonne', 'sexe', 'sigle', 'nomContact', 'fonctionContact', 'adresse', 'contact', 'contact2', 'contact3', 'email', 'actif', 'annuaire', 'dateEnr','dateEdit', 'user')
    list_filter = ('typepersonne',)
    date_hierarchy = 'dateEnr'
    ordering       = ('dateEnr', 'nom',)
    search_fields  = ('nom', 'nomContact', 'contact', 'contact1', 'contact2',)

class AbonnementResource(resources.ModelResource):

    class Meta:
        model = Abonnement
        skip_unchanged = True
        report_skipped = False
        fields = ('nom', 'typepersonne', 'sexe', 'nomContact', 'fonctionContact', 'adresse', 'contact', 'contact2', 'contact3', 'email', 'actif', 'annuaire', 'dateEnr','dateEdit',)
        import_id_fields = ('nom', 'typepersonne', 'sexe', 'nomContact', 'fonctionContact', 'adresse', 'contact', 'contact2', 'contact3', 'email', 'actif', 'annuaire', 'dateEnr','dateEdit',)
        export_order = ('nom', 'typepersonne', 'sexe', 'nomContact', 'fonctionContact', 'adresse', 'contact', 'contact2', 'contact3', 'email', 'actif', 'annuaire', 'dateEnr','dateEdit',)


# Pays

class PaysAdmin(admin.ModelAdmin):
    list_display = ('codePays', 'nomPays')

# Visa

class VisaAdmin(admin.ModelAdmin):
    list_display = ('pays', 'nbrVisa', 'nbreIn', 'dateIn', 'dateOut', 'typeDoc', 'nomContact', 'dateNais', 'nation', 'adresse','email','contact','profession','objet','info','hote','adresseHote','emailHote','contactHote','finance','numdemande','statutvisa','dateEnr','dateEdit',)
    list_filter = ('pays__nomPays','statutvisa','nbreIn',)
    date_hierarchy = 'dateEnr'
    ordering       = ('dateEnr', 'pays','nomContact',)
    search_fields  = ('numdemande', 'nomContact', 'contact',)

class VisaResource(resources.ModelResource):

    class Meta:
        model = Visa
        skip_unchanged = True
        report_skipped = False
        fields = ('pays__nomPays', 'nbrVisa', 'nbreIn', 'dateIn', 'dateOut', 'typeDoc', 'nomContact', 'dateNais', 'nation', 'adresse','email','contact','profession','objet','info','hote','adresseHote','emailHote','contactHote','finance','numdemande','statutvisa','dateEnr','dateEdit',)
        import_id_fields = ('pays__nomPays', 'nbrVisa', 'nbreIn', 'dateIn', 'dateOut', 'typeDoc', 'nomContact', 'dateNais', 'nation', 'adresse','email','contact','profession','objet','info','hote','adresseHote','emailHote','contactHote','finance','numdemande','statutvisa','dateEnr','dateEdit',)
        export_order = ('pays__nomPays', 'nbrVisa', 'nbreIn', 'dateIn', 'dateOut', 'typeDoc', 'nomContact', 'dateNais', 'nation', 'adresse','email','contact','profession','objet','info','hote','adresseHote','emailHote','contactHote','finance','numdemande','statutvisa','dateEnr','dateEdit',)


admin.site.register(Abonnement, AbonnementAdmin)
admin.site.register(Pays, PaysAdmin)
admin.site.register(Visa, VisaAdmin)
admin.site.register(Marketing)
admin.site.register(Gift)
admin.site.register(Gift_Gain)
admin.site.register(Meeting)
admin.site.register(Taxi)
admin.site.register(Reservation_Taxi)
admin.site.register(Carnet)
admin.site.register(Aircraft)
admin.site.register(Voyage)
admin.site.register(Horaire)
admin.site.register(Tarif_Aircraft)
admin.site.register(Aircraft_Available)
admin.site.register(Aircraft_Reservation)
admin.site.register(Mobilier)
admin.site.register(Filiale)
admin.site.register(Facilities)
admin.site.register(Reservation_Restaurant)
admin.site.register(Marketing_Data)
admin.site.register(Taux)
admin.site.register(Cout_Service)
admin.site.register(Cash_Book)