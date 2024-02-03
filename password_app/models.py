from django.db import models

class PasswordVault(models.Model):
    """
    Model representing a password entry in the vault. 
    Each entry contains information such as the user, website name, website URL, password, and creation timestamp.

    Methods:  __str__: Returns a string representation of the password entry.
    """
    user = models.CharField(max_length=40,blank=False)
    website_name = models.CharField(max_length = 30, blank = False)
    website_url = models.URLField(blank = False)
    password = models.CharField(max_length = 100,blank = False)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.user}'s vault for {self.website_name}"