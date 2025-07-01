from django.apps import AppConfig
import cloudinary
import os

class ECommerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'e_commerce'

    # def ready(self):
    #     cloudinary.config(
    #         cloud_name='dgvjxhqjd',
    #         api_key='912747183312112',
    #         api_secret='YNIkhloSMWRuzhfKBviqQGJhDJM',
    #         secure=True
    #     )
