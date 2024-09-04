from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models import Sum


class Basemodel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4,primary_key=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)

    class Meta:
        abstract=True


class Cakecategory(Basemodel):
    category_name= models.CharField(max_length=100)

    

class Cake(Basemodel):
    category= models.ForeignKey(Cakecategory,on_delete=models.CASCADE,related_name="cakes")
    cake_name=models.CharField(max_length=100)
    price=models.IntegerField(default=100)
    images = models.ImageField(upload_to='media')   


class Cart(Basemodel):
    user=models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL,related_name="carts") 
    is_paid=models.BooleanField(default=False)

    def gettotal(self):
        return CartItems.objects.filter(cart=self).aggregate(Sum('cake__price'))['cake__price__sum']

class CartItems(Basemodel):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='cart_items')
    cake = models.ForeignKey(Cake,on_delete=models.CASCADE)        


class Info(models.Model):
    name=models.CharField(max_length=100)
    amount=models.CharField(max_length=100)
    payment_id=models.CharField(max_length=100)
    paid=models.BooleanField(default=False)