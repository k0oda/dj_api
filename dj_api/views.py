from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer

from django.contrib.auth import authenticate, get_user_model

from dj_api import models, serializers


@api_view(['POST'])
def auth(request):
    email = request.data['email']
    password = request.data['password']
    user = authenticate(email=email, password=password)
    if user is not None:
        token = Token.objects.create(user=user)
        return Response(
            {
                'data': {
                    'user_token': token,
                }
            },
            status=200,
        )
    else:
        return Response(
            {
                'error': {
                    'code': 401,
                    'message': 'Неправильные логин или пароль',
                }
            },
            status=401,
        )


@api_view(['POST'])
def register(request):
    blank_fields = []

    name = request.data['fio']
    email = request.data['email']
    password = request.data['password']

    if name is None:
        blank_fields.append('name')
    else:
        name = name.split()
        last_name = name[0]
        first_name = name[1]
        middle_name = name[2]

    if email is None:
        blank_fields.append('email')

    if password is None:
        blank_fields.append('password')

    if len(blank_fields) == 0:
        return Response(
            {
                'error': {
                    'code': 422,
                    'message': 'Ошибка валидации',
                    'errors': {
                         item: [f'field {item} can not be blank'] for item in blank_fields
                    }
                }
            },
            status=422,
        )
    else:
        user = get_user_model().objects.create(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=email,
            password=password,
        )
        user.save()
        token = Token.objects.create(user=user)
        return Response(
            {
                'data': {
                    'user_token': token,
                }
            },
            status=201,
        )


@api_view(['GET'])
def list_products(request):
    products = models.Product.objects.all()
    serialized_products = serializers.ProductSerializer(products, many=True)
    return Response(
        {
            serialized_products.data,
        },
        status=200,
    )


# Auth required
@api_view(['POST'])
def add_product_to_cart(request, product_id):
    user_token = Token.objects.get(user=request.user)
    if user_token == request.auth:
        if request.user.has_perm('dj_api.can_add_product_to_cart'):
            product = models.Product.objects.get(pk=product_id)
            cart = models.Cart.objects.get_or_create(
                user=request.user,
            )
            cart.products.add(product)
            cart.save()
            return Response(
                {
                    'data': {
                        'message': 'Сувенир добавлен в корзину'
                    },
                },
                status=201,
            )
        else:
            return Response(
                {
                    'error': {
                        'code': 403,
                        'message': 'Запрещено для вас',
                    }
                },
                status=403,
            )
    else:
        return Response(
            {
                'error': {
                    'code': 403,
                    'message': 'Ошибка авторизации',
                }
            },
            status=403,
        )


# Auth required
@api_view(['GET'])
def list_cart(request):
    user_token = Token.objects.get(user=request.user)
    if user_token == request.auth:
        if request.user.has_perm('dj_api.can_list_cart'):
            cart = models.Cart.objects.get_or_create(
                user=request.user,
            )
            products = JSONRenderer().render(serializers.ProductSerializer(cart.products, many=True).data)
            return Response(
                {
                    products,
                },
                status=201,
            )
        else:
            return Response(
                {
                    'error': {
                        'code': 403,
                        'message': 'Запрещено для вас',
                    }
                },
                status=403,
            )
    else:
        return Response(
            {
                'error': {
                    'code': 403,
                    'message': 'Ошибка авторизации',
                }
            },
            status=403,
        )


# Auth required
@api_view(['DELETE'])
def remove_product_from_cart(request, product_id):
    user_token = Token.objects.get(user=request.user)
    if user_token == request.auth:
        if request.user.has_perm('dj_api.can_remove_product_from_cart'):
            product = models.Product.objects.get(pk=product_id)
            cart = models.Cart.objects.get_or_create(
                user=request.user,
            )
            cart.products.remove(product)
            cart.save()
            return Response(
                {
                    'data': {
                        'message': 'Сувенир удален из корзины'
                    }
                },
                status=201,
            )
        else:
            return Response(
                {
                    'error': {
                        'code': 403,
                        'message': 'Запрещено для вас',
                    }
                },
                status=403,
            )
    else:
        return Response(
            {
                'error': {
                    'code': 403,
                    'message': 'Ошибка авторизации',
                }
            },
            status=403,
        )


