from django.urls import path
from . import views

from . import views

urlpatterns = [
    path('', views.log_and_reg, name='log_and_reg'),  # Landing page (registration/login)
    path('register', views.register, name='register'),  # Registration
    path('login', views.login, name='login'),  # Login
    path('logout', views.logout, name='logout'),  # Logout

    path('index', views.index, name='index'),  # Main page after login where you add a book
    path('books', views.list_books, name='list_books'),  # Main book list view
    path('books/add', views.add_book, name='add_book'),  # Handles form submission for adding a book
    path('books/<int:book_id>', views.show_one, name='show_book'),  # View a single book

    path('books/<int:book_id>/favorite', views.favorite, name='favorite_book'),  # Add to favorites
    path('books/<int:book_id>/unfavorite', views.unfavorite, name='unfavorite_book'),  # Remove from favorites

    path('books/<int:book_id>/edit', views.edit, name='edit_book'),  # Edit a book
    path('books/<int:book_id>/update', views.update, name='update_book'),  # Update a book
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'), # Delete a book

]
