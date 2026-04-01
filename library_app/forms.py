from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import Member, Book, BorrowRecord


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'email', 'phone', 'address', 'membership_type', 'status', 'joined_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Address'}),
            'membership_type': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'joined_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 2:
            raise ValidationError('Name must be at least 2 characters long.')
        return name.strip()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Email address is required.')
        if Member.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This email is already registered.')
        return email.lower()

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise ValidationError('Phone number is required.')
        phone = ''.join(filter(str.isdigit, phone))
        if len(phone) < 10 or len(phone) > 15:
            raise ValidationError('Phone number must be between 10 and 15 digits.')
        return phone

    def clean_joined_date(self):
        joined_date = self.cleaned_data.get('joined_date')
        if joined_date and joined_date > timezone.now().date():
            raise ValidationError('Joined date cannot be in the future.')
        return joined_date


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'genre', 'publisher', 'publication_year',
                  'total_copies', 'available_copies', 'status', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Book Title'}),
            'author': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Author Name'}),
            'isbn': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ISBN Number'}),
            'genre': forms.Select(attrs={'class': 'form-input'}),
            'publisher': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Publisher'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Year'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Description'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or len(title.strip()) < 2:
            raise ValidationError('Title must be at least 2 characters long.')
        return title.strip()

    def clean_author(self):
        author = self.cleaned_data.get('author')
        if not author or len(author.strip()) < 2:
            raise ValidationError('Author name must be at least 2 characters long.')
        return author.strip()

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if not isbn:
            raise ValidationError('ISBN is required.')
        isbn = isbn.replace('-', '').replace(' ', '').upper()
        if Book.objects.filter(isbn=isbn).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This ISBN already exists.')
        if not (len(isbn) == 10 or len(isbn) == 13):
            raise ValidationError('ISBN must be 10 or 13 characters long.')
        return isbn

    def clean_total_copies(self):
        total = self.cleaned_data.get('total_copies')
        if total and total < 1:
            raise ValidationError('Total copies must be at least 1.')
        return total

    def clean_available_copies(self):
        available = self.cleaned_data.get('available_copies')
        total = self.cleaned_data.get('total_copies')
        if available and total and available > total:
            raise ValidationError('Available copies cannot exceed total copies.')
        if available and available < 0:
            raise ValidationError('Available copies cannot be negative.')
        return available

    def clean_publication_year(self):
        year = self.cleaned_data.get('publication_year')
        if year:
            current_year = timezone.now().year
            if year < 1000 or year > current_year:
                raise ValidationError(f'Publication year must be between 1000 and {current_year}.')
        return year


class BorrowRecordForm(forms.ModelForm):
    class Meta:
        model = BorrowRecord
        fields = ['member', 'book', 'issue_date', 'due_date', 'notes']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-input'}),
            'book': forms.Select(attrs={'class': 'form-input'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Optional notes'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add type: ignore to suppress Pylance warnings
        self.fields['book'].queryset = Book.objects.filter(available_copies__gt=0, status='available')  # type: ignore
        self.fields['member'].queryset = Member.objects.filter(status='active')  # type: ignore
        if not self.instance.pk:
            today = timezone.now().date()
            self.fields['issue_date'].initial = today
            self.fields['due_date'].initial = today + timedelta(days=7)

    def clean_member(self):
        member = self.cleaned_data.get('member')
        if not member:
            raise ValidationError('Please select a member.')
        if member.status != 'active':
            raise ValidationError('This member is not active and cannot borrow books.')
        
        # Check if member has reached max books allowed
        currently_borrowed = member.books_currently_borrowed()
        if currently_borrowed >= member.max_books_allowed:
            raise ValidationError(
                f'This member has already borrowed {member.max_books_allowed} books. '
                f'Please return some books first. (Currently: {currently_borrowed}/{member.max_books_allowed})'
            )
        return member

    def clean_book(self):
        book = self.cleaned_data.get('book')
        if not book:
            raise ValidationError('Please select a book.')
        if book.available_copies <= 0:
            raise ValidationError('This book is not available for borrowing.')
        return book

    def clean_issue_date(self):
        issue_date = self.cleaned_data.get('issue_date')
        if issue_date and issue_date > timezone.now().date():
            raise ValidationError('Issue date cannot be in the future.')
        return issue_date

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        issue_date = self.cleaned_data.get('issue_date')
        if due_date and issue_date and due_date <= issue_date:
            raise ValidationError('Due date must be after the issue date.')
        return due_date


class ReturnBookForm(forms.ModelForm):
    class Meta:
        model = BorrowRecord
        fields = ['return_date', 'fine_amount', 'notes']
        widgets = {
            'return_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'fine_amount': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Return notes'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['return_date'].initial = timezone.now().date()
        self.fields['return_date'].label = "Return Date"
        self.fields['fine_amount'].label = "Fine Amount"
        self.fields['fine_amount'].help_text = "Auto-calculated fine: ₹2 per day after due date"

    def clean_return_date(self):
        return_date = self.cleaned_data.get('return_date')
        if return_date and return_date > timezone.now().date():
            raise ValidationError('Return date cannot be in the future.')
        return return_date

    def clean_fine_amount(self):
        fine = self.cleaned_data.get('fine_amount')
        if fine and fine < 0:
            raise ValidationError('Fine amount cannot be negative.')
        return fine