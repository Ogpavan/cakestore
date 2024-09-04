from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.http import HttpResponseBadRequest
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Info








def index(request):
    cakes= Cake.objects.all()
    context={'cakes':cakes}
    print(context)
    return render(request,'home.html',context)



def login(request):
    if request.method == "POST":
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')

            
            user_obj = User.objects.filter(username=username).first()
            if not user_obj:
                messages.error(request, 'User not found')
                return redirect('/login/')
            
           
            user_obj = authenticate(username=username, password=password)
            if user_obj:
                auth_login(request, user_obj) 
                return redirect('/')
            else:
                messages.error(request, 'Wrong password')
                return redirect('/login/')
        
        except Exception as e:
            messages.error(request, 'Something went wrong')
            return redirect('/login/')  

    return render(request, 'login.html')



def register(request):
    if request.method== "POST":
    
     try:
        username=request.POST.get('username')
        password1=request.POST.get('password1')
        password2=request.POST.get('password2')

        user_obj=User.objects.filter(username=username)
        if user_obj.exists():
            messages.error(request, 'User already exists')
            return redirect ('/register/')
        
        user=User.objects.create_user(username,password1,password2)
        user.save()

        messages.success(request, 'Account created successfully')
        return redirect ('/login/')
    
     except Exception as e:
        messages.error(request, 'Something went wrong')
        return redirect ('/register/')


    return render(request,'register.html')



def add_cart(request,cake_uid):
    user=request.user
    cake_obj=Cake.objects.get(uid=cake_uid)
    cart , _=Cart.objects.get_or_create(user=user,is_paid=False)
    cart_items=CartItems.objects.create(
        cart=cart,
        cake=cake_obj
    )
    return redirect('/')


def order(request):
    cart=Cart.objects.get(is_paid=False,user=request.user)
    context={'carts':cart}
    return render(request,'order.html',context)

def remove_cart(request,cart_items_uid):
    try:

      CartItems.objects.get(uid=cart_items_uid).delete()
      return redirect('/order/')
    
    except Exception as e:
        print(e)
   
   
def review(request):
    return render(request,'review.html')   

def about(request):
    return render(request,'about.html')   



import razorpay
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Info
import logging

logger = logging.getLogger(__name__)

def pay(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        
        if not amount:
            return HttpResponseBadRequest("Amount is required.")
        
        try:
            amount = int(amount) * 100  # Convert to paise
        except ValueError:
            return HttpResponseBadRequest("Invalid amount provided.")

        # Initialize Razorpay client with provided keys
        try:
            client = razorpay.Client(auth=("rzp_test_GkuBoY156QroSM", "Jj3fCDeZTSm3E5CpOMvyUmnW"))
        except Exception as e:
            logger.error(f"Razorpay client initialization failed: {e}")
            return HttpResponseBadRequest(f"Razorpay client initialization failed: {e}")

        # Create a Razorpay order
        try:
            payment_data = client.order.create({
                'amount': amount,
                'currency': 'INR',
                'payment_capture': '1'  # Auto-capture
            })
        except razorpay.errors.BadRequestError as e:
            logger.error(f"Razorpay order creation failed: {e}")
            return HttpResponseBadRequest(f"Razorpay order creation failed: {e}")

        # Save the payment info to the database
        try:
            info = Info(
                name=name,
                amount=amount,  # Store the amount in paise
                payment_id=payment_data['id'],
                paid=False
            )
            info.save()
        except Exception as e:
            logger.error(f"Failed to save payment info: {e}")
            return HttpResponseBadRequest("Failed to save payment information.")

        # Render the payment page with payment details
        return render(request, 'pay.html', {'payment': payment_data})

    # Render the initial payment page
    return render(request, 'pay.html')


@csrf_exempt
def success(request):
    if request.method == "POST":
        try:
            client = razorpay.Client(auth=("rzp_test_GkuBoY156QroSM", "Jj3fCDeZTSm3E5CpOMvyUmnW"))

            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')

            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # Verify the payment signature
            client.utility.verify_payment_signature(params_dict)

            # Update the payment info in the database
            info = Info.objects.get(payment_id=order_id)
            info.paid = True
            info.save()

            return render(request, 'success.html')

        except razorpay.errors.SignatureVerificationError as e:
            logger.error(f"Signature verification failed: {e}")
            return HttpResponseBadRequest("Invalid payment or payment verification failed.")
        except Info.DoesNotExist:
            logger.error(f"Payment record not found for order_id: {order_id}")
            return HttpResponseBadRequest("Payment record not found.")
        except Exception as e:
            logger.error(f"Unexpected error occurred during payment verification: {e}")
            return HttpResponseBadRequest("An unexpected error occurred during payment verification.")

    return HttpResponseBadRequest("Invalid request method.")
