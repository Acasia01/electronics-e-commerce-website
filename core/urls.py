from django.urls import path,include
from core.views import index,shop,category_view,category_product_view,product_detail_view,tag_list,ajax_add_review,search_view,vendor_view,filter_product,product_list_view,add_to_cart,cart_view,delete_item_from_cart,update_cart,checkout_view, payment_completed_view,payment_failed_view,customer_dashboard,add_to_wishlist,wishlist_view,remove_wishlist,order_detail,contact,ajax_contact_form,about_us

app_name = "core"

urlpatterns = [
    path("", index, name="index"),
    path("shop/", shop ,name="shop"),
    #shop is basically consist of categories
    
    #####   and products have products inside it according to categories
    path('products/<str:cid>/',category_product_view,name="products"),
    path('product/<str:pid>/',product_detail_view,name="product-detail"),
    
    path('product-list/',product_list_view,name="product-list"),
    
    #vendor page
    path('vendor/<str:vid>',vendor_view,name="vendors"),
    
    #tags
    path("products/tag/<slug:tag_slug>/",tag_list,name="tags"),
    
    #Add review
    path("ajax-add-review/<int:pid>/",ajax_add_review,name="ajax-add-review"),
     
    #search
    path("search/",search_view, name="search"),
    
    #path to filter product
    path("filter-products/",filter_product,name="filter-product"),
    
    #path to add-to-cart
    path("add-to-cart/",add_to_cart,name="add-to-cart"),
    
    #cart page
    path("cart/",cart_view,name="cart"),
    
    path("delete_from_cart/",delete_item_from_cart,name="delete_from_cart"),
    
    path("update-cart/",update_cart,name="update-cart"),
    
    path("checkout/",checkout_view,name="checkout"),
    
    path('paypal/', include('paypal.standard.ipn.urls')),
    
    path("payment-completed/",payment_completed_view,name="payment-completed"),
    
    path("payment-failed/",payment_failed_view,name="payment-failed"),
    
    path("dashboard/",customer_dashboard,name="dashboard"),
    
    path("wishlist/",wishlist_view,name="wishlist"),
    
    path("add-to-wishlist/",add_to_wishlist,name="add-to-wishlist"),
    
    path("delete-from-wishlist/",remove_wishlist, name="delete-from-wishlist"),
    
    path('dashboard/', customer_dashboard,name="dashboard"),
    
    path('dashboard/order/<int:id', order_detail,name="order-detail"),
    
    path('contact/',contact,name="contact"),
    path("ajax-contact-form/",ajax_contact_form,name="ajax-contact-form"),
    
    path("about_us/",about_us,name="about_us"),
]