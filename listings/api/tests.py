from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from realtors.models import Realtor
from listings.models import Listing
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

User = get_user_model()


class ListingAPITestCase(APITestCase):

    def test_anonymous_cannot_create_listing(self):
        response = self.client.post(
            "/api/listings/",
            {},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_non_owner_cannot_update_listing(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f"/api/listings/{self.listing.pk}/",
            {"title": "Unauthorized Change"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, "Test Apartment")

    def test_non_owner_cannot_delete_listing(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f"/api/listings/{self.listing.pk}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(Listing.objects.filter(pk=self.listing.pk).exists())

    def setUp(self):
        self.user = User.objects.create_user(
            username="testcfeuser",
            email="test@test.com",
            password="somerandompassword",
        )

        content_type = ContentType.objects.get_for_model(Listing)
        permission = Permission.objects.get(
            codename="add_listing",
            content_type=content_type,
        )
        self.user.user_permissions.add(permission)

        self.realtor = Realtor.objects.create(
            name="Test Realtor",
            photo="",
            phone="0900000000",
            email="realtor@test.com",
        )

        self.listing = Listing.objects.create(
            realtor=self.realtor,
            title="Test Apartment",
            address="123 Test Street",
            city="Ho Chi Minh City",
            state="Ho Chi Minh",
            zipcode="700000",
            description="This is a test apartment",
            price=2000000000,
            bedrooms=2,
            bathrooms=2.0,
            garage=1,
            sqft=800,
            lot_size=100.0,
            photo_main="",
        )

    def test_single_user(self):
        self.assertEqual(User.objects.count(), 1)

    def test_listing_created(self):
        self.assertEqual(Listing.objects.count(), 1)
        self.assertEqual(self.listing.title, "Test Apartment")

    def test_listing_has_realtor(self):
        self.assertEqual(self.listing.realtor, self.realtor)

    def test_list_listings_api(self):
        response = self.client.get("/api/listings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_listing_detail_api(self):
        response = self.client.get(f"/api/listings/{self.listing.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Apartment")

    def test_search_listings_api(self):
        response = self.client.get("/api/listings/?q=Test Apartment")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_no_results(self):
        response = self.client.get("/api/listings/?q=NoSuchProperty")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_listing_api(self):
        image_buffer = BytesIO()

        Image.new("RGB", (100, 100), color="white").save(
            image_buffer,
            format="JPEG",
        )

        image = SimpleUploadedFile(
            "test_photo.jpg",
            image_buffer.getvalue(),
            content_type="image/jpeg",
        )
        data = {
            "realtor": self.realtor.pk,
            "title": "New Test Apartment",
            "address": "456 Test Street",
            "city": "Ho Chi Minh City",
            "state": "Ho Chi Minh",
            "zipcode": "700001",
            "description": "Created through API",
            "price": 2500000000,
            "bedrooms": 3,
            "bathrooms": "2.0",
            "garage": 1,
            "sqft": 1000,
            "lot_size": "120.0",
            "is_published": True,
            "photo_main": image,
        }
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/listings/",
            data,
            format="multipart",
        )
        print("POST response:", response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Listing.objects.count(), 2)
        self.assertEqual(
            Listing.objects.get(title="New Test Apartment").realtor,
            self.realtor,
        )
