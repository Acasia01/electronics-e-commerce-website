from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse , JsonResponse
from django.db.models import Count,Avg
from taggit.models import Tag

from core.models import Product, Category,Vendor,CartOrder,ProductReview,CartOrderItems,ProductImages,Wishlist, Address
from userauths.models import ContactUs
from core.forms import ProductReviewForm
from django.db.models import Q
from django.template.loader import render_to_string
import traceback
from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.urls import reverse
from django.core import serializers


# Create your views here.
def index(request):
    products = Product.objects.all().order_by("-id")
    new_arrivals = Product.objects.filter(new_arrival= True)
    best_sellers = Product.objects.filter(best_seller= True)
    banner_products = Product.objects.filter(banner_product = True)
    context = {
        "products":products,
        'new_arrivals':new_arrivals,
        'best_sellers':best_sellers,
        'banners':banner_products,
        
    }
    return render(request, 'core/index.html',context)

def shop(request):
    products = Product.objects.all().order_by("-id")
    new_arrivals = Product.objects.filter(new_arrival= True)
    best_sellers = Product.objects.filter(best_seller= True)
    banner_products = Product.objects.filter(banner_product = True)
    Categories = Category.objects.all()
    vendors = Vendor.objects.all()
    context = {
        "products":products,
        'new_arrivals':new_arrivals,
        'best_sellers':best_sellers,
        'banners':banner_products,
        'categories':Categories,
        'vendors':vendors
        
    }
    return render(request,"core/shop.html",context)

def vendor_view(request,vid):
    vendors = Vendor.objects.get(vid=vid)
    products = Product.objects.all()
    context ={
        "vendors":vendors,
        'products':products
    }
    return render(request,"core/vendor.html",context)
    

def category_view(request):
    Categories = Category.objects.all().annotate(product_count=Count("category"))
    context = {
        "categories":Categories
    }
    return render(request,'core/shop.html',context)

def category_product_view(request,cid):
    category = get_object_or_404(Category, cid=cid)
    products = Product.objects.filter(product_status ="published",category=category)
    
    context = {
        "category":category,
        "products":products,
    }
    
    return render(request,"core/products.html",context)

def product_list_view(request):
    products = Product.objects.all().order_by("-id")
    category = Category.objects.all()
    
    context={
        "products":products,
        "category":category,
    }
    return render(request,"core/product-list.html",context)

def product_detail_view(request, pid):
    product = get_object_or_404(Product, pid=pid)
    p_image = product.p_images.all()
    products = Product.objects.filter(category=product.category).exclude(pid=pid)[:4]
    reviews = ProductReview.objects.filter(product=product).order_by("-date")
    review_form = ProductReviewForm()
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
    
    review_form = ProductReviewForm()
    
    make_review = True
    
    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=request.user,product=product).count()
        
        if user_review_count > 0:
            make_review = False
    
    
    context = {
        "p":product,
        "make_review":make_review,
        "review_form":review_form,
        "p_image":p_image,
        "average_rating":average_rating,
        "reviews":reviews,
        "products":products,
    }
    
    return render(request,"core/product-detail.html",context)

def tag_list(request,tag_slug=None):
    
    products = Product.objects.filter(product_status = "published").order_by("-id")
    
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag , slug=tag_slug)
        products = products.filter(tags__slug =tag_slug)
        
    context={
        "products":products,
        "tag":tag,
    }
    
    return render(request, "core/tag.html",context)

def ajax_add_review(request, pid):
    # 1. Check for POST method and authenticated user
    if request.method != "POST" or not request.user.is_authenticated:
        return JsonResponse({'bool': False, 'error': 'Invalid request or user not logged in.'}, status=400)
        
    # 2. Get the product safely
    product = get_object_or_404(Product, pk=pid)
    user = request.user
    
    # 3. Safely retrieve POST data
    review_text = request.POST.get('review')
    rating_val = request.POST.get('rating')

    # Optional: Basic data validation
    if not review_text or not rating_val:
        return JsonResponse({'bool': False, 'error': 'Review text or rating is missing.'}, status=400)

    # Convert rating to an integer (if your model expects an integer)
    try:
        rating_val = int(rating_val)
    except ValueError:
        return JsonResponse({'bool': False, 'error': 'Rating must be a number.'}, status=400)
    
    # 4. Create the review
    review = ProductReview.objects.create(
        user=user,
        product=product,
        review=review_text,
        rating=rating_val,
    )
    
    # 5. Prepare the context for the AJAX response
    context = {
        'user': user.username,
        # Use str() for safety in JSON response
        'review': review.review, 
        'rating': str(review.rating),
        'date': review.date.strftime("%b %d, %Y"), # Add date for display
    }
    
    # 6. Calculate average review
    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))
    
    return JsonResponse(
        {
            'bool': True,
            'context': context,
            'avg_reviews': average_reviews,
        }
    )
    
