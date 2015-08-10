from django.db import models


class LibraryNickname(models.Model):
    library_id = models.CharField(max_length=32)
    nickname = models.CharField(max_length=254)