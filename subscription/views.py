import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.conf import settings
import requests
from .models import SubscriptionPlan, UserSubscription, PaymentTransaction

def plans_list(request):
    plans = SubscriptionPlan.objects.all()
    return render(request, "subscription/plans_list.html", {"plans": plans})

def generate_esewa_signature(secret_key, data_string):
    secret_key_bytes = secret_key.encode('utf-8')
    data_bytes = data_string.encode('utf-8')
    hmac_sha256 = hmac.new(secret_key_bytes, data_bytes, hashlib.sha256)
    signature_bytes = hmac_sha256.hexdigest()
    return signature_bytes

def checkout(request, plan_name):
    plan = get_object_or_404(SubscriptionPlan, name=plan_name)

    # Generate a unique transaction ID (do it once per session or per checkout page load)
    transaction_id = str(uuid.uuid4())

    # On GET, create a pending payment transaction so you have a transaction ID stored
    if request.method == "GET":
        # Check if a pending transaction for this user and plan exists? Optional.
        # Or simply create a new one:
        PaymentTransaction.objects.create(
            user=request.user,
            transaction_id=transaction_id,
            product_id=plan.name,
            amount=plan.price,
            status="pending"
        )
        signature = ""
        # Pass variables to render the form dynamically
        context = {
            "plan": plan,
            "transaction_id": transaction_id,
            "success_url": request.build_absolute_uri(f'/subscription/payment-success/?transaction_id={transaction_id}'),
            "failure_url": request.build_absolute_uri(f'/subscription/payment-failure/?transaction_id={transaction_id}'),
            "merchant_id": settings.ESEWA_MERCHANT_ID,
            "signature": signature,
        }
        return render(request, "subscription/checkout.html", context)

    # On POST, process the payment method selection
    elif request.method == "POST":
        payment_method = request.POST.get("payment_method")
        # Retrieve existing pending payment by transaction_id if posted
        transaction_id_post = request.POST.get("transaction_id")
        try:
            payment = PaymentTransaction.objects.get(transaction_id=transaction_id_post)
        except PaymentTransaction.DoesNotExist:
            # Handle error or redirect
            return redirect('subscription:plans_list')

        if payment_method == "esewa":
            # Prepare all amounts; adjust if you use tax or service charges
            amount = payment.amount
            tax_amount = 0
            product_service_charge = 0
            product_delivery_charge = 0
            total_amount = amount + tax_amount + product_service_charge + product_delivery_charge

            # All values as string
            total_amount_str = str(total_amount)
            transaction_uuid = payment.transaction_id
            product_code = settings.ESEWA_MERCHANT_ID

            # Prepare the string exactly as per eSewa requirements
            data_string = f"total_amount={total_amount_str},transaction_uuid={transaction_uuid},product_code={product_code}"


            # Generate signature using your secret key from settings
            signature = generate_esewa_signature(settings.ESEWA_SECRET_KEY, data_string)
            print(f"Generated eSewa signature: {signature}")

            esewa_payload = {
            'amount': str(amount),
            'tax_amount': str(tax_amount),
            'total_amount': total_amount_str,
            'transaction_uuid': transaction_uuid,
            'product_code': product_code,
            'product_service_charge': str(product_service_charge),
            'product_delivery_charge': str(product_delivery_charge),
            'success_url': request.build_absolute_uri(f'/subscription/payment-success/?transaction_id={transaction_uuid}'),
            'failure_url': request.build_absolute_uri(f'/subscription/payment-failure/?transaction_id={transaction_uuid}'),
            'signed_field_names': "total_amount,transaction_uuid,product_code",
            'signature': signature,
            'plan': plan,
            }

            return render(request, 'subscription/checkout.html', esewa_payload)
        else:
            payment.status = "failed"
            payment.save()
            return redirect('subscription:payment_failure')

def payment_success(request):
    transaction_id = request.GET.get('transaction_id')
    ref_id = request.GET.get('refId')
    amt = request.GET.get('amt')

    payment = get_object_or_404(PaymentTransaction, transaction_id=transaction_id)

    # Verify with eSewa API
    verify_payload = {
        'amt': str(payment.amount),
        'scd': settings.ESEWA_MERCHANT_ID,
        'rid': ref_id,
        'pid': transaction_id,
    }
    response = requests.post('https://uat.esewa.com.np/epay/transrec', data=verify_payload)
    if "Success" in response.text:
        payment.status = "success"
        payment.save()

        # Subscription logic here
        plan = SubscriptionPlan.objects.get(name=payment.product_id)
        start_date = timezone.now()
        end_date = start_date + timezone.timedelta(days=plan.duration_days)
        UserSubscription.objects.update_or_create(
            user=payment.user,
            plan=plan,
            defaults={"start_date": start_date, "end_date": end_date, "active": True}
        )
        return render(request, "subscription/payment_success.html", {"payment": payment, "ref_id": ref_id})
    else:
        payment.status = "failed"
        payment.save()
        return redirect('subscription:payment_failure')
    
def payment_failure(request):
    transaction_id = request.GET.get('transaction_id')
    payment = get_object_or_404(PaymentTransaction, transaction_id=transaction_id)
    payment.status = "failed"
    payment.save()
    return render(request, "subscription/payment_failed.html", {"payment": payment})


import hmac
import hashlib
import base64

def generate_esewa_signature(secret_key, data_string):
    """
    Generate HMAC SHA256 base64-encoded signature for eSewa.

    :param secret_key: eSewa secret key (string)
    :param data_string: concatenated string of fields, e.g.
        "total_amount=100,transaction_uuid=241028,product_code=EPAYTEST"
    :return: base64-encoded signature string
    """
    secret_key_bytes = secret_key.encode('utf-8')
    data_bytes = data_string.encode('utf-8')
    hmac_obj = hmac.new(secret_key_bytes, data_bytes, hashlib.sha256)
    signature_bytes = hmac_obj.digest()
    signature = base64.b64encode(signature_bytes).decode('utf-8')
    return signature