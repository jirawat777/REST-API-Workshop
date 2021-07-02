from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login
# ใช้ CRSF เพื่อส่ง TOKEN
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
# Import Model เข้ามา
from api_workshop.models import category, Product, product_image, cart, invoice, invoice_item
from django.contrib.auth.models import User
import jwt
import datetime
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
# Import Serializer เข้ามา
from api_workshop.serializers import ProductSerializer
# Import REST FRAMWORK เข้ามา
from rest_framework.views import APIView, exception_handler
from django.db.models.signals import post_save
import django_filters.rest_framework
from rest_framework.parsers import JSONParser
from rest_framework.decorators import *
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, generics, permissions, renderers, filters, serializers
from renderer import UserRenderer
from rest_framework.reverse import reverse
from rest_framework import permissions
from .response_custom.response_custom import ResponseInfo, ErrorInfo
# Import Serializer เข้ามา
from api_workshop.serializers import *
from rest_framework import pagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .paginator import CustomPagination
from rest_framework.exceptions import NotFound, ParseError, AuthenticationFailed,NotAcceptable
# Create your views here.

class RegisterView_2(APIView):
    def post(self, request):
        serializer = Regis(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class RefrestView(TokenObtainPairView):
    serializer_class = TokenRefreshSerializer


class RegisterApi(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(
                user=serializer.instance)
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    # "user": UserSerializer(user, context=self.get_serializer_context()).data,
                    "access_token": str(refresh.access_token),
                    "token_type": str(refresh.token_type),
                    "refresh": str(refresh),
                    "expire_in": int(
                        refresh.access_token.lifetime.total_seconds())
                },
                status=status.HTTP_201_CREATED)
        else:
            raise NotAcceptable()

    # def create(self, validated_data):
    #     user = User.objects.create_user(
    #         username=validated_data['username'],
    #         password=validated_data['password1'],
    #         first_name=validated_data['first_name'],
    #         last_name=validated_data['last_name'])
    #     user.save()
    #     return user


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users':
        reverse('user-list', request=request, format=format),
        'product':
        reverse('product-list', request=request, format=format),
        'category':
        reverse('category-list', request=request, format=format),
        'product_image':
        reverse('product_image-list', request=request, format=format),
        'cart':
        reverse('cart-list', request=request, format=format),
        'invoice':
        reverse('invoice-list', request=request, format=format),
        'invoice_item':
        reverse('invoice_item-list', request=request, format=format),
    })


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email']
    ordering_fields = ['id']
    permission_classes = [permissions.DjangoModelPermissions]

    def get(self, request, format=None):
        content = {'status': 'request was permitted'}
        return Response(content)


