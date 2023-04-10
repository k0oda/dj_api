from rest_framework import serializers


class ProductSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000)
    price = serializers.DecimalField(max_digits=9, decimal_places=2)


class OrderSerializer(serializers.Serializer):
    products = ProductSerializer(many=True)
