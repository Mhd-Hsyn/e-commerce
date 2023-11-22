from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Admin)
admin.site.register(AdminWhitelistToken)
admin.site.register(ProductCategory)
admin.site.register(Product_SubCategory)
admin.site.register(Seller)
admin.site.register(SellerWhitelistToken)
admin.site.register(Product)
admin.site.register(ProductImages)
admin.site.register(Sale)
admin.site.register(Customer)
admin.site.register(CustomerWhitelistToken)
admin.site.register(Address)
admin.site.register(Orders)
admin.site.register(OrderDetail)
admin.site.register(Cart)
admin.site.register(CartDetail)
admin.site.register(Likes)