class ProductViewSet(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend
    ]
    search_fields = ['name']
    filterset_fields = ['is_enabled']
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(ProductViewSet, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        response_data = super(ProductViewSet,
                              self).list(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        if not response_data.data:
            self.response_format = ErrorInfo().response
        return Response(self.response_format)

    def get_queryset(self):
        queryset = Product.objects.all()
        sorts_by = self.request.query_params.get('sort', 'desc')
        category_in = self.request.query_params.get('category_in', None)
        category_not_in = self.request.query_params.get(
            'category_not_in', None)

        list_params_in = []
        list_params_not_in = []

        if category_in:
            for i in category_in.split(","):
                list_params_in.append(int(i))

        if category_not_in:
            for i in category_not_in.split(","):
                list_params_not_in.append(int(i))

        if sorts_by == 'desc':
            queryset = queryset.order_by('price')

        else:
            queryset = queryset.order_by('-price')

        if category_in:
            queryset = queryset.filter(category__in=list_params_in)
        if category_not_in:
            queryset = queryset.exclude(category__in=list_params_not_in)

        return queryset


class ProductViewSetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(ProductViewSetDetail, self).__init__(**kwargs)

    def retrieve(self, request, *args, **kwargs):
        response_data = super(ProductViewSetDetail,
                              self).retrieve(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        return Response(self.response_format)


class Product_Image_ViewSet(viewsets.ModelViewSet):
    queryset = product_image.objects.all()
    serializer_class = Product_Image_Serializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product']
    ordering_fields = ['product']
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]


class CategotyViewSet(viewsets.ModelViewSet):
    queryset = category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(CategotyViewSet, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        response_data = super(CategotyViewSet,
                              self).list(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        if not response_data.data:
            self.response_format = ErrorInfo().response
        return Response(self.response_format)

    def retrieve(self, request, *args, **kwargs):
        response_data = super(CategotyViewSet,
                              self).retrieve(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        if not response_data.data:
            self.response_format["message"] = "Empty"
        return Response(self.response_format)


class CartViewSet(generics.ListCreateAPIView):
    queryset = cart.objects.all()
    serializer_class = CartSerializer
    pagination_class = CustomPagination
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    ]
    filterset_fields = ['product']
    ordering_fields = ['quantity', 'total']
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user_id = self.request.user
            user = User.objects.get(username=user_id)
            product_id = self.request.data['product']
            products = Product.objects.get(pk=int(product_id))
            quantities = int(serializer.data['quantity'])
            item = cart.objects.filter(user=user, product=products.id).first()
            if item:
                item.quantity += quantities
                mul = quantities * products.price
                item.total += float(mul)
                item.save()
                newdict = {
                    'user': item.user.username,
                    'id': item.id,
                    'product': products.id,
                    'price': item.total,
                }
                newdict.update(serializer.data)
                return Response({
                    "data": newdict,
                    'msg': "บันทึกสำเร็จ",
                },
                    status=status.HTTP_201_CREATED)
            else:
                new_item = cart.objects.create(product=products,
                                               user=user,
                                               quantity=quantities,
                                               total=quantities *
                                               products.price)
                new_item.save()
                print(user_id)
                newdict = {
                    'user': new_item.user.username,
                    'id': new_item.id,
                    'product': new_item.id,
                    'price': new_item.total,
                }
                newdict.update(serializer.data)
                return Response({
                    "data": newdict,
                    'msg': "บันทึกสำเร็จ",
                },
                    status=status.HTTP_201_CREATED)
        else:
            return Response(
                {
                    "code": "ADD TO CART FAIL",
                    "msg": "บันทึกไม่สำเร็จ",
                    "error": [serializer.errors]
                },
                status=status.HTTP_400_BAD_REQUEST)

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(CartViewSet, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        response_data = super(CartViewSet, self).list(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format)


class EditCartQuanlity(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = cart.objects.all()
    serializer_class = CartSerializer

    def patch(self, request, pk):
        try:
            Cart = cart.objects.get(id=pk)
            user = self.request.user
            data = request.data
            Cart.total = float(data['quantity']) * float((Cart.product.price))
            Cart.quantity = data['quantity']
            Cart.save()
            if Cart.quantity == 0:
                Cart.delete()
                return Response({
                    'msg': 'ลบสำเร็จ'
                })
            data = {}
            data['id'] = Cart.id
            data['user'] = user.username
            data['quantity'] = Cart.quantity
            data['total'] = Cart.total
            newdict = {
                'data': data,
                'product': Cart.product,
                'quantity': Cart.total,
                'total': Cart.total,
                'msg': "บันทึกสำเร็จ",
            }
            return Response({
                'msg': 'บันทึกสำเร็จ',
                'data': data,
            },
                status=status.HTTP_200_OK)
        except:
            return Response({
                'msg': 'ไม่พบ',
                "code": "HTTP_404_NOT_FOUND",
            },
                status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        current_user = self.request.user
        try:
            instance = self.get_object()
            cart_user = cart.objects.get(pk=kwargs['pk']).user
        except:
            raise NotFound()
        if cart_user != current_user:
            return Response({
                "code": "HTTP_403_FORBIDDEN",
                "msg": "ไม่มีสิทธ์เข้าใช้งาน",
            })
        self.perform_destroy(instance)
        return Response({
            'msg': 'ลบข้อมูลสำเร็จ',
        }, status=status.HTTP_200_OK)


class InvoiceViewSet(generics.ListCreateAPIView):
    queryset = invoice.objects.all()
    serializer_class = InvoiceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id', 'user']
    ordering_fields = ['id']
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(InvoiceViewSet, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        response_data = super(InvoiceViewSet, self).list(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format)

class Invoice_Item_ViewSet(viewsets.ModelViewSet):
    queryset = invoice_item.objects.all()
    serializer_class = Invoice_Item_Serializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id', 'product']
    ordering_fields = ['id']
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]