def search_view(request):
    query = request.GET.get("q","")
    
    products = Product.objects.filter(Q(title__icontains = query)|Q (description__icontains = query)| Q(tags__name__icontains = query)).distinct().order_by("-date")
    
    context = {
        "products":products,
        "query":query,
    }
    
    return render(request,"core/search.html",context)


def filter_product(request):
    try:
        categories = request.GET.getlist('category[]')
        vendors = request.GET.getlist('vendor[]')
        
        min_price = request.GET['min_price']
        max_price = request.GET['max_price']
        
        if min_price:
            min_price = float(min_price)
        if max_price:
            max_price = float(max_price)
        
        products = Product.objects.filter(product_status="published").order_by("-id").distinct()
        
        if min_price is not None:
            products = products.filter(price__gte=min_price)

        if max_price is not None:
            products = products.filter(price__lte=max_price)
        
        if len(categories)>0:
            products = products.filter(category__id__in=categories).distinct()
            
        if len(vendors)>0:
            products = products.filter(vendor__id__in=vendors).distinct()
            
        context ={
            "products":products,
        }
        # Assuming render_to_string is imported correctly
        data = render_to_string('core/async/product-list.html',context)
        
        # If everything succeeds
        return JsonResponse({"data":data}) 

    except Exception as e:
        # Log the error on the server side
        print("An error occurred in filter_product:")
        print(traceback.format_exc()) # Prints a detailed stack trace

        # Return a 500 status code with a simple error message to the frontend
        return JsonResponse({"error": "An internal server error occurred"}, status=500)
    
    
def add_to_cart(request):
    print("add to cart called")

    product_id = request.GET.get("id")
    if not product_id:
        return JsonResponse({"error": "Invalid product"}, status=400)

    try:
        qty = int(request.GET.get("qty", 1))
    except ValueError:
        qty = 1

    try:
        price = float(request.GET.get("price", 0))
    except ValueError:
        price = 0.0

    cart_product = {
        str(product_id): {
            "title": request.GET.get("title", ""),
            "qty": qty,
            "price": price,
            "image": request.GET.get("image", ""),
        }
    }

    cart = request.session.get("cart_data_obj", {})

    if str(product_id) in cart:
        cart[str(product_id)]["qty"] += qty
    else:
        cart.update(cart_product)

    request.session["cart_data_obj"] = cart
    request.session.modified = True

    return JsonResponse({
        "data": cart,
        "totalcartitems": len(cart),
    })


def cart_view(request):
    cart = request.session.get("cart_data_obj", {})

    cart_total_amount = 0
    for item in cart.values():
        qty = int(item.get("qty", 0))
        price = float(item.get("price", 0))
        cart_total_amount += qty * price

    return render(request, "core/cart.html", {
        "cart_data": cart,
        "totalcartitems": len(cart),
        "cart_total_amount": cart_total_amount,
    })


def delete_item_from_cart(request):
    product_id = str(request.GET.get('id'))

    if 'cart_data_obj' in request.session:
        cart_data = request.session['cart_data_obj']

        if product_id in cart_data:
            del cart_data[product_id]
            request.session['cart_data_obj'] = cart_data
            request.session.modified = True

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for item in request.session['cart_data_obj'].values():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string(
        "core/async/cart-list.html",
        {
            'cart_data': request.session.get('cart_data_obj', {}),
            'totalcartitems': len(request.session.get('cart_data_obj', {})),
            'cart_total_amount': cart_total_amount
        }
    )

    return JsonResponse({
        "data": context,
        "totalcartitems": len(request.session.get('cart_data_obj', {})),
        "cart_total_amount": cart_total_amount
    })

