from core.models import Product, Category, Vendor, CartOrder, ProductReview, CartOrderItems, ProductImages, Wishlist, Address
from django.shortcuts import get_object_or_404 # Import this if you want to use it for 'Address'
from django.db.models import Min,Max,Count
from django.contrib import messages

def default(request):
    Categories = Category.objects.annotate(
        product_count=Count("category")
    )
    vendors= Vendor.objects.all()
    
    min_max_price = Product.objects.aggregate(Min("price"),Max("price"))
    
    
    try:
        wishlist = Wishlist.objects.filter(user=request.user)
    except:
        messages.warning(request,"You need to login before accesing your wishlist..")
        wishlist = 0
    
    # Initialize 'address' to None or a default value
    address = None 
    
    # ⭐ CRITICAL FIX: Only run the database query if the user is authenticated
    if request.user.is_authenticated:
        try:
            # Use .filter().first() or a try-except block to handle cases where 
            # a logged-in user might not have an address yet. 
            # Using .filter().first() is safer than .get() here.
            address = Address.objects.filter(user=request.user).first()
        except Exception as e:
            # Optionally log the error or pass
            pass
            
    return {
        'categories': Categories,
        'address': address,
        'vendors':vendors,
        'min_max_price':min_max_price,
    }
    
    
def categories_with_count(request):
    return {
        "nav_categories": Category.objects.annotate(
            product_count=Count("category")
        )
    }