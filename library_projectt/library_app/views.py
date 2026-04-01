from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
from .models import Member, Book, BorrowRecord
from .forms import MemberForm, BookForm, BorrowRecordForm, ReturnBookForm


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

def dashboard(request):
    total_members = Member.objects.count()
    total_books = Book.objects.count()
    open_records = BorrowRecord.objects.filter(status__in=['open', 'overdue']).count()
    closed_records = BorrowRecord.objects.filter(status='returned').count()
    active_members = Member.objects.filter(status='active').count()
    available_books = Book.objects.filter(status='available').count()
    overdue_records = BorrowRecord.objects.filter(
        status='overdue', due_date__lt=timezone.now().date()
    ).count()
    recent_borrows = BorrowRecord.objects.select_related('member', 'book').order_by('-issue_date')[:5]
    recent_members = Member.objects.order_by('-pk')[:5]

    context = {
        'total_members': total_members,
        'total_books': total_books,
        'open_records': open_records,
        'closed_records': closed_records,
        'active_members': active_members,
        'available_books': available_books,
        'overdue_records': overdue_records,
        'recent_borrows': recent_borrows,
        'recent_members': recent_members,
    }
    return render(request, 'library_app/dashboard.html', context)


# ─── MEMBERS ─────────────────────────────────────────────────────────────────

def member_list(request):
    query = request.GET.get('q', '')
    filter_status = request.GET.get('status', '')
    members = Member.objects.all()
    if query:
        members = members.filter(
            Q(name__icontains=query) | Q(email__icontains=query) |
            Q(member_id__icontains=query) | Q(phone__icontains=query)
        )
    if filter_status:
        members = members.filter(status=filter_status)
    return render(request, 'library_app/member_list.html', {
        'members': members, 'query': query, 'filter_status': filter_status
    })


def member_add(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f'✅ Member "{member.name}" added successfully! ID: {member.member_id}')
            return redirect('member_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {field}: {error}')
    else:
        form = MemberForm()
    return render(request, 'library_app/member_form.html', {'form': form, 'action': 'Add'})


def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Member "{member.name}" updated successfully!')
            return redirect('member_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {field}: {error}')
    else:
        form = MemberForm(instance=member)
    return render(request, 'library_app/member_form.html', {'form': form, 'action': 'Edit', 'member': member})


def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        name = member.name
        member.delete()
        messages.success(request, f'🗑️ Member "{name}" deleted successfully!')
        return redirect('member_list')
    return render(request, 'library_app/confirm_delete.html', {'object': member, 'type': 'Member'})


def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    borrow_history = BorrowRecord.objects.filter(member=member).select_related('book').order_by('-issue_date')
    active_borrows = borrow_history.filter(status='open')
    
    context = {
        'member': member,
        'borrow_history': borrow_history,
        'active_borrows': active_borrows,
        'now': timezone.now().date(),
    }
    return render(request, 'library_app/member_detail.html', context)


# ─── BOOKS ────────────────────────────────────────────────────────────────────

def book_list(request):
    query = request.GET.get('q', '')
    filter_genre = request.GET.get('genre', '')
    filter_status = request.GET.get('status', '')
    books = Book.objects.all()
    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query) | Q(isbn__icontains=query)
        )
    if filter_genre:
        books = books.filter(genre=filter_genre)
    if filter_status:
        books = books.filter(status=filter_status)
    return render(request, 'library_app/book_list.html', {
        'books': books, 'query': query,
        'filter_genre': filter_genre, 'filter_status': filter_status,
        'genres': Book.GENRE_CHOICES,
    })


def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'✅ Book "{book.title}" added successfully!')
            return redirect('book_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {field}: {error}')
    else:
        form = BookForm()
    return render(request, 'library_app/book_form.html', {'form': form, 'action': 'Add'})


def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Book "{book.title}" updated successfully!')
            return redirect('book_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {field}: {error}')
    else:
        form = BookForm(instance=book)
    return render(request, 'library_app/book_form.html', {'form': form, 'action': 'Edit', 'book': book})


