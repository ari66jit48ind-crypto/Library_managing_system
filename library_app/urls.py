from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
   path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),


    # Members
    path('members/', views.member_list, name='member_list'),
    path('members/add/', views.member_add, name='member_add'),
    path('members/<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('members/<int:pk>/delete/', views.member_delete, name='member_delete'),
    path('members/<int:pk>/', views.member_detail, name='member_detail'),

    # Books
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_add, name='book_add'),
    path('books/<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),

    # Records
    path('records/open/', views.open_records, name='open_records'),
    path('records/closed/', views.closed_records, name='closed_records'),
    path('records/issue/', views.issue_book, name='issue_book'),
    path('records/<int:pk>/return/', views.return_book, name='return_book'),
    path('records/<int:pk>/delete/', views.record_delete, name='record_delete'),
]
