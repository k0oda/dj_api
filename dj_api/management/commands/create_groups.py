from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from dj_api import models


class Command(BaseCommand):
    help = 'Checks or creates base Groups and Permissions'

    def handle(self, *args, **options):
        client, created = Group.objects.get_or_create(name='client')
        if created:
            self.stdout.write("Created Client group")
        staff = Group.objects.get(name='staff')

        product_content_type = ContentType.objects.get_for_model(models.Product)
        cart_content_type = ContentType.objects.get_for_model(models.Cart)
        order_content_type = ContentType.objects.get_for_model(models.Order)

        can_list_product = Permission.objects.create(
            codename='can_list_product',
            name='Can list Product',
            content_type=product_content_type,
        )
        can_add_product_to_cart = Permission.objects.create(
            codename='can_add_product_to_cart',
            name='Can add Product to Cart',
            content_type=cart_content_type,
        )
        can_list_cart = Permission.objects.create(
            codename='can_list_cart',
            name='Can list Cart',
            content_type=cart_content_type,
        )
        can_remove_product_from_cart = Permission.objects.create(
            codename='can_remove_product_from_cart',
            name='Can remove Product from Cart',
            content_type=cart_content_type,
        )
        can_create_order = Permission.objects.create(
            codename='can_create_order',
            name='Can create Order',
            content_type=order_content_type,
        )
        can_list_order = Permission.objects.create(
            codename='can_list_order',
            name='Can list Order',
            content_type=order_content_type,
        )

        client.permissions.add(can_list_product)
        client.permissions.add(can_add_product_to_cart)
        client.permissions.add(can_list_cart)
        client.permissions.add(can_remove_product_from_cart)
        client.permissions.add(can_create_order)
        client.permissions.add(can_list_order)

        staff.permissions.add(can_list_product)
        staff.permissions.add(can_add_product_to_cart)
        staff.permissions.add(can_list_cart)
        staff.permissions.add(can_remove_product_from_cart)
        staff.permissions.add(can_create_order)
        staff.permissions.add(can_list_order)
