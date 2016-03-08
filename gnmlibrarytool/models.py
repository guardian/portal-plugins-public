from django.db import models
from rest_framework import serializers


class LibraryNickname(models.Model):
    library_id = models.CharField(max_length=32)
    nickname = models.CharField(max_length=254)


class LibraryNicknameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LibraryNickname
        fields = ('library_id','nickname')