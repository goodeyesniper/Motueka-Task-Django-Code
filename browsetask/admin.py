# Whatever you make here in reference to your models.py will reflect in your 127.0.0.1:8000/admin panel

from django.contrib import admin
from .models import Post, Offer

class PostAdmin(admin.ModelAdmin):
    pass
class OfferAdmin(admin.ModelAdmin):
    pass


admin.site.register(Post, PostAdmin)
admin.site.register(Offer, OfferAdmin)

