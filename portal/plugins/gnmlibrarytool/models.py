from django.db import models
from rest_framework import serializers


class LibraryNickname(models.Model):
    library_id = models.CharField(max_length=32)
    nickname = models.CharField(max_length=254)


class LibraryNicknameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LibraryNickname
        fields = ('library_id', 'nickname')


blank_storagerule = """<?xml version="1.0" ?>
<StorageRulesDocument xmlns:ns0="http://xml.vidispine.com/schema/vidispine">
	<tag id="original">
	    <storages>1</storages>
		<precedence>MEDIUM</precedence>
	</tag>
</StorageRulesDocument>"""


class LibraryStorageRule(models.Model):
    storagerule_name = models.CharField(max_length=256)
    storagerule_xml_source = models.TextField(default=blank_storagerule)
