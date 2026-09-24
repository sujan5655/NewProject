
from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source="category.category_name",
        read_only=True
    )

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product

        fields = [
            "id",
            "product_name",
            "slug",
            "product_description",
            "price",
            "images",
            "image_url",
            "stock",
            "is_available",
            "category",
            "category_name",
            "created_date",
            "modified_date",
        ]

        read_only_fields = [
            "id",
            "slug",
            "category_name",
            "image_url",
        ]

    def get_image_url(self, obj):
        if obj.images:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.images.url)

        return None
