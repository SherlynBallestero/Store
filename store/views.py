from django.shortcuts import render
from .models import Product, OrderDetail,Order, Customer, FeaturedProducts, Favorite
from .forms import ContactForm, CustomerProfileForm
from .forms import ContactForm, CustomerProfileForm, CheckoutForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import stripe
from django.conf import settings as django_settings
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect,Http404, JsonResponse
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.contrib import messages  # Para mensajes de error/exito
from django.views.decorators.http import require_POST
from decimal import Decimal, ROUND_HALF_UP


 # Create your views here.

TAX_RATE = Decimal("0.075")


def _favorite_product_ids(user, products=None):
    if not user.is_authenticated:
        return set()

    favorites = Favorite.objects.filter(user=user)
    if products is not None:
        favorites = favorites.filter(product__in=products)

    return set(favorites.values_list("product_id", flat=True))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("home"))
        else:
            return render(request, "store/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "store/login.html")
     
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        address = request.POST.get("address", "")
        phone = request.POST.get("phone", "")

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "store/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            Customer.objects.create(
                user=user,
                name=username,
                email=email,
                address=address,
                phone=phone,
            )
        except IntegrityError:
            return render(request, "store/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("home"))
    else:
        return render(request, "store/register.html")
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))
    
def index(request):
    return render(request, "store/index.html",{
        "products":Product.objects.all(),
        "featured_products":FeaturedProducts.objects.all(),
    })

def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    quantity = 1

    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity", "1"))
        except ValueError:
            quantity = 1

    if quantity < 1:
        quantity = 1

    if product.is_available:
        cart = request.session.get('cart', {})  # Obtiene el carrito de la sesión (dict: {product_id: quantity})
        cart_key = str(product.id)  # Usa str para claves
        cart[cart_key] = cart.get(cart_key, 0) + quantity  # Incrementa cantidad
        request.session['cart'] = cart  # Guarda de vuelta
        messages.success(request, f'{quantity} x {product.name} added to cart!')
    else:
        messages.error(request, f'{product.name} is out of stock.')

    next_url = request.POST.get('next') if request.method == 'POST' else None
    if next_url:
        return redirect(next_url)

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return redirect('home')  


def cart_view(request):
    cart = request.session.get('cart', {})

    if request.method == "POST":
        action = request.POST.get("action")
        product_id = request.POST.get("product_id")

        if product_id and product_id in cart:
            if action == "remove":
                del cart[product_id]
                messages.success(request, "Product removed from cart.")
            elif action == "update":
                try:
                    quantity = int(request.POST.get("quantity", "1"))
                except ValueError:
                    quantity = 1

                if quantity <= 0:
                    del cart[product_id]
                else:
                    cart[product_id] = quantity

                messages.success(request, "Cart updated.")

            request.session['cart'] = cart

        return redirect('cart')

    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.filter(id__in=product_ids)
    product_map = {str(p.id): p for p in products}

    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = product_map.get(product_id)
        if not product:
            continue

        subtotal = product.pack_price * quantity
        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    return render(request, "store/cart.html", {
        "cart_items": cart_items,
        "cart_total": total,
    })

