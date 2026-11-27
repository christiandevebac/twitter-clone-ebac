from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def login_page(request):
    if request.user.is_authenticated:
        return redirect("feed")
    return render(request, "login.html")


@login_required
def feed_page(request):
    return render(request, "feed.html")
