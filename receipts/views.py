from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, ReceiptForm 
from .models import Receipt
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime, timedelta
from .export import ReceiptResource
from django.http import HttpResponse
from receipts import models
import json, csv
from django.db.models.functions import TruncMonth 
from django.db.models.functions import TruncMonth, ExtractWeekDay
from django.utils.timezone import make_aware
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.cache import never_cache


@login_required

def home(request):
    return render(request, 'receipts/home.html')
@never_cache
@login_required
def dashboard(request):
    receipts = Receipt.objects.filter(user=request.user).order_by('-date')
    
    total_spent = sum(r.amount for r in receipts)
    
    from collections import defaultdict
    category_totals = defaultdict(float)
    for r in receipts:
        category_totals[r.category] += float(r.amount)
    top_category = max(category_totals.items(), key=lambda x: x[1])[0] if category_totals else None

    context = {
        'receipts': receipts,
        'total_spent': total_spent,
        'top_category': dict(Receipt.CATEGORY_CHOICES).get(top_category, "No data"),
    }
    return render(request, 'receipts/dashboard.html', context)
@never_cache
@login_required
def reports(request):
   
    default_start = make_aware(datetime.now() - timedelta(days=180))
    default_end = make_aware(datetime.now())
    
    try:
        start_date = make_aware(datetime.strptime(
            request.GET.get('start_date'), 
            '%Y-%m-%d'
        )) if request.GET.get('start_date') else default_start
    except (ValueError, TypeError):
        start_date = default_start
        
    try:
        end_date = make_aware(datetime.strptime(
            request.GET.get('end_date'), 
            '%Y-%m-%d'
        )) if request.GET.get('end_date') else default_end
    except (ValueError, TypeError):
        end_date = default_end

    receipts = Receipt.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    )
    
  
    monthly_data = list(
        receipts.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    

    category_data = list(
        receipts.values('category')
        .annotate(total=Sum('amount'))
        .annotate(percentage=100*Sum('amount')/receipts.aggregate(Sum('amount'))['amount__sum'])
        .order_by('-total')
    )
    
    
    weekly_data = list(
        receipts.annotate(weekday=ExtractWeekDay('date'))
        .values('weekday')
        .annotate(total=Sum('amount'))
        .order_by('weekday')
    )
    
    
    weekly_totals = [0.0] * 7
    for day in weekly_data:
        weekly_totals[day['weekday'] - 1] = float(day['total'])

    context = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'weekly_data_json': json.dumps(weekly_totals, cls=DjangoJSONEncoder),
        'monthly_labels_json': json.dumps(
            [d['month'].strftime("%b %Y") for d in monthly_data],
            cls=DjangoJSONEncoder
        ),
        'monthly_totals_json': json.dumps(
            [float(d['total']) for d in monthly_data],
            cls=DjangoJSONEncoder
        ),
        'category_labels_json': json.dumps(
            [dict(Receipt.CATEGORY_CHOICES)[d['category']] for d in category_data],
            cls=DjangoJSONEncoder
        ),
        'category_totals_json': json.dumps(
            [float(d['total']) for d in category_data],
            cls=DjangoJSONEncoder
        ),
    }
    
   
    print("Weekly totals:", weekly_totals)
    print("Monthly data:", monthly_data)
    print("Category data:", category_data)
    
    return render(request, 'receipts/reports.html', context)

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'receipts/signup.html', {'form': form})
@never_cache
@login_required
def upload_receipt(request):
    if request.method == 'POST':
        form = ReceiptForm(request.POST, request.FILES)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.user = request.user
            receipt.save()
            messages.success(request, 'Receipt uploaded successfully!')
            return redirect('dashboard')
    else:
        form = ReceiptForm()
    
    return render(request, 'receipts/upload.html', {'form': form})    
@never_cache
@login_required
def export_data(request):
    dataset = ReceiptResource().export(Receipt.objects.filter(user=request.user))
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="receipts_export.csv"'
    return response
@never_cache
@login_required
def export_reports(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="spending_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Vendor', 'Category', 'Amount'])
    
    receipts = Receipt.objects.filter(user=request.user).order_by('-date')
    for r in receipts:
        writer.writerow([
            r.date.strftime('%Y-%m-%d'),
            r.vendor,
            r.get_category_display(),
            r.amount
        ])
    
    return response
@never_cache
@login_required
def delete_receipt(request, id):
    receipt = get_object_or_404(Receipt, id=id, user=request.user)
    receipt.delete()
    return redirect('dashboard')

def custom_logout(request):
    logout(request)
    return redirect('logout_page')

def logout_page(request):
    return render(request, 'receipts/logout.html')


@login_required
def receipt_detail(request, receipt_id):
    receipt = get_object_or_404(Receipt, id=receipt_id, user=request.user)
    return render(request, 'receipts/receipt_detail.html', {'receipt': receipt})