def catalog_view(request):
    products = Product.objects.all()

    selected_type = request.GET.get("type", "").strip()
    selected_color = request.GET.get("color", "").strip()
    search_term = request.GET.get("q", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    if selected_type:
        products = products.filter(type=selected_type)

    if selected_color:
        products = products.filter(color__iexact=selected_color)

    if search_term:
        products = products.filter(name__icontains=search_term)

    if min_price:
        products = products.filter(unit_price__gte=min_price)

    if max_price:
        products = products.filter(unit_price__lte=max_price)

    available_colors = Product.objects.exclude(color="").values_list("color", flat=True).distinct().order_by("color")
    favorite_product_ids = _favorite_product_ids(request.user, products)

    return render(request, "store/catalog.html", {
        "products": products,
        "favorite_product_ids": favorite_product_ids,
        "available_colors": available_colors,
        "product_types": Product._meta.get_field("type").choices,
        "selected_type": selected_type,
        "selected_color": selected_color,
        "search_term": search_term,
        "min_price": min_price,
        "max_price": max_price,
    })


def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    pack_price = product.pack_price

    return render(request, "store/product_detail.html", {
        "product": product,
        "pack_price": pack_price,
        "is_favorite": request.user.is_authenticated and Favorite.objects.filter(user=request.user, product=product).exists(),
    })


@login_required
@require_POST
def toggle_favorite(request, pk):
    product = get_object_or_404(Product, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    is_favorite = created

    if not created:
        favorite.delete()
        is_favorite = False

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    if is_ajax:
        return JsonResponse({
            "ok": True,
            "product_id": product.pk,
            "is_favorite": is_favorite,
        })

    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)

    return redirect("product_detail", pk=product.pk)


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            intent = form.cleaned_data["intent"]
            comments = form.cleaned_data["comments"]

            intent_label = "Ask for a service" if intent == "request" else "Offer a service"
            business_subject = f"New Contact Form: {intent_label}"
            business_message = (
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Intent: {intent_label}\n"
                f"Comments: {comments or '(none)'}\n"
            )

            user_subject = "Thanks for contacting Lafont's Flowers"
            user_message = (
                f"Hi {name},\n\n"
                "Thanks for reaching out to Lafont's Flowers. "
                "We received your message and will contact you soon.\n\n"
                "Best regards,\nLafont's Flowers"
            )

            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = getattr(settings, "CONTACT_RECEIVER_EMAIL", settings.DEFAULT_FROM_EMAIL)

            try:
                send_mail(
                    business_subject,
                    business_message,
                    from_email,
                    [to_email],
                    fail_silently=False,
                )
                send_mail(
                    user_subject,
                    user_message,
                    from_email,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, "Message sent successfully. We will contact you soon.")
                return redirect("contact")
            except Exception:
                messages.error(request, "We could not send your message right now. Please try again in a few minutes.")
    else:
        form = ContactForm()

    return render(request, "store/contact.html", {"form": form})


@login_required
def profile_view(request):
    default_email = request.user.email or f"{request.user.username}@noemail.local"
    customer, _ = Customer.objects.get_or_create(
        user=request.user,
        defaults={
            "name": request.user.get_full_name() or request.user.username,
            "email": default_email,
            "address": "",
            "phone": "",
            "preferred_address": "",
        },
    )

    active_tab = request.GET.get("tab", "overview")
    if active_tab not in {"overview", "orders", "edit", "favorites"}:
        active_tab = "overview"

    if request.method == "POST":
        form = CustomerProfileForm(request.POST, instance=customer, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("profile")
        active_tab = "edit"
    else:
        form = CustomerProfileForm(instance=customer, user=request.user)

    orders = (
        Order.objects
        .filter(customer=customer)
        .order_by("-purchase_date")
    )

    favorites = Favorite.objects.filter(user=request.user).select_related("product")

    return render(request, "store/profile.html", {
        "form": form,
        "customer": customer,
        "orders": orders,
        "favorites": favorites,
        "active_tab": active_tab,
    })


@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.filter(id__in=product_ids)
    product_map = {str(p.id): p for p in products}

    cart_items = []
    subtotal_total = Decimal("0.00")
    for product_id, quantity in cart.items():
        product = product_map.get(product_id)
        if not product or not product.pack_price:
            continue
        subtotal = product.pack_price * quantity
        subtotal_total += subtotal
        cart_items.append({"product": product, "quantity": quantity, "subtotal": subtotal})

    tax_total = (subtotal_total * TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    grand_total = subtotal_total + tax_total

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    default_email = request.user.email or ""
    customer = Customer.objects.filter(user=request.user).first()

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            if not django_settings.STRIPE_SECRET_KEY.startswith("sk_"):
                messages.error(request, "Stripe is not configured correctly. STRIPE_SECRET_KEY must start with 'sk_test_' or 'sk_live_'.")
                return render(request, "store/checkout.html", {
                    "form": form,
                    "cart_items": cart_items,
                    "cart_subtotal": subtotal_total,
                    "cart_tax": tax_total,
                    "cart_total": grand_total,
                    "tax_rate_percent": "7.5",
                    "stripe_public_key": django_settings.STRIPE_PUBLIC_KEY,
                })

            stripe.api_key = django_settings.STRIPE_SECRET_KEY
            line_items = []
            for item in cart_items:
                line_items.append({
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": item["product"].name},
                        "unit_amount": int(item["product"].pack_price * 100),
                    },
                    "quantity": item["quantity"],
                })

            if tax_total > 0:
                line_items.append({
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "Sales Tax (7.5%)"},
                        "unit_amount": int(tax_total * 100),
                    },
                    "quantity": 1,
                })

            success_url = (
                request.build_absolute_uri(reverse("checkout_success"))
                + "?session_id={CHECKOUT_SESSION_ID}"
            )
            cancel_url = request.build_absolute_uri(reverse("cart"))

            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=line_items,
                    mode="payment",
                    success_url=success_url,
                    cancel_url=cancel_url,
                    customer_email=form.cleaned_data["email"],
                )
            except stripe.StripeError as e:
                messages.error(request, "Payment service unavailable. Please try again.")
                return render(request, "store/checkout.html", {
                    "form": form,
                    "cart_items": cart_items,
                    "cart_subtotal": subtotal_total,
                    "cart_tax": tax_total,
                    "cart_total": grand_total,
                    "tax_rate_percent": "7.5",
                })

            request.session["checkout_delivery"] = {
                "full_name": form.cleaned_data["full_name"],
                "email": form.cleaned_data["email"],
                "phone": form.cleaned_data["phone"],
                "delivery_address": form.cleaned_data["delivery_address"],
                "notes": form.cleaned_data.get("notes", ""),
            }

            return redirect(session.url)
    else:
        initial = {
            "full_name": customer.name if customer else "",
            "email": (customer.email if customer else "") or default_email,
            "phone": customer.phone if customer else "",
            "delivery_address": (
                customer.preferred_address or customer.address
                if customer else ""
            ),
        }
        form = CheckoutForm(initial=initial)

    return render(request, "store/checkout.html", {
        "form": form,
        "cart_items": cart_items,
        "cart_subtotal": subtotal_total,
        "cart_tax": tax_total,
        "cart_total": grand_total,
        "tax_rate_percent": "7.5",
        "stripe_public_key": django_settings.STRIPE_PUBLIC_KEY,
    })


