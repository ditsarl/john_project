from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import User, Group
from .models import Abonnement


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'password', 'groups')
        extra_kwargs = {'password': {'write_only': True, 'min_length':8}}

        def create(self, validated_data):

            get_user_model().objects.create_user(**validated_data)

            username = validated_data.pop("username")
            code = validated_data.pop("code")
            user = get_user_model.objects.get(username=username)
            abonnement = Abonnement.objects.get(code=code)
            abonnement.user = user
            abonnement_serializer = AbonnementSerializer(data=abonnement)
            abonnement_serializer.update(user, user)
            abonnement.save()

            return user

class AbonnementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Abonnement
        fields = ('nom', 'sexe', 'sigle', 'nomContact', 'fonctionContact', 'adresse',
                  'contact',
                  'contact2',
                  'contact3',
                  'email',
                  'actif',
                  'code',
                  'annuaire',
                  'dateEnr',
                  'dateEdit',
                  'user')

class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type':'password'},
        trim_whitespace = False
    )
    code = serializers.CharField()

    def validate(self,attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if User.objects.filter(username=username):
            user_code = User.objects.get(username=username)
            abonnement = Abonnement.objects.get(user=user_code)
            code_abonnement = abonnement.code

        code = attrs.pop('code')

        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password,
            code=code
        )
        if not user or code != code_abonnement:
            raise serializers.ValidationError("Nom d'utilisateur, mot de passe ou code DFS non valide")
        attrs['user'] = user
        return attrs