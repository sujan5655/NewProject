# from django.shortcuts import get_object_or_404, render

# from category.models import Category
# from store.models import Product

# # Create your views here.
# def store(request,category_slug=None):
#   categories=None
#   products=None
#   if category_slug !=None:
#     categories=get_object_or_404(Category,slug=category_slug)
#     products=Product.objects.filter(category=categories,is_available=True)
#     product_count=products.count()
#   else:
#     products=Product.objects.all().filter(is_available=True)
#     product_count=products.count()

  
#   context={
#     'products':products,
#    'product_count':product_count
#   }
#   return render(request,'store/store.html',context)



# def product_detail(request,category_slug,product_slug):
#   try:
#     single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)
#   except Exception as e:
#     raise e
#   context={
#     'single_product':single_product
#   }

#   return render(request,'store/product_detail.html',context)





from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.category.models import Category
from .models import Product
from .serializers import ProductSerializer


class StoreAPIView(APIView):
  def get(self,request,category_slug=None):
    # Get query parameters
    search = request.GET.get("search", "")
    max_price = request.GET.get("max_price")
    if category_slug:
      category=get_object_or_404(
        Category,
        slug=category_slug
      )
    
      products=Product.objects.filter(
        category=category,
        is_available=True
      )
    else:
      products=Product.objects.filter(is_available=True)
      # Search Filter
    if search:
      products=products.filter(
        product_name__icontains=search
      )
    # Pricing Filter
    if max_price:
      products = products.filter(
        price__lte=max_price
    )
    product_count=products.count()
    serializer = ProductSerializer(
            products,
            many=True,
            context={"request": request}
        )
    
    return Response({
        "product_count":product_count,
        "products":serializer.data
    })

class ProductDetailAPIView(APIView):
  def get(self,request,category_slug,product_slug):
    product=get_object_or_404(
      Product,
      category__slug=category_slug,
      slug=product_slug
    )
    serializer=ProductSerializer(product,context={"request": request})
    return Response(serializer.data)


class CategoryListAPIView(APIView):
  def get(self,request):
    categories=Category.objects.all()
    return Response({
      "id":category.id,
      "category_name":category.category_name,
      "slug":category.slug,
      "description":category.description,
      "cat_image":(
        request.build_absolute_uri(category.cat_image.url)
        if category.cat_image
        else None
      )
    }
    for category in categories
    )