@login_required
def stripe_success_view(request):
    session_id = request.GET.get("session_id", "").strip()
    if not session_id:
        return redirect("home")

    # Idempotency: return existing order if already processed
    existing_order = Order.objects.filter(stripe_session_id=session_id).first()
    if existing_order:
        return redirect("confirmation", pk=existing_order.pk)

    stripe.api_key = django_settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.StripeError:
        messages.error(request, "Could not verify payment. Please contact us.")
        return redirect("home")

    if session.payment_status != "paid":
        messages.error(request, "Payment was not completed.")
        return redirect("cart")

    delivery = request.session.pop("checkout_delivery", {})
    cart = request.session.pop("cart", {})

    if not cart:
        messages.error(request, "Your cart was empty when processing the order. Please contact us if you were charged.")
        return redirect("home")

    customer, _ = Customer.objects.get_or_create(
        user=request.user,
        defaults={
            "name": delivery.get("full_name") or request.user.username,
            "email": request.user.email or f"{request.user.username}@noemail.local",
            "address": delivery.get("delivery_address", ""),
            "phone": delivery.get("phone", ""),
        },
    )

    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.filter(id__in=product_ids)
    product_map = {str(p.id): p for p in products}

    order = Order.objects.create(
        customer=customer,
        total=0,
        status="pending",
        delivery_address=delivery.get("delivery_address", ""),
        notes=delivery.get("notes", ""),
        stripe_session_id=session_id,
    )

    order_subtotal = Decimal("0.00")
    for product_id, quantity in cart.items():
        product = product_map.get(product_id)
        if not product or not product.pack_price:
            continue
        price = product.pack_price
        OrderDetail.objects.create(order=order, product=product, quantity=quantity, price=price)
        order_subtotal += price * quantity

    order_tax = (order_subtotal * TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    order.total = order_subtotal + order_tax
    order.save()

    return redirect("confirmation", pk=order.pk)


def confirmation_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    # Only the customer who placed the order (or staff) can see it
    if not request.user.is_staff:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer or order.customer != customer:
            raise Http404
    order_items = order.orderdetail_set.select_related("product").all()
    order_subtotal = sum((item.subtotal() for item in order_items), Decimal("0.00"))
    order_tax = (order.total - order_subtotal).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if order_tax < 0:
        order_tax = Decimal("0.00")

    return render(request, "store/confirmation.html", {
        "order": order,
        "order_items": order_items,
        "order_subtotal": order_subtotal,
        "order_tax": order_tax,
        "tax_rate_percent": "7.5",
    })