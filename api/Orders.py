from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, Product, Parent
from .serializers import OrderSerializer
JWT_SECRET = "H18E15A11H18D14D14F16D14C13Wed"

import jwt
from django.http import JsonResponse
from .models import Attendance
from django.views.decorators.csrf import csrf_exempt


class UserOrdersView(APIView):
    def get(self, request, parent_id):
        """Retrieve orders for a specific parent, including product and parent details."""
        decoded = jwt.decode(parent_id, JWT_SECRET, algorithms=['HS256'])
        phone_number = decoded.get('phone')
        parent = Parent.objects.filter(phone=phone_number).first()
        orders = Order.objects.filter(parent__id=parent.id)

        data = []
        for order in orders:
            data.append({
                "id": str(order.id),
                "product": {
                    "id": str(order.product.id),
                    "ProductName": order.product.ProductName,
                    "price": order.product.price,
                    "imgurl": order.product.imgurl
                },
                "quantity": order.quantity,
                "parent": {
                    "id": str(order.parent.id),
                    "name": order.parent.name,
                    "phone": order.parent.phone
                },
                "paid": order.paid,
                "fulfilled": order.fulfilled,
                "created_at": order.created_at.strftime("%Y-%m-%d")
            })
            print(data)
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new order."""
        data = request.data
        try:
            product = Product.objects.get(id=data["product"])
            parent = Parent.objects.get(id=data["parent"])

            order = Order.objects.create(
                product=product,
                parent=parent,
                quantity=data["quantity"],
                paid=data["paid"],
                fulfilled=data.get("fulfilled", False),
            )

            response_data = {
                "id": str(order.id),
                "product": {
                    "id": str(product.id),
                    "ProductName": product.ProductName,
                    "price": product.price,
                    "imgurl": product.imgurl
                },
                "quantity": order.quantity,
                "parent": {
                    "id": str(parent.id),
                    "name": parent.name,
                    "phone": parent.phone
                },
                "paid": order.paid,
                "fulfilled": order.fulfilled,
                "created_at": order.created_at.strftime("%Y-%m-%d")
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        except (Product.DoesNotExist, Parent.DoesNotExist):
            return Response({"error": "Invalid product or parent ID"}, status=status.HTTP_400_BAD_REQUEST)
