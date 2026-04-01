from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import Manager


class Member(models.Model):
    MEMBERSHIP_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff'),
        ('public', 'Public'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES, default='student')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    joined_date = models.DateField(default=timezone.now)
    member_id = models.CharField(max_length=20, unique=True, blank=True)
    max_books_allowed = models.IntegerField(default=5)

    if TYPE_CHECKING:
        borrowrecord_set: 'Manager[BorrowRecord]'

    def save(self, *args, **kwargs):
        # Set max_books_allowed based on membership type
        if self.membership_type == 'student':
            self.max_books_allowed = 3
        elif self.membership_type == 'faculty':
            self.max_books_allowed = 7
        elif self.membership_type == 'staff':
            self.max_books_allowed = 5
        elif self.membership_type == 'public':
            self.max_books_allowed = 2
        
        if not self.member_id:
            last = Member.objects.order_by('-pk').first()
            next_id = (last.pk + 1) if last else 1
            self.member_id = f'MEM{next_id:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.member_id})'

    def books_currently_borrowed(self):
        return self.borrowrecord_set.filter(status='open').count()

    def get_membership_type_display(self):
        return dict(self.MEMBERSHIP_CHOICES).get(self.membership_type, self.membership_type)

    class Meta:
        ordering = ['-pk']


class Book(models.Model):
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('technology', 'Technology'),
        ('history', 'History'),
        ('biography', 'Biography'),
        ('children', 'Children'),
        ('reference', 'Reference'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('issued', 'Issued'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]

    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='other')
    publisher = models.CharField(max_length=200, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    description = models.TextField(blank=True)
    added_date = models.DateField(default=timezone.now)

    if TYPE_CHECKING:
        borrowrecord_set: 'Manager[BorrowRecord]'

    def __str__(self):
        return f'{self.title} by {self.author}'

    def is_available(self):
        return self.available_copies > 0

    class Meta:
        ordering = ['-pk']


class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Set due date to 7 days from issue date if not set
        if not self.due_date:
            self.due_date = self.issue_date + timedelta(days=7)
        
        # AUTO CALCULATE FINE
        today = timezone.now().date()
        
        if self.status == 'open':
            if self.due_date < today:
                self.status = 'overdue'
                days_overdue = (today - self.due_date).days
                self.fine_amount = Decimal(days_overdue * 2)
            else:
                self.fine_amount = Decimal('0.00')
        elif self.status == 'overdue':
            # Recalculate fine for existing overdue records
            if self.due_date < today:
                days_overdue = (today - self.due_date).days
                self.fine_amount = Decimal(days_overdue * 2)
        
        super().save(*args, **kwargs)
    
    def calculate_fine(self):
        """Auto calculate current fine amount"""
        today = timezone.now().date()
        if self.status in ['open', 'overdue'] and self.due_date < today:
            days_overdue = (today - self.due_date).days
            return Decimal(days_overdue * 2)
        return Decimal('0.00')
    
    def days_overdue(self):
        """Auto calculate days overdue"""
        today = timezone.now().date()
        if self.status in ['open', 'overdue'] and self.due_date < today:
            return (today - self.due_date).days
        return 0

    def __str__(self):
        return f'{self.member.name} - {self.book.title} ({self.status})'

    class Meta:
        ordering = ['-issue_date']