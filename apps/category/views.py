from django.shortcuts import render

# Create your views here.


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category


class CategoryListAPIView(APIView):
  def get(self,request):
    categories=Category.objects.all()
    return Response({
      "id":category.id,
      "category_name":category.category_name,
      "slug":category.slug,
      "description":category.description,
      "cat_image":(
        request.build_absolute_url(category.cat_image.url)
        if category.cat_image
        else None
      )
    }
    for category in categories
    )