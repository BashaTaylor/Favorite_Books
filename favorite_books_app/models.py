from django.db import models
import re

# Create your models here.
class UserManager(models.Manager):
    def register_validator(self, postData):
        errors = {}
        users = User.objects.filter(email=postData['email'])
        if users:
            errors['existing_user'] = 'Account with email already exists.'
        EMAIL_REGEX=re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData['email']):
            errors['email']=("Invalid email address!")
        if len(postData['first_name']) < 2:
            errors['first_name'] = 'First name requires at least 2 characters'
        if len(postData['last_name']) < 2:
            errors['last_name'] = 'Last name requires at least 2 characters.'
        if len(postData['password']) < 8:
            errors['password'] = 'Password requires at least 8 characters.'
        if postData['password'] != postData['confirm_password']:
            errors['confirm_password']='Password must match.'
        return errors
    def login_validator(self, postData):
        errors = {}
        users = User.objects.filter(email=postData['email'])
        if len(postData['email']) < 1:
            errors['email'] = 'Email can not be blank.'
        if len(postData['password']) < 8:
            errors['password'] = 'Password requires at least 8 characters.'
    def edit_validator(self, postData, logged_user_id):
        errors = {}
        users = User.objects.filter(email=postData['email'])
        user_tied_to_email = users[0]
        if users:
            my_user = User.objects.get(id=logged_user_id)
            if my_user.email != user_tied_to_email:
                errors['email'] = 'Email is already in use.'
        if len(postData['first_name']) < 2:
            errors['first_name'] = 'First name requires at least 2 characters.'
        if len(postData['last_name']) < 2:
            errors['last_name'] = 'Last name requires at least 2 characters'
        if len(postData['password']) < 8:
            errors['password'] = 'Password requires at least 8 characters.'
        if postData['password'] != postData['confirm_password']:
            errors['confirm_password']='Password must match.'
        return errors

class User(models.Model):
    first_name=models.CharField(max_length=45)
    last_name=models.CharField(max_length=45)
    email=models.CharField(max_length=255)
    password=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects=UserManager()
    

class BookManager(models.Manager):
    #define BookManager:
    def book_validator(self,postData):
        errors = {}
        if len(postData['title']) < 1:
            errors['title'] = 'Title can not be blank.'
        if len(postData['description']) < 5:
            errors['description'] = 'Description requires at least 5 characters.'
        return errors


class Book(models.Model):
    title = models.CharField(max_length = 255)
    description = models.CharField(max_length = 255)
    uploaded_by = models.ForeignKey(User, related_name="books_uploaded", on_delete=models.CASCADE)
    users_who_like = models.ManyToManyField(User, related_name = "liked_books")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = BookManager()


