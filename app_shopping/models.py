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
    
    def __str__(self):
        return str(self.id)
    
        
class Admin(BaseModel):
    first_name = models.CharField( max_length=50 , default= "")
    last_name = models.CharField( max_length=50, default= "")
    email = models.EmailField( max_length=50, unique= True)
    phone = models.CharField( max_length=20,  default= "")
    image = models.ImageField( upload_to="AdminImage/", height_field=None, width_field=None, max_length=None, default="AdminImage/dummyadmin.png")
    password = models.TextField(null= False)
    Otp = models.IntegerField(default=0)
    OtpCount = models.IntegerField(default=0)
    OtpStatus = models.BooleanField(default=False)
    no_of_attempts_allowed = models.IntegerField(default=3)
    no_of_wrong_attempts = models.IntegerField(default=0)
    account_status = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class AdminWhitelistToken (models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, blank= True, null=True)
    token = models.TextField(default="")
    created_at = models.DateTimeField( auto_now_add=True, blank=True, null= True)
    
    def __str__(self):
        return str(self.admin)
    
class ProductCategory(BaseModel):
    name = models.CharField( max_length=50, default="")
    description = models.TextField(default="")
    
    def __str__(self):
        return str(self.name)
    
class Product_SubCategory(BaseModel):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, blank=True, null= True)
    name = models.CharField( max_length=50, default="")
    description = models.TextField(default="")
    
    def __str__(self):
        return str(self.name)

    
class Seller(BaseModel):
    first_name = models.CharField( max_length=50, default= "")
    last_name = models.CharField( max_length=50, default= "")
    email = models.EmailField( max_length=254, unique= True)
    phone = models.CharField( max_length=15, default="")
    shop_name = models.CharField( max_length=50, unique=True)
    shop_image = models.ImageField( upload_to="SellerImage/", height_field=None, width_field=None, max_length=None, default="SellerImage/dummyseller.png")
    description = models.TextField(default="")
    shop_address = models.TextField(default="")
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
        return str(self.email)

class SellerWhitelistToken(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, blank= True, null=True)
    token = models.TextField(default="")
    created_at = models.DateTimeField( auto_now_add=False, blank= True, null=True)
    
    def __str__(self) :
        return str(self.seller)
    
class Product(BaseModel):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE,  blank= True, null=True)
    sub_category = models.ForeignKey(Product_SubCategory, on_delete=models.CASCADE, blank= True, null=True)
    title = models.CharField( max_length=50, default= "")
    description = models.TextField(default="")
    image = models.ImageField( upload_to="ProductImages/", height_field=None, width_field=None, max_length=None, default= None, null= True, blank=True)
    size = models.CharField( max_length=50, default="")
    color = models.CharField( max_length=50, default="")
    price = models.DecimalField( max_digits=6, decimal_places=2, default= 0)
    stock_quantity = models.IntegerField(default=0)
    product_available = models.BooleanField(default=False)
    discount_price = models.DecimalField( max_digits=5, decimal_places=2, default=0)
    discount_startdate = models.DateTimeField( auto_now=False, auto_now_add=False, default= None , null= True, blank=True)
    discount_enddate = models.DateTimeField( auto_now=False, auto_now_add=False, default= None, null= True, blank=True)
    discount_available = models.BooleanField(default= False)
    admin_allow_status = models.BooleanField(default= True)
    
    def __str__(self):
        return str(f"{self.title} - {self.seller.email}")
    
class ProductImages(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,  blank= True, null=True)
    image = models.ImageField( upload_to="ProductImages/", height_field=None, width_field=None, max_length=None, default= None, null= True, blank=True)
    
    def __str__(self):
        return str(f"{self.product.title} - {str(self.image.url)}")
    
class Sale(BaseModel):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE,  blank= True, null=True)
    sub_category = models.ForeignKey(Product_SubCategory, on_delete=models.CASCADE, blank= True, null=True)
    sale_percent = models.IntegerField(default=0, validators= [MinValueValidator(0), MaxValueValidator(100)] , help_text="Enter the sale percentage")
    sale_startdate = models.DateTimeField( auto_now=False, auto_now_add=False, default=None, null= True, blank=True)
    sale_enddate = models.DateTimeField( auto_now=False, auto_now_add=False, default=None, null= True, blank=True)
    sale_available = models.BooleanField(default=False)
    admin_allow_status = models.BooleanField(default=False)
    
class Customer(BaseModel):
    first_name = models.CharField( max_length=50, default="")
    last_name = models.CharField( max_length=50, default= "")
    email = models.EmailField( max_length=254, unique=True)
    phone = models.CharField( max_length=15, default="")
    profile_image = models.ImageField( upload_to="CustomerImage/", height_field=None, width_field=None, max_length=None, default="CustomerImage/dummycustomer.png")
    password = models.TextField(null= False)
    Otp = models.IntegerField(default=0)
    OtpCount = models.IntegerField(default=0)
    OtpStatus = models.BooleanField(default=False)
    no_of_attempts_allowed = models.IntegerField(default=3)
    no_of_wrong_attempts = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    admin_allow_status = models.BooleanField(default=True)
    
    def __str__(self):
        return str(self.email)

class CustomerWhitelistToken(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null =True)
    token = models.TextField(default="")
    created_at = models.DateTimeField( auto_now_add=False, null=True, blank=True)

    def __str__(self):
        return str(self.customer)

class Address(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,  blank= True, null=True)
    title = models.CharField( max_length=20, default= "")
    address = models.TextField(default="")
    city = models.CharField( max_length=50 , default="")
    
    def __str__(self):
        return str(f"{self.title} - {self.customer}")
    
class Orders(BaseModel):
    payment_choices = [
        ("paypal", "paypal"),
        ("card", "card")
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,  blank= True, null=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE,  blank= True, null=True)
    final_amount = models.DecimalField( max_digits=10, decimal_places=2, default="")
    payment_method = models.CharField( max_length=50, choices= payment_choices, default="")
    payment_status = models.BooleanField(default= False)
    payment_date = models.DateTimeField( auto_now=False, auto_now_add=False, blank=True, null=True)  # payment date added only when payment status becomes True
    
    def __str__(self) :
        return str(f"{self.payment_status} - {self.customer}")

class OrderDetail(BaseModel):
    shipstatus_choice = [
        ("pending", "pending"),
        ("shipped", "shipped"),
        ("delivered", "delivered")
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE,  blank= True, null=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE,  blank= True, null=True)
    quantity = models.IntegerField(default=0)
    discounted_price = models.DecimalField( max_digits=5, decimal_places=2, default="" )
    total_amount = models.DecimalField( max_digits=5, decimal_places=2, default="")
    size = models.CharField( max_length=50, default="")
    color = models.CharField( max_length=50 , default="")
    ship_date = models.DateTimeField( auto_now=False, auto_now_add=False, default= None, null= True, blank=True)
    ship_status = models.CharField(choices= shipstatus_choice, max_length=50, default="")
    order_approve = models.BooleanField(default=False)
    
    def __str__(self):
        return str(f"{self.product} - {self.quantity} -{self.order}")

class Cart(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,  blank= True, null=True)  
    def __str__(self):
        return str(self.customer)

class CartDetail(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,  blank= True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank= True, null=True)
    quantity = models.IntegerField(default="")

class Likes (BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,  blank= True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,  blank= True, null=True)
    like_status = models.BooleanField(default= False)

