from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe 
from userauths.models  import User
from taggit.managers import TaggableManager
from tinymce.models import HTMLField
from ckeditor_uploader.fields import RichTextUploadingField


STATUS_CHOICE = (
    ("process","Processing"),
    ("shipped","Shipped"),
    ("delivered","Delivered"),
)

STATUS = (
    ("draft","Draft"),
    ("disabled","Disabled"),
    ("rejected","Rejected"),
    ("in_review","In_Review"),
    ("published","Published"),
)

RATING = (
    (1,"⭐☆☆☆☆"),
    (2,"⭐⭐☆☆☆"),
    (3,"⭐⭐⭐☆☆"),
    (4,"⭐⭐⭐⭐☆"),
    (5,"⭐⭐⭐⭐⭐"),
)


# models.py

def user_directory_path(instance, filename):
    # Check if the user is an actual logged-in user (not the AnonymousUser object)
    if not instance.user.is_anonymous:
        user_id = instance.user.id
        return f"user_{user_id}/{filename}"
    else:
        # For AnonymousUser (logged out user)
        return f"user_anonymous/{filename}"

class Category(models.Model):
    cid = ShortUUIDField(unique= True, length=10,max_length=30,prefix="cat")
    title = models.CharField(max_length=100,default="Mobile")
    image = models.ImageField(upload_to="category/")
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
    
class Vendor(models.Model):
    vid = ShortUUIDField(unique= True, length=10,max_length=30,prefix="ven")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to= user_directory_path)
   # description = models.TextField(null=True,blank=True)
    description = RichTextUploadingField(null=True,blank=True)
    
    address = models.CharField(max_length=100 , default="123 hello")
    contact = models.CharField(max_length=15 ,default="123456789")
    chat_resp_time = models.CharField(max_length=100,default="100")
    shipping_time = models.CharField(max_length=100,default="100")
    authentic_rating = models.CharField(max_length=100,default="100")
    days_return = models.CharField(max_length=100,default="100")
    warranty_period = models.CharField(max_length=100,default="100")
    
    user = models.ForeignKey(User,on_delete=models.SET_NULL , null=True)
    
    class Meta:
        verbose_name_plural = "Vendors"
    
    def vendor_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
    
class Tags(models.Model):
    pass
    
    
class Product(models.Model):
    pid = ShortUUIDField( unique= True, length=10,max_length=30,prefix="pr")
    
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True,related_name="category")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL,null=True)
    
    title = models.CharField(max_length=100, default="Earphones")
    
    image = models.ImageField(upload_to= user_directory_path, default="product.jpg")
   #description = models.TextField(null=True,blank=True,default="This is nice product")
    description = RichTextUploadingField(null=True,blank=True,default="This is nice product")
    
    price = models.DecimalField(max_digits=10 , decimal_places=2 , default=500)
    old_price = models.DecimalField(max_digits=10 , decimal_places=2 , default=700)
    
    new_arrival = models.BooleanField(default=False)
    best_seller = models.BooleanField(default=False)
    banner_product = models.BooleanField(default=False)
    
    specifications = RichTextUploadingField(null=True , blank=True)
    type = models.CharField(max_length=100, default="Organic")
    stock_count = models.CharField(max_length=100, default="10")
    life = models.CharField(max_length=100, default="100 Days")
    mfd = models.DateTimeField(auto_now_add=False,null=True,blank=True)
    
    tags = TaggableManager(blank=True)
    
    product_status = models.CharField(choices=STATUS,max_length=10, default="in_review")
    
    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=True)
    digital = models.BooleanField(default=False)
    
    sku = ShortUUIDField(unique=True, length =4,max_length=10, prefix = "sku",alphabet = "123456789")
    
    date= models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null= True, blank=True)
    
    class Meta:
        verbose_name_plural = "Products"
        
    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50"/>' % (self.image.url))
    
    def __str__(self):
        return self.title
    
    def get_percentage(self):
        discount = 100 - (self.price/self.old_price)*100
        return round(discount,0)
    
class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images",default="product.jpg")
    product = models.ForeignKey(Product,related_name="p_images",on_delete=models.SET_NULL,null=True)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Product_Images"



##############################cart, order,orderItems and address ########################    
        
class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICE,max_length=30,default="processing")
    
    class Meta:
        verbose_name_plural = "Cart Orders"

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder , on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=700.00)
    
    
    class Meta:
        verbose_name_plural = "Cart Order Items"
        
    def order_img(self):
        return mark_safe('<img src="/media/%s" width="50" height="50"/>'% (self.image))
    
##############################Product Review, Wishlist, address ######################## 
##############################Product Review, Wishlist, address ######################## 
##############################Product Review, Wishlist, address ######################## 


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, null=True,blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Product Reviews"
        
    def __str__(self):
        return self.product.title
    
    def get_rating(self):
        return self.rating
    
class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Wishlists"
        unique_together = ("user", "product")

        
    def __str__(self):
        return self.product.title if self.product else "Wishlist item"

    
class Address(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    address = models.CharField(max_length=100, null=True,blank=True)
    status = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Addresses"
        
    def __str__(self):
        return self.address or "No address"