def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'🗑️ Book "{title}" deleted successfully!')
        return redirect('book_list')
    return render(request, 'library_app/confirm_delete.html', {'object': book, 'type': 'Book'})


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    records = BorrowRecord.objects.filter(book=book).select_related('member')
    return render(request, 'library_app/book_detail.html', {'book': book, 'records': records})


# ─── BORROW RECORDS ───────────────────────────────────────────────────────────

def open_records(request):
    today = timezone.now().date()
    
    # Get all open and overdue records
    records = BorrowRecord.objects.filter(status__in=['open', 'overdue']).select_related('member', 'book')
    
    # Auto-update overdue status and calculate fine
    for record in records:
        if record.due_date < today and record.status == 'open':
            record.status = 'overdue'
            days_overdue = (today - record.due_date).days
            record.fine_amount = Decimal(days_overdue * 2)
            record.save()
        elif record.status == 'overdue':
            # Recalculate fine for existing overdue records
            days_overdue = (today - record.due_date).days
            if days_overdue > 0:
                record.fine_amount = Decimal(days_overdue * 2)
                record.save()
    
    # Refresh records after updates
    records = BorrowRecord.objects.filter(status__in=['open', 'overdue']).select_related('member', 'book')
    
    return render(request, 'library_app/open_records.html', {'records': records, 'today': today})


def closed_records(request):
    records = BorrowRecord.objects.filter(status='returned').select_related('member', 'book')
    return render(request, 'library_app/closed_records.html', {'records': records})


def issue_book(request):
    if request.method == 'POST':
        form = BorrowRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            book = record.book
            
            if book.available_copies <= 0:
                messages.error(request, f'❌ No copies of "{book.title}" available!')
                return render(request, 'library_app/issue_form.html', {'form': form})
            
            # Reduce available copies
            book.available_copies -= 1
            if book.available_copies == 0:
                book.status = 'issued'
            book.save()
            
            # Save the record
            record.status = 'open'
            record.fine_amount = Decimal('0.00')
            record.save()
            
            messages.success(request, f'✅ "{book.title}" issued to {record.member.name} successfully! Due in 7 days.')
            return redirect('open_records')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {field}: {error}')
    else:
        form = BorrowRecordForm()
    
    return render(request, 'library_app/issue_form.html', {'form': form})


def return_book(request, pk):
    record = get_object_or_404(BorrowRecord, pk=pk)
    today = timezone.now().date()
    
    # Calculate fine if overdue
    if record.due_date < today and record.status in ['open', 'overdue']:
        days_overdue = (today - record.due_date).days
        calculated_fine = Decimal(days_overdue * 2)
    else:
        calculated_fine = Decimal('0.00')
    
    if request.method == 'POST':
        # Get notes from form
        notes = request.POST.get('notes', '')
        
        # Update the record
        record.status = 'returned'
        record.return_date = today
        record.fine_amount = calculated_fine
        record.notes = notes
        record.save()
        
        # Increase available copies
        book = record.book
        book.available_copies += 1
        if book.available_copies > 0:
            book.status = 'available'
        book.save()
        
        if calculated_fine > 0:
            messages.success(request, f'✅ Book returned successfully! Auto-calculated fine: ₹{calculated_fine}')
        else:
            messages.success(request, f'✅ Book returned successfully! No fine.')
        
        return redirect('closed_records')
    
    context = {
        'record': record,
        'auto_fine': calculated_fine,
        'today': today,
    }
    return render(request, 'library_app/return_form.html', context)


def record_delete(request, pk):
    record = get_object_or_404(BorrowRecord, pk=pk)
    if request.method == 'POST':
        # If record was open, restore book copies
        if record.status in ['open', 'overdue']:
            book = record.book
            book.available_copies += 1
            book.save()
        record.delete()
        messages.success(request, '🗑️ Record deleted successfully!')
        return redirect('open_records')
    return render(request, 'library_app/confirm_delete.html', {'object': record, 'type': 'Record'})