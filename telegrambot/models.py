from django.db import models

class DataCenter(models.Model):
    name = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField()
    api_key = models.CharField(max_length=255)
    api_password = models.CharField(max_length=255)
    port = models.IntegerField(default=4084)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name