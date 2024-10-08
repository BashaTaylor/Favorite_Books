from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import Book, User
import bcrypt
import logging

logger = logging.getLogger(__name__)

def log_and_reg(request):
    """Renders the login and registration page"""
    return render(request, 'log_and_reg.html')

def register(request):
    """Handles user registration"""
    errors = User.objects.register_validator(request.POST)
    if errors:
        for val in errors.values():
            messages.error(request, val)
        return redirect('/')
    else:
        password = request.POST['password']
        hash_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = User.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
            password=hash_pw
        )
        request.session['userid'] = user.id
        messages.success(request, "Successfully registered account")
        return redirect('/index')

def login(request):
    """Handles user login"""
    if request.method == 'POST':
        users = User.objects.filter(email=request.POST['email'])
        if users:
            logged_user = users[0]
            if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password.encode()):
                request.session['userid'] = logged_user.id
                messages.success(request, "Successfully logged in")
                return redirect('/index')  # Redirect to index.html where user can add a book
            else:
                messages.error(request, "Invalid Email/Password Combo")
        else:
            messages.error(request, "Account not found with that email")
    return redirect('/')

def logout(request):
    """Handles user logout"""
    request.session.flush()
    return redirect('/')

def index(request):
    """Renders the page to add a book (index.html)"""
    if 'userid' not in request.session:
        return redirect('/')
    context = {
        'user': User.objects.get(id=request.session['userid']),
        'all_books': Book.objects.all(),
    }
    return render(request, 'index.html', context)  # Ensure this renders 'index.html'

def add_book(request):
    """Handles adding a new book and redirects to the book list."""
    if request.method == 'POST':
        # Use book_validator to check for errors
        errors = Book.objects.book_validator(request.POST)
        
        if errors:
            # Display validation errors as messages
            for error in errors.values():
                messages.error(request, error)
            # Redirect to the form page to show errors
            return redirect('/index')
        
        # Ensure user is logged in and session contains a valid user ID
        user_id = request.session.get('userid')
        if not user_id:
            messages.error(request, "User not logged in.")
            return redirect('/login')  # Redirect to login page if user ID is missing

        try:
            my_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect('/login')  # Redirect to login page if user is not found
        
        # Create a new book
        new_book = Book.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            uploaded_by=my_user
        )
        
        # Optionally add the book to the user's liked books
        my_user.liked_books.add(new_book)
        
        # Redirect to the book list page
        return redirect('/books')
    
    # For GET requests, render the book addition form
    return render(request, 'index.html')

# def add_book(request):
#     """Handles adding a new book and redirects to the book list (books.html)"""
#     if request.method == 'POST':
#         errors = Book.objects.book_validator(request.POST)
#         if errors:
#             for val in errors.values():
#                 messages.error(request, val)
#             return redirect('/index')  # Redirect back to add book page (index.html) if there are errors
#         else:
#             my_user = User.objects.get(id=request.session['userid'])
#             new_book = Book.objects.create(
#                 title=request.POST['title'], 
#                 description=request.POST['description'],
#                 uploaded_by=my_user
#             )
#             my_user.liked_books.add(new_book)
#             return redirect('/books')  # Redirect to books.html after adding the book

def list_books(request):
    """Displays a list of all books, separated into favorites and others."""
    if 'userid' not in request.session:
        return redirect('/')  # Redirect to login page if user is not logged in

    current_user = User.objects.get(id=request.session['userid'])
    all_books = Book.objects.all()

    # Separate books into favorites and others
    my_favorite_books = [book for book in all_books if current_user in book.users_who_like.all()]
    other_books = [book for book in all_books if current_user not in book.users_who_like.all()]

    context = {
        'user': current_user,
        'my_favorite_books': my_favorite_books,
        'other_books': other_books,
    }

    return render(request, 'books.html', context)

def show_one(request, book_id):
    """Displays the details of a single book."""
    if 'userid' not in request.session:
        return redirect('/')  # Redirect to login page if user is not logged in

    book = get_object_or_404(Book, id=book_id)
    current_user = User.objects.get(id=request.session['userid'])
    
    context = {
        'book': book,
        'current_user': current_user,
    }

    return render(request, 'show_book.html', context)  

def favorite(request, book_id):
    """Adds a book to the user's favorites"""
    if 'userid' not in request.session:
        return redirect('/')
    book = Book.objects.get(id=book_id)
    user = User.objects.get(id=request.session['userid'])
    book.users_who_like.add(user)  # Assuming a many-to-many relationship exists
    return redirect('/books')

def unfavorite(request, book_id):
    """Removes a book from the user's favorites"""
    if 'userid' not in request.session:
        return redirect('/')
    book = Book.objects.get(id=book_id)
    user = User.objects.get(id=request.session['userid'])
    book.users_who_like.remove(user)  # Assuming a many-to-many relationship exists
    return redirect('/books')


def edit(request, book_id):
    """Renders the edit page for a single book."""
    if 'userid' not in request.session:
        return redirect('/')
    
    book = get_object_or_404(Book, id=book_id)
    current_user = get_object_or_404(User, id=request.session['userid'])
    
    context = {
        'book': book,
        'user': current_user
    }
    
    return render(request, 'edit.html', context)

#This function finally worked! :)
def delete_book(request, book_id):
    """Handles the deletion of a book."""
    if 'userid' not in request.session:
        return redirect('/')  # Redirect to login page if user is not logged in

    book = get_object_or_404(Book, id=book_id)
    
    # Optional: Check if the current user is allowed to delete the book
    if book.uploaded_by.id != request.session['userid']:
        messages.error(request, "You are not authorized to delete this book.")
        return redirect('/books')

    # Delete the book
    book.delete()
    messages.success(request, "Book deleted successfully.")
    return redirect('/books')

def update(request, book_id):
    """Handles updating the book and redirects to the book list page."""
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        # Validate form data
        errors = Book.objects.book_validator(request.POST)
        if errors:
            for val in errors.values():
                messages.error(request, val)
            # Render the edit page with error messages
            return render(request, 'edit.html', {'book': book})

        # Update book details
        book.title = request.POST.get('title', book.title)
        book.description = request.POST.get('description', book.description)
        book.save()

        return redirect('list_books')  # Redirect to books list page

    # Render edit page for GET requests
    return render(request, 'edit.html', {'book': book})
def delete (request, book_id):
    """Removes a book from the user's favorites"""
    if 'userid' not in request.session:
        return redirect('/')
    book = Book.objects.get(id=book_id)
    user = User.objects.get(id=request.session['userid'])
    book.users_who_like.remove(user)  # Assuming a many-to-many relationship exists
    return redirect('/books')

def book_validator(postData):
    errors = {}
    # Use `get` to avoid KeyError
    title = postData.get('title', '')
    description = postData.get('description', '')

    if len(title) < 1:
        errors['title'] = "Title is required."
    if len(description) < 1:
        errors['description'] = "Description is required."

    return errors
