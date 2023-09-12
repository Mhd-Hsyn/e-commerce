from django.db import models
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class BaseModel(models.Model):
    id = models.UUIDField(default= uuid.uuid4, editable= False, auto_created=True, primary_key= True )
    created_at = models.DateTimeField( auto_now_add=True , null= True, blank=True)
    updated_at = models.DateTimeField( auto_now= True, null= True, blank= True)
    class Meta:
        abstract = True
        
class Admin(BaseModel):
    first_name = models.CharField( max_length=50 , default= "")
    last_name = models.CharField( max_length=50, default= "")
    email = models.EmailField( max_length=50, unique= True)
    phone = models.CharField( max_length=20,  default= "")
    image = models.ImageField( upload_to="Admin_image", height_field=None, width_field=None, max_length=None)
    password = models.TextField(null= False)
    Otp = models.IntegerField(default=0)
    OtpCount = models.IntegerField(default=0)
    OtpStatus = models.BooleanField(default=False)
    no_of_attempts_allowed = models.IntegerField(default=3)
    no_of_wrong_attempts = models.IntegerField(default=0)
    account_status = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.f_name} {self.l_name}"

class AdminWhitelistToken (models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, blank= True, null=True)
    token = models.TextField(default="")
    created_at = models.DateTimeField( auto_now_add=True, blank=True, null= True)
    
    def __str__(self):
        return self.admin
    
class ProductCategory(BaseModel):
    name = models.CharField( max_length=50, default="")
    description = models.TextField()
    
    def __str__(self):
        return self.name
    
class Product_SubCategory(BaseModel):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, blank=True, null= True)
    name = models.CharField( max_length=50, default="")
    description = models.TextField()
    
    def __str__(self):
        return self.name

    
class Seller(BaseModel):
    first_name = models.CharField( max_length=50, default= "")
    last_name = models.CharField( max_length=50, default= "")
    email = models.EmailField( max_length=254, unique= True)
    phone = models.CharField( max_length=15, default="")
    shop_name = models.CharField( max_length=50, unique=True)
    shop_image = models.ImageField( upload_to="Seller_image", height_field=None, width_field=None, max_length=None)
    description = models.TextField()
    shop_address = models.TextField()
    shop_city = models.CharField( max_length=50, default= "" )
    password = models.TextField(null= False)
    Otp = models.IntegerField(default=0)
    OtpCount = models.IntegerField(default=0)
    OtpStatus = models.BooleanField(default=False)
    no_of_attempts_allowed = models.IntegerField(default=3)
    no_of_wrong_attempts = models.IntegerField(default=0)
    account_status = models.BooleanField(default=True)
    admin_allow_status = models.BooleanField(default= False)
    
    def __str__(self):
        return self.email

class SellerWhitelistToken(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, blank= True, null=True)
    token = models.TextField(default="")
    created_at = models.DateTimeField( auto_now_add=False, blank= True, null=True)
    
    def __str__(self) :
        return self.seller
    
class Product(BaseModel):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(Product_SubCategory, on_delete=models.CASCADE)
    title = models.CharField( max_length=50, default= "")
    description = models.TextField()
    image = models.ImageField( upload_to="Product_images", height_field=None, width_field=None, max_length=None, default= None)
    size = models.CharField( max_length=50)
    color = models.CharField( max_length=50)
    price = models.DecimalField( max_digits=6, decimal_places=2)
    stock_quantity = models.IntegerField()
    product_available = models.BooleanField(default=False)
    discount_price = models.DecimalField( max_digits=5, decimal_places=2)
    discount_startdate = models.DateTimeField( auto_now=False, auto_now_add=False, default= None)
    discount_enddate = models.DateTimeField( auto_now=False, auto_now_add=False, default= None)
    discount_available = models.BooleanField(default= False)
    admin_allow_status = models.BooleanField(default= True)
    
    def __str__(self):
        return f"{self.title} - {self.seller.email}"
    
class ProductImages(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField( upload_to="Product_images", height_field=None, width_field=None, max_length=None)
    
    def __str__(self):
        return f"{self.product.title} - {str(self.image.url)}"    
    
class Sale(BaseModel):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(Product_SubCategory, on_delete=models.CASCADE)
    sale_percent = models.IntegerField(default=0, validators= [MinValueValidator(0), MaxValueValidator(100)] , help_text="Enter the sale percentage")
    sale_startdate = models.DateTimeField( auto_now=False, auto_now_add=False, default=None)
    sale_enddate = models.DateTimeField( auto_now=False, auto_now_add=False, default=None)
    sale_available = models.BooleanField(default=False)
    admin_allow_status = models.BooleanField(default=False)
    
class Customer(BaseModel):
    first_name = models.CharField( max_length=50, default="")
    last_name = models.CharField( max_length=50, default= "")
    email = models.EmailField( max_length=254, unique=True)
    phone = models.CharField( max_length=15, default="")
    profile_image = models.ImageField( upload_to="Customer_image", height_field=None, width_field=None, max_length=None)
    password = models.TextField(null= False)
    Otp = models.IntegerField(default=0)
    OtpCount = models.IntegerField(default=0)
    OtpStatus = models.BooleanField(default=False)
    no_of_attempts_allowed = models.IntegerField(default=3)
    no_of_wrong_attempts = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    admin_allow_status = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email

class CustomerWhitelistToken(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null =True)
    token = models.TextField(default="")
    created_at = models.DateTimeField( auto_now_add=False, null=True, blank=True)

    def __str__(self):
        return self.customer

class Address(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    title = models.CharField( max_length=20, default= "")
    address = models.TextField()
    city = models.CharField( max_length=50 , default="")
    
    def __str__(self):
        return f"{self.title} - {self.customer}"
    
class Orders(BaseModel):
    payment_choices = [
        ("paypal", "paypal"),
        ("card", "card")
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    final_amount = models.DecimalField( max_digits=10, decimal_places=2)
    payment_method = models.CharField( max_length=50, choices= payment_choices)
    payment_status = models.BooleanField(default= False)
    payment_date = models.DateTimeField( auto_now=False, auto_now_add=False)  # payment date added only when payment status becomes True
    
    def __str__(self) :
        return f"{self.payment_status} - {self.customer}"

class OrderDetail(BaseModel):
    shipstatus_choice = [
        ("pending", "pending"),
        ("shipped", "shipped"),
        ("delivered", "delivered")
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    discounted_price = models.DecimalField( max_digits=5, decimal_places=2)
    total_amount = models.DecimalField( max_digits=5, decimal_places=2)
    size = models.CharField( max_length=50, default="")
    color = models.CharField( max_length=50)
    ship_date = models.DateTimeField( auto_now=False, auto_now_add=False, default= None)
    ship_status = models.CharField(choices= shipstatus_choice, max_length=50)
    order_approve = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.product} - {self.quantity} -{self.order}"

class Cart(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  
    def __str__(self):
        return self.customer

class CartDetail(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default="")

class Likes (BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    like_status = models.BooleanField(default= False)

