from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from decimal import Decimal

from apps.cart.cart import Cart
from apps.newProduct.models import Product, Variants

# from .models import Order, OrderItem
from apps.ordering.models import Order,OrderItem
from apps.coupon.models import Coupon
from ..vendor.models import Transporter, Vendor,VendorDelivery


def checkout(
    request,
    cart,
    first_name,
    last_name,
    email,
    address,
    phone,
    district,
    sector,
    cell,
    village,
    delivery_address,
    delivery_cost,
    delivery_type,
    cart_cost,
    coupon_code,
    is_paid_now
):
    print(" === coupon code = ", coupon_code)
    coupon_discount = 0
    if coupon_code != "":
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.can_use():
                coupon.use()
                coupon_discount = coupon.discount
        except:
            pass

    try:

        print("before calc: ", type(delivery_cost), type(cart_cost), type(coupon_discount))
        paid_amount = Decimal(delivery_cost) + Decimal(cart_cost) * (100 - coupon_discount) / 100
        paid_amount=cart.get_cart_cost_with_coupen()
        print("paid amount = ", paid_amount)
        order = Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            phone=phone,
            district=district,
            sector=sector,
            cell=cell,
            village=village,
            delivery_address=delivery_address,
            delivery_cost=delivery_cost,
            delivery_type=delivery_type,
            paid_amount=paid_amount,
            used_coupon=coupon_code,
            coupon_discount=coupon_discount,
            is_paid=is_paid_now
        )

        total_quantity = 0
        subtotal_amount = 0
        print("checkout")

        for item in Cart(request):

            total_quantity += item['quantity']
            print("quantity in cart")
            print(total_quantity)
            subtotal_amount += Decimal(item['product']['total_price'] * item['quantity'])
            subtotal_amount=round(Decimal(subtotal_amount),2)
            if item['product']['is_variant']:
                var_id=int(item['product']['variant_id'])
                pro_id=int(item['product']['id'])
                print(pro_id)
            else:
                pro_id=int(item['product']['id'])
                var_id=''

            OrderItem.objects.create(
                order=order,
                product_id=pro_id,
                variant_id=var_id,
                vendor_id=item['product']['vendor_id'],
                price=item['product']['total_price'],
                quantity=item['quantity'],
                is_variant=item['product']['is_variant']
            )
            vendor = Vendor.objects.get(pk=item['product']['vendor_id'])
            order.vendors.add(vendor)

        order.total_quantity = total_quantity
        order.subtotal_amount = subtotal_amount
        notify_customer(order)
        notify_vendor(order)
    except Exception as e:
        raise e

    return order

def notify_vendor(order):
    connection = get_connection() # uses SMTP server specified in settings.py
    connection.open()
    print("vendor order")
    print(order)
    print("vender")
    print(order.vendors)

    from_email = settings.DEFAULT_EMAIL_FROM
    try:

        for vendor in order.vendors.all():
            to_email = vendor.email
            vendor_item_price=0
            vendor_items_total_price=0
            total_quantity= 0
            order_items= OrderItem.objects.filter(order=order)
            delivery_cost=0
            for items in order_items:
                if vendor == items.vendor:
                    vendor_item_price=items.get_product_total_price()
                    vendor_items_total_price+=vendor_item_price*items.quantity
                    total_quantity+=items.quantity
                    if not items.product.is_free_delivery:
                        if order.delivery_type == "Vendor_Delivery":
                            delivery_cost=VendorDelivery.objects.get(vendor=vendor).price
                            is_delivery=True
                            if delivery_cost == None:
                                delivery_cost=0
                                is_delivery=False
                        else:
                            delivery_cost=0
                            is_delivery=False

            total_cost= float(vendor_items_total_price-(order.coupon_discount*vendor_items_total_price/100))
            total_cost += float(delivery_cost)

            vendor_items_total_price=round(Decimal(vendor_items_total_price),2)
            total_cost=round(Decimal(total_cost),2)

            subject = 'New order'
            text_content = 'You have a new order!'
            html_content = render_to_string(
                'order/email_notify_vendor.html', {'order': order,
                'vendor': vendor,
                'subtotal_cost':vendor_items_total_price,
                'delivery_cost':delivery_cost,
                'is_delivery':is_delivery,
                'grand_total':total_cost,
                'total_quantity':total_quantity})

            msg = EmailMultiAlternatives(
                subject, text_content, from_email, [to_email], connection=connection)
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
    except Exception as e:
            print(e)

    connection.close()


def notify_customer(order):
    connection = get_connection() # uses SMTP server specified in settings.py
    connection.open()
    grand_cost=order.paid_amount + Decimal(order.delivery_cost)
    from_email = settings.DEFAULT_EMAIL_FROM
    to_email = order.email
    subject = 'Order confirmation'
    text_content = 'Thank you for the order!'
    html_content = render_to_string(
        'order/email_notify_customer.html', {'order': order,'grand_cost':grand_cost})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email], connection=connection)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

    connection.close()


