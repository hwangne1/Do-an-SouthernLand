from django.db.models import Q
from rest_framework import generics, mixins
from rest_framework.permissions import IsAdminUser

from listings.models import Listing
from .serializers import ListingSerializer


class ListingsAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    lookup_field = "pk"
    serializer_class = ListingSerializer

    def get_queryset(self):
        qs = Listing.objects.all()
        query = self.request.GET.get("q")

        if query is not None:
            qs = qs.filter(
                Q(title__icontains=query) | Q(zipcode__icontains=query)
            ).distinct()

        return qs

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return []

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()


class ListingsRudView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "pk"
    serializer_class = ListingSerializer

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [IsAdminUser()]
        return []

    def get_queryset(self):
        return Listing.objects.all()
