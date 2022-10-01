from distutils.command.upload import upload
from pyexpat import model
from ssl import create_default_context
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, Group, User, Permission
import re
from myapp import settings


class UserProfileManager(BaseUserManager):
    """Manager for user profiles"""

    def create_user(self, email, username, password=None):
        """Create a new user profiles"""
        if not email:
            raise ValueError('User must have an email address!')

        regex = r'\b[A-Za-z0-9._%+-]+@ourorg.in'
        email = self.normalize_email(email)
        print(email)
        if re.fullmatch(regex,email):
            user = self.model(email=email, username=username)

            user.set_password(password)
            user.save(using=self._db)

            print('here1')
            g = Group.objects.get_or_create(name='Agent')
            user.is_staff=True
            user.groups.set(g)
        else:
            raise ValueError('Sorry! your not Authorized user!')
        # if len(g):
        #     print(g)
        return user

    def create_superuser(self, email, username, password):
        """Create and save a new superuser with given details"""

        regex = r'\b[A-Za-z0-9._%+-]+admin@ourorg.in'
        if re.fullmatch(regex,email):
            user = self.create_user(email, username, password)
            user.is_superuser = True
            user.is_staff = True
            user.save(using=self._db)
            g = Group.objects.get_or_create(name='Admin')
            user.groups.set(g)
        else:
            raise ValueError('Sorry! your not Authorized user!')

        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Database model for use in a system"""
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    profile_pic = models.ImageField(upload_to='home/student/images', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)


    objects = UserProfileManager()


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']


    def get_full_name(self):
        """Retrive full name of user"""
        return self.username


    def get_short_name(self):
        """Retrieve short name of user"""
        return self.username


    def __str__(self):
        """Return string representation of our user"""
        return self.email
    

class CriminalMasterData(models.Model):
    """Store the criminal data"""

    criminal_name = models.CharField(max_length=200)
    criminal_age = models.PositiveIntegerField()
    criminal_dob = models.DateField()
    criminal_image = models.ImageField(upload_to='home/criminals/images', blank=True, null=True)
    crime = models.TextField()
    created_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.criminal_name + '-' + str(self.criminal_age)


class DataLogs(models.Model):
    """Store the logs"""

    match_found = models.BooleanField(default=False)
    match_user = models.ForeignKey(CriminalMasterData, on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.match_found) + (self.created_by.username)



