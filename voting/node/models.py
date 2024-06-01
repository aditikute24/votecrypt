from django.db import models

class HashedBlindedSecret(models.Model):
    hashed_blinded_secret = models.CharField(max_length = 250)
    is_signed = models.BooleanField(default = False)
    signed_secret = models.CharField(max_length = 250, blank = True)
    unblinded_signed_secret = models.CharField(max_length = 250, blank = True)
    #is_validated = models.BooleanField(default = False)

    def __str__(self):
        return self.hashed_blinded_secret