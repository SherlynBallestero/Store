from django.shortcuts import render
from .models import Product, OrderDetail,Order, Customer, FeaturedProducts
from .forms import ContactForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.contrib import messages  # Para mensajes de error/exito


 # Create your views here.

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
    if product.available_quantity > 0:
        cart = request.session.get('cart', {})  # Obtiene el carrito de la sesión (dict: {product_id: quantity})
        cart_key = str(product.id)  # Usa str para claves
        cart[cart_key] = cart.get(cart_key, 0) + 1  # Incrementa cantidad
        request.session['cart'] = cart  # Guarda de vuelta
        messages.success(request, f'{product.name} added to cart!')
    else:
        messages.error(request, f'{product.name} is out of stock.')
    
    # Redirige a la página anterior (o a catálogo si no hay referer)
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

    return render(request, "store/catalog.html", {
        "products": products,
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
    pack_price = None

    if product.pack_quantity:
        pack_price = product.unit_price * product.pack_quantity

    return render(request, "store/product_detail.html", {
        "product": product,
        "pack_price": pack_price,
    })


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