# Auth required
@api_view(['POST'])
def create_order(request):
    user_token = Token.objects.get(user=request.user)
    if user_token == request.auth:
        if request.user.has_perm('dj_api.can_create_order'):
            cart = models.Cart.objects.get_or_create(
                user=request.user,
            )
            products = cart.products.all()
            if len(products) == 0:
                return Response(
                    {
                        'error': {
                            'code': 422,
                            'message': 'Корзина пуста',
                        }
                    },
                    status=422,
                )
            else:
                total_price = 0
                for product in products:
                    total_price += product.price
                order = models.Order.objects.create(
                    products=products,
                    price=total_price,
                )
                order.save()
                return Response(
                    {
                        'data': {
                            'order_id': order.pk,
                            'message': 'Заказ оформлен',
                        }
                    },
                    status=201,
                )
        else:
            return Response(
                {
                    'error': {
                        'code': 403,
                        'message': 'Запрещено для вас',
                    }
                },
                status=403,
            )
    else:
        return Response(
            {
                'error': {
                    'code': 403,
                    'message': 'Ошибка авторизации',
                }
            },
            status=403,
        )


# Auth required
@api_view(['GET'])
def list_order(request):
    user_token = Token.objects.get(user=request.user)
    if user_token == request.auth:
        if request.user.has_perm('dj_api.can_list_order'):
            orders = models.Order.objects.filter(
                user=request.user
            )
            orders = JSONRenderer().render(serializers.OrderSerializer(orders, many=True))
            return Response(
                {
                    orders,
                },
                status=201,
            )
        else:
            return Response(
                {
                    'error': {
                        'code': 403,
                        'message': 'Запрещено для вас',
                    }
                },
                status=403,
            )
    else:
        return Response(
            {
                'error': {
                    'code': 403,
                    'message': 'Ошибка авторизации',
                }
            },
            status=403,
        )


# Auth required
@api_view(['GET'])
def logout(request):
    user_token = Token.objects.get(user=request.user)
    if user_token == request.auth:
        request.auth.delete()
        return Response(
            {
                'data': {
                    'message': 'Вы вышли из системы'
                }
            },
            status=200,
        )
    else:
        return Response(
            {
                'error': {
                    'code': 403,
                    'message': 'Ошибка авторизации',
                }
            },
            status=403,
        )


# Auth required
@api_view(['POST'])
def create_product(request):
    user_token = Token.objects.get(user=request.user)
    if user_token == request.auth:
        if request.user.is_staff:
            product = models.Product.objects.create(
                name=request.data['name'],
                description=request.data['description'],
                price=request.data['description'],
            )
            product.save()
            return Response(
                {
                    'data': {
                        'id': product.pk,
                        'message': 'Сувенир добавлен в каталог',
                    }
                },
                status=201,
            )
        else:
            return Response(
                {
                    'error': {
                        'code': 403,
                        'message': 'Запрещено для вас',
                    }
                },
                status=403,
            )
    else:
        return Response(
            {
                'error': {
                    'code': 403,
                    'message': 'Ошибка авторизации',
                }
            },
            status=403,
        )


# Auth required
@api_view(['DELETE'])
def remove_product(request, product_id):
    user_token = Token.objects.get(user=request.user)
    if user_token == request.auth:
        if request.user.is_staff:
            product = models.Product.objects.get(pk=product_id)
            product.delete()
            return Response(
                {
                    'data': {
                        'message': 'Сувенир удален из каталога'
                    }
                },
                status=200,
            )
        else:
            return Response(
                {
                    'error': {
                        'code': 403,
                        'message': 'Запрещено для вас',
                    }
                },
                status=403,
            )
    else:
        return Response(
            {
                'error': {
                    'code': 403,
                    'message': 'Ошибка авторизации',
                }
            },
            status=403,
        )


@api_view(['POST'])
def edit_product(request, product_id):
    user_token = Token.objects.get(user=request.user)
    if user_token == request.auth:
        if request.user.is_staff:
            product = models.Product.objects.get(pk=product_id)
            product.name = request.data['name']
            product.description = request.data['description']
            product.price = request.data['price']
            product.save()
            return Response(
                {
                    JSONRenderer().render(serializers.ProductSerializer(product).data),
                },
                status=200,
            )
        else:
            return Response(
                {
                    'error': {
                        'code': 403,
                        'message': 'Запрещено для вас',
                    }
                },
                status=403,
            )
    else:
        return Response(
            {
                'error': {
                    'code': 403,
                    'message': 'Ошибка авторизации',
                }
            },
            status=403,
        )

