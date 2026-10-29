from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.decorators import login_required
from .choices import price_choices, bedroom_choices, state_choices

# Nhớ import thêm model Favorite (nếu bạn đã tạo)
from django.shortcuts import get_object_or_404, render
from .models import Listing
from accounts.models import Favorite # Thêm dòng này để lấy dữ liệu từ app accounts

def index(request):
  listings = Listing.objects.order_by('-list_date').filter(is_published=True)

  paginator = Paginator(listings, 6)
  page = request.GET.get('page')
  paged_listings = paginator.get_page(page)

  context = {
    'listings': paged_listings
  }

  return render(request, 'listings/listings.html', context)


def listing(request, listing_id):
  listing = get_object_or_404(Listing, pk=listing_id)
  
  # Kiểm tra trạng thái yêu thích
  is_favorited = False
  if request.user.is_authenticated:
    is_favorited = Favorite.objects.filter(user=request.user, listing=listing).exists()

  context = {
    'listing': listing,
    'is_favorited': is_favorited, # Truyền ra template
  }

  return render(request, 'listings/listing.html', context)
  # -----------------------------------------------------------

  context = {
    'listing': listing,
    'is_favorited': is_favorited, # Truyền biến này ra HTML
  }

  return render(request, 'listings/listing.html', context)


# --- PHẦN THÊM MỚI: Hàm xử lý khi bấm nút Yêu thích ---
@login_required(login_url='login')
def toggle_favorite(request, listing_id):
  listing = get_object_or_404(Listing, pk=listing_id)
  
  # Nếu đã yêu thích rồi thì xóa (bỏ thích), nếu chưa thì tạo mới
  favorite, created = Favorite.objects.get_or_create(
    user=request.user, 
    listing=listing
  )
  if not created:
    favorite.delete()
      
  # Xong việc thì load lại trang chi tiết bất động sản
  return redirect('listing', listing_id=listing.id)
# ------------------------------------------------------


def search(request):
  queryset_list = Listing.objects.order_by('-list_date')

  # Keywords
  if 'keywords' in request.GET:
    keywords = request.GET['keywords']
    if keywords:
      queryset_list = queryset_list.filter(description__icontains=keywords)

  # City
  if 'city' in request.GET:
    city = request.GET['city']
    if city:
      queryset_list = queryset_list.filter(city__iexact=city)

  # State
  if 'state' in request.GET:
    state = request.GET['state']
    if state:
      queryset_list = queryset_list.filter(state__iexact=state)

  # Bedrooms
  if 'bedrooms' in request.GET:
    bedrooms = request.GET['bedrooms']
    if bedrooms:
      queryset_list = queryset_list.filter(bedrooms__lte=bedrooms)

  # Price
  if 'price' in request.GET:
    price = request.GET['price']
    if price:
      queryset_list = queryset_list.filter(price__lte=price)

  context = {
    'state_choices': state_choices,
    'bedroom_choices': bedroom_choices,
    'price_choices': price_choices,
    'listings': queryset_list,
    'values': request.GET
  }

  return render(request, 'listings/search.html', context)