def update_cart(request):
    product_id = str(request.GET.get("id"))
    product_qty = request.GET.get("qty")

    if not product_id or not product_qty:
        return JsonResponse({"error": "Invalid request"}, status=400)

    cart = request.session.get("cart_data_obj", {})

    if product_id in cart:
        cart[product_id]["qty"] = product_qty
        request.session["cart_data_obj"] = cart
        request.session.modified = True

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for item in request.session['cart_data_obj'].values():
            try:
                # Use try/except or safe casting to prevent 500 errors
                cart_total_amount += int(item['qty']) * float(item['price'])
            except (ValueError, TypeError):
                continue 

    context = render_to_string(
        "core/async/cart-list.html",
        {
            "cart_data": cart,
            "totalcartitems": len(cart),
            "cart_total_amount": cart_total_amount,
        }
    )

    return JsonResponse({
        "data": context,
        "totalcartitems": len(cart),
        "cart_total_amount": cart_total_amount,
    })

@login_required
def checkout_view(request):
    host= request.get_host()
    paypal_dict = {
        'business':settings.PAYPAL_RECEIVER_EMAIL,
        'amount':'200',
        'item_name':"Order-Item-No-3",
        'invoice':"INVOICE_NO-3",
        'currency_code':"USD",
        'notify_url':'http://{}{}'.format(host, reverse("core:paypal-ipn")),
        'return_url':'http://{}{}'.format(host, reverse("core:payment-completed")),
        'cancel_url':'http://{}{}'.format(host, reverse("core:payment-failed")),
    }
    
    paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)
    
    cart = request.session.get('cart_data_obj', {})

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for item in request.session['cart_data_obj'].values():
            try:
                # Use try/except or safe casting to prevent 500 errors
                cart_total_amount += int(item['qty']) * float(item['price'])
            except (ValueError, TypeError):
                continue 
            
    return render(request,"core/checkout.html",{
            "cart_data": cart,
            "totalcartitems": len(cart),
            "cart_total_amount": cart_total_amount,
            'paypal_payment_button':paypal_payment_button,
        })
    
def payment_completed_view(request):
    return render(request,'core/payment-completed.html')

def payment_failed_view(request):
    return render(request,'core/payment-failed.html')

@login_required
def customer_dashboard(request):
    orders = CartOrder.objects.filter(user=request.user)
    context = {
        "orders" : orders,
    }
    return render(request,'core/dashboard.html')

def order_detail(request,id):
    order = CartOrder.objects.filter(user=request.user,id=id)
    products =CartOrderItems.objects.filter(order=order)
    context = {
        "products" : products,
    }
    return render(request,'core/order-detail.html')
    
@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    context ={
        "w": wishlist
    }
    return render(request, "core/wishlist.html", context)

def add_to_wishlist(request):
    print("wishlist view hit")
    if not request.user.is_authenticated:
        return JsonResponse({"bool": False, "error": "Login required"})

    product_id = request.GET.get("id")
    product = get_object_or_404(Product, id=product_id)
    
    # Check if already in wishlist
    if Wishlist.objects.filter(user=request.user, product=product).exists():
        return JsonResponse({"bool": True, "message": "Already in wishlist"})

    # Add to wishlist
    Wishlist.objects.create(
        user=request.user,
        product=product, 
    )
    
    return JsonResponse({"bool": True, "message": "Added to wishlist"})

@login_required
def remove_wishlist(request):
    wishlist_id = request.GET.get("id")

    Wishlist.objects.filter(id=wishlist_id, user=request.user).delete()

    wishlist = Wishlist.objects.filter(user=request.user)

    t = render_to_string("core/async/wishlist-list.html", {
        "wishlist": wishlist
    })

    return JsonResponse({
        "bool": True,
        "data": t,
        "w_count": wishlist.count(),
    })



#other pages
def contact(request):
    return render(request,"core/contact.html")

def ajax_contact_form(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        ContactUs.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
        )

        return JsonResponse({
            "bool": True,
            "message": "Message sent successfully"
        })

    return JsonResponse({"bool": False, "message": "Invalid request"})


def about_us(request):
    return render(request, "core/about_us.html")