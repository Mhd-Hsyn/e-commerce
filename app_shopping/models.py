from django.db import models
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class BaseModel(models.Model):
    id = models.UUIDField(default= uuid.uuid4, editable= False, auto_created=True, primary_key= True )
    created_at = models.DateTimeField( auto_now_add=True , null= True)
    updated_at = models.DateTimeField( auto_now= True, null= True)
    class Meta:
        abstract = True

class Admin(BaseModel):
    admin_role =(
        ("superadmin", "superadmin"),
        ("manager", "manager"),
    )
    f_name = models.CharField( max_length=50 , default= "")
    l_name = models.CharField( max_length=50, default= "")
    email = models.EmailField( max_length=50, default="" ,unique= True)
    phone = models.CharField( max_length=20,  default= "")
    password = models.TextField(null= False)
    role = models.CharField(choices= admin_role, max_length=50, default= "superadmin")
    
    def __str__(self):
        return f"{self.f_name} {self.l_name}"
    
class Seller(BaseModel):
    f_name = models.CharField( max_length=50, default= "")
    l_name = models.CharField( max_length=50, default= "")
    email = models.EmailField( max_length=254, default="", unique= True)
    phone = models.CharField( max_length=15, default="")
    profile_name = models.CharField( max_length=50, default="", unique=True)
    profile_image = models.ImageField( upload_to="Seller_image", height_field=None, width_field=None, max_length=None)
    description = models.TextField()
    seller_address = models.TextField()
    seller_city = models.CharField( max_length=50, default= "" )
    password = models.TextField(null= False)
    status = models.BooleanField(default= False)
    
    def __str__(self):
        return self.email
    
class Customer(BaseModel):
    f_name = models.CharField( max_length=50, default="")
    l_name = models.CharField( max_length=50, default= "")
    email = models.EmailField( max_length=254, unique=True, default="")
    phone = models.CharField( max_length=15, default="")
    profile_image = models.ImageField( upload_to="Customer_image", height_field=None, width_field=None, max_length=None)
    password = models.TextField(null= False)
    status = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email

class Address(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    title = models.CharField( max_length=20, default= "")
    address = models.TextField()
    city = models.CharField( max_length=50 , default="")
    
    def __str__(self):
        return f"{self.title} - {self.customer}"
    
class ProductCategory(BaseModel):
    name = models.CharField( max_length=50, default="")
    description = models.TextField()
    
    def __str__(self):
        return self.name
    
class Product_SubCategory(BaseModel):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    name = models.CharField( max_length=50, default="")
    description = models.TextField()
    
    def __str__(self):
        return self.name
    
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
    status = models.BooleanField(default= False)
    
    def __str__(self):
        return f"{self.title} - {self.seller.email}"
    
class ProductImages(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField( upload_to="Product_images", height_field=None, width_field=None, max_length=None)
    
    def __str__(self):
        return f"{self.product.title} - {str(self.image.url)}"
    
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

class Sale(BaseModel):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(Product_SubCategory, on_delete=models.CASCADE)
    sale_percent = models.IntegerField(default=0, validators= [MinValueValidator(0), MaxValueValidator(100)] , help_text="Enter the sale percentage")
    sale_startdate = models.DateTimeField( auto_now=False, auto_now_add=False, default=None)
    sale_enddate = models.DateTimeField( auto_now=False, auto_now_add=False, default=None)
    sale_available = models.BooleanField(default=False)
    status = models.BooleanField(default=False)