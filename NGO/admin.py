

from django.contrib import admin
from .models import Post, EmailVerificationToken
from django.contrib.auth.models import User  # Remove Group import

admin.site.register(Post)
admin.site.register(EmailVerificationToken)
# Remove admin.site.register(Group)