# 
# Tango with Django 2 Progress Tests
# By Leif Azzopardi and David Maxwell
# With assistance from Gerardo A-C (https://github.com/gerac83) and Enzo Roiz (https://github.com/enzoroiz)
# 
# Chapter 9 -- Forms
# Last updated: February 6th, 2020
# Revising Author: David Maxwell
# 

#
# In order to run these tests, copy this module to your tango_with_django_project/rango/ directory.
# Once this is complete, run $ python manage.py test rango.tests_chapter9
# 
# The tests will then be run, and the output displayed -- do you pass them all?
# 
# Once you are done with the tests, delete the module. You don't need to put it in your Git repository!
#

import os
import re
import inspect
import tempfile
import rango.models
from rango import forms
from populate_rango import populate
from django.db import models
from django.test import TestCase
from django.conf import settings
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.forms import fields as django_fields

FAILURE_HEADER = f"{os.linesep}{os.linesep}{os.linesep}================{os.linesep}TwD TEST FAILURE =({os.linesep}================{os.linesep}"
FAILURE_FOOTER = f"{os.linesep}"

f"{FAILURE_HEADER} {FAILURE_FOOTER}"


def create_user_object():
    """
    Helper function to create a User object.
    """
    user = User.objects.get_or_create(username='testuser',
                                      first_name='Test',
                                      last_name='User',
                                      email='test@test.com')[0]
    user.set_password('testabc123')
    user.save()

    return user

def create_super_user_object():
    """
    Helper function to create a super user (admin) account.
    """
    return User.objects.create_superuser('admin', 'admin@test.com', 'testpassword')

def get_template(path_to_template):
    """
    Helper function to return the string representation of a template file.
    """
    f = open(path_to_template, 'r')
    template_str = ""

    for line in f:
        template_str = f"{template_str}{line}"

    f.close()
    return template_str

class Chapter9SetupTests(TestCase):
    """
    A simple test to check whether the auth app has been specified.
    """
    def test_installed_apps(self):
        """
        Checks whether the 'django.contrib.auth' app has been included in INSTALLED_APPS.
        """
        self.assertTrue('django.contrib.auth' in settings.INSTALLED_APPS)


class Chapter9ModelTests(TestCase):
    """
    Tests to check whether the UserProfile model has been created according to the specification.
    """
    def test_userprofile_class(self):
        """
        Does the UserProfile class exist in rango.models? If so, are all the required attributes present?
        Assertion fails if we can't assign values to all the fields required (i.e. one or more missing).
        """
        self.assertTrue('UserProfile' in dir(rango.models))

        user_profile = rango.models.UserProfile()

        # Now check that all the required attributes are present.
        # We do this by building up a UserProfile instance, and saving it.
        expected_attributes = {
            'website': 'www.google.com',
            'picture': tempfile.NamedTemporaryFile(suffix=".jpg").name,
            'user': create_user_object(),
        }

        expected_types = {
            'website': models.fields.URLField,
            'picture': models.fields.files.ImageField,
            'user': models.fields.related.OneToOneField,
        }

        found_count = 0

        for attr in user_profile._meta.fields:
            attr_name = attr.name

            for expected_attr_name in expected_attributes.keys():
                if expected_attr_name == attr_name:
                    found_count += 1

                    self.assertEqual(type(attr), expected_types[attr_name], f"{FAILURE_HEADER}The type of attribute for '{attr_name}' was '{type(attr)}'; we expected '{expected_types[attr_name]}'. Check your definition of the UserProfile model.{FAILURE_FOOTER}")
                    setattr(user_profile, attr_name, expected_attributes[attr_name])
        
        self.assertEqual(found_count, len(expected_attributes.keys()), f"{FAILURE_HEADER}In the UserProfile model, we found {found_count} attributes, but were expecting {len(expected_attributes.keys())}. Check your implementation and try again.{FAILURE_FOOTER}")
        user_profile.save()
    

    def test_model_admin_interface_inclusion(self):
        """
        Attempts to access the UserProfile admin interface instance.
        If we don't get a HTTP 200, then we assume that the model has not been registered. Fair assumption!
        """
        super_user = create_super_user_object()
        self.client.login(username='admin', password='testpassword')

        # The following URL should be available if the UserProfile model has been registered to the admin interface.
        response = self.client.get('/admin/rango/userprofile/')
        self.assertEqual(response.status_code, 200, f"{FAILURE_HEADER}When attempting to access the UserProfile in the admin interface, we didn't get a HTTP 200 status code. Did you register the new model with the admin interface?{FAILURE_FOOTER}")


class Chapter9RegisterFormClassTests(TestCase):
    """
    A series of tests to check whether the UserForm and UserProfileForm have been created as per the specification.
    """
    def test_user_form(self):
        """
        Tests whether UserForm is in the correct place, and whether the correct fields have been specified for it.
        """
        self.assertTrue('UserForm' in dir(forms), f"{FAILURE_HEADER}We couldn't find the UserForm class in Rango's forms.py module. Did you create it in the right place?{FAILURE_FOOTER}")
        
        user_form = forms.UserForm()
        self.assertEqual(type(user_form.__dict__['instance']), User, f"{FAILURE_HEADER}Your UserForm does not match up to the User model. Check your Meta definition of UserForm and try again.{FAILURE_FOOTER}")

        fields = user_form.fields
        
        expected_fields = {
            'username': django_fields.CharField,
            'email': django_fields.EmailField,
            'password': django_fields.CharField,
        }
        
        for expected_field_name in expected_fields:
            expected_field = expected_fields[expected_field_name]

            self.assertTrue(expected_field_name in fields.keys(), f"{FAILURE_HEADER}The field {expected_field_name} was not found in the UserForm form. Check you have complied with the specification, and try again.{FAILURE_FOOTER}")
            self.assertEqual(expected_field, type(fields[expected_field_name]), f"{FAILURE_HEADER}The field {expected_field_name} in UserForm was not of the correct type. Expected {expected_field}; got {type(fields[expected_field_name])}.{FAILURE_FOOTER}")
    
    def test_user_profile_form(self):
        """
        Tests whether UserProfileForm is in the correct place, and whether the correct fields have been specified for it.
        """
        self.assertTrue('UserProfileForm' in dir(forms), f"{FAILURE_HEADER}We couldn't find the UserProfileForm class in Rango's forms.py module. Did you create it in the right place?{FAILURE_FOOTER}")
        
        user_profile_form = forms.UserProfileForm()
        self.assertEqual(type(user_profile_form.__dict__['instance']), rango.models.UserProfile, f"{FAILURE_HEADER}Your UserProfileForm does not match up to the UserProfile model. Check your Meta definition of UserProfileForm and try again.{FAILURE_FOOTER}")

        fields = user_profile_form.fields

        expected_fields = {
            'website': django_fields.URLField,
            'picture': django_fields.ImageField,
        }

        for expected_field_name in expected_fields:
            expected_field = expected_fields[expected_field_name]

            self.assertTrue(expected_field_name in fields.keys(), f"{FAILURE_HEADER}The field {expected_field_name} was not found in the UserProfile form. Check you have complied with the specification, and try again.{FAILURE_FOOTER}")
            self.assertEqual(expected_field, type(fields[expected_field_name]), f"{FAILURE_HEADER}The field {expected_field_name} in UserProfileForm was not of the correct type. Expected {expected_field}; got {type(fields[expected_field_name])}.{FAILURE_FOOTER}")


class Chapter9RegistrationTests(TestCase):
    """
    A series of tests that examine changes to views that take place in Chapter 9.
    Specifically, we look at tests related to registering a user.
    """
    def test_new_registration_view_exists(self):
        """
        Checks to see if the new registration view exists in the correct place, with the correct name.
        """
        url = ''

        try:
            url = reverse('rango:register')
        except:
            pass
        
        self.assertEqual(url, '/rango/register/', f"{FAILURE_HEADER}Have you created the rango:register URL mapping correctly? It should point to the new register() view, and have a URL of '/rango/register/' Remember the first part of the URL (/rango/) is handled by the project's urls.py module, and the second part (register/) is handled by the Rango app's urls.py module.{FAILURE_FOOTER}")
    
    def test_registration_template(self):
        """
        Does the register.html template exist in the correct place, and does it make use of template inheritance?
        """
        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'rango')
        template_path = os.path.join(template_base_path, 'register.html')
        self.assertTrue(os.path.exists(template_path), f"{FAILURE_HEADER}We couldn't find the 'register.html' template in the 'templates/rango/' directory. Did you put it in the right place?{FAILURE_FOOTER}")

        template_str = get_template(template_path)
        full_title_pattern = r'<title>(\s*|\n*)Rango(\s*|\n*)-(\s*|\n*)Register(\s*|\n*)</title>'
        block_title_pattern = r'{% block title_block %}(\s*|\n*)Register(\s*|\n*){% (endblock|endblock title_block) %}'

        request = self.client.get(reverse('rango:register'))
        content = request.content.decode('utf-8')

        self.assertTrue(re.search(full_title_pattern, content), f"{FAILURE_HEADER}The <title> of the response for 'rango:register' is not correct. Check your register.html template, and try again.{FAILURE_FOOTER}")
        self.assertTrue(re.search(block_title_pattern, template_str), f"{FAILURE_HEADER}Is register.html using template inheritance? Is your <title> block correct?{FAILURE_FOOTER}")

    def test_registration_get_response(self):
        """
        Checks the GET response of the registration view.
        There should be a form with the correct markup.
        """
        request = self.client.get(reverse('rango:register'))
        content = request.content.decode('utf-8')

        self.assertTrue('<h1>Register for Rango</h1>' in content, f"{FAILURE_HEADER}We couldn't find the '<h1>Register for Rango</h1>' header tag in your register template. Did you follow the specification in the book to the letter?{FAILURE_FOOTER}")
        self.assertTrue('Rango says: <strong>register here!</strong>' in content, f"{FAILURE_HEADER}When loading the register view with a GET request, we didn't see the required 'Rango says: <strong>register here!</strong>'. Check your register.html template and try again.{FAILURE_FOOTER}")
        self.assertTrue('enctype="multipart/form-data"' in content, f"{FAILURE_HEADER}In your register.html template, are you using 'multipart/form-data' for the <form>'s 'enctype'?{FAILURE_FOOTER}")
        self.assertTrue('action="/rango/register/"' in content, f"{FAILURE_HEADER}Is your <form> in register.html pointing to the correct URL for registering a user?{FAILURE_FOOTER}")
        self.assertTrue('<input type="submit" name="submit" value="Register" />' in content, f"{FAILURE_HEADER}We couldn't find the markup for the form submission button in register.html. Check it matches what is in the book, and try again.{FAILURE_FOOTER}")
        self.assertTrue('<p><label for="id_password">Password:</label> <input type="password" name="password" required id="id_password"></p>' in content, f"{FAILURE_HEADER}Checking a random form field in register.html (password), the markup didn't match what we expected. Is your password form field configured correctly?{FAILURE_FOOTER}")
    
    def test_bad_registration_post_response(self):
        """
        Checks the POST response of the registration view.
        What if we submit a blank form?
        """
        request = self.client.post(reverse('rango:register'))
        content = request.content.decode('utf-8')

        self.assertTrue('<ul class="errorlist">' in content)
    
    def test_good_form_creation(self):
        """
        Tests the functionality of the forms.
        Creates a UserProfileForm and UserForm, and attempts to save them.
        Upon completion, we should be able to login with the details supplied.
        """
        user_data = {'username': 'testuser', 'password': 'test123', 'email': 'test@test.com'}
        user_form = forms.UserForm(data=user_data)

        user_profile_data = {'website': 'http://www.bing.com', 'picture': tempfile.NamedTemporaryFile(suffix=".jpg").name}
        user_profile_form = forms.UserProfileForm(data=user_profile_data)

        self.assertTrue(user_form.is_valid(), f"{FAILURE_HEADER}The UserForm was not valid after entering the required data. Check your implementation of UserForm, and try again.{FAILURE_FOOTER}")
        self.assertTrue(user_profile_form.is_valid(), f"{FAILURE_HEADER}The UserProfileForm was not valid after entering the required data. Check your implementation of UserProfileForm, and try again.{FAILURE_FOOTER}")

        user_object = user_form.save()
        user_object.set_password(user_data['password'])
        user_object.save()
        
        user_profile_object = user_profile_form.save(commit=False)
        user_profile_object.user = user_object
        user_profile_object.save()
        
        self.assertEqual(len(User.objects.all()), 1, f"{FAILURE_HEADER}We were expecting to see a User object created, but it didn't appear. Check your UserForm implementation, and try again.{FAILURE_FOOTER}")
        self.assertEqual(len(rango.models.UserProfile.objects.all()), 1, f"{FAILURE_HEADER}We were expecting to see a UserProfile object created, but it didn't appear. Check your UserProfileForm implementation, and try again.{FAILURE_FOOTER}")
        self.assertTrue(self.client.login(username='testuser', password='test123'), f"{FAILURE_HEADER}We couldn't log our sample user in during the tests. Please check your implementation of UserForm and UserProfileForm.{FAILURE_FOOTER}")
    
    def test_good_registration_post_response(self):
        """
        Checks the POST response of the registration view.
        We should be able to log a user in with new details after this!
        """
        post_data = {'username': 'webformuser', 'password': 'test123', 'email': 'test@test.com', 'website': 'http://www.bing.com', 'picture': tempfile.NamedTemporaryFile(suffix=".jpg").name}
        request = self.client.post(reverse('rango:register'), post_data)
        content = request.content.decode('utf-8')

        self.assertTrue('<h1>Register for Rango</h1>' in content, f"{FAILURE_HEADER}We were missing the '<h1>Register for Rango</h1>' header in the registration response.{FAILURE_FOOTER}")
        self.assertTrue('Rango says: <strong>thank you for registering!</strong>' in content, f"{FAILURE_HEADER}When a successful registration occurs, we couldn't find the expected success message. Check your implementation of register.html, and try again.{FAILURE_FOOTER}")
        self.assertTrue('<a href="/rango/">Return to the homepage.</a>' in content, f"{FAILURE_HEADER}After successfully registering, we couldn't find the expected link back to the Rango homepage.{FAILURE_FOOTER}")

        self.assertTrue(self.client.login(username='webformuser', password='test123'), f"{FAILURE_HEADER}We couldn't log in the user we created using your registration form. Please check your implementation of the register() view. Are you missing a .save() call?{FAILURE_FOOTER}")

    def test_base_for_register_link(self):
        """
        Tests whether the registration link has been added to the base.html template.
        This should work for pre-exercises, and post-exercises.
        """
        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'rango')
        base_path = os.path.join(template_base_path, 'base.html')
        template_str = get_template(base_path)
        self.assertTrue('<li><a href="{% url \'rango:register\' %}">Sign Up</a></li>' in template_str)
    

class Chapter9LoginTests(TestCase):
    """
    A series of tests for checking the login functionality of Rango.
    """
    def test_login_url_exists(self):
        """
        Checks to see if the new login view exists in the correct place, with the correct name.
        """
        url = ''

        try:
            url = reverse('rango:login')
        except:
            pass
        
        self.assertEqual(url, '/rango/login/', f"{FAILURE_HEADER}Have you created the rango:login URL mapping correctly? It should point to the new login() view, and have a URL of '/rango/login/' Remember the first part of the URL (/rango/) is handled by the project's urls.py module, and the second part (login/) is handled by the Rango app's urls.py module.{FAILURE_FOOTER}")

    def test_login_functionality(self):
        """
        Tests the login functionality. A user should be able to log in, and should be redirected to the Rango homepage.
        """
        user_object = create_user_object()

        response = self.client.post(reverse('rango:login'), {'username': 'testuser', 'password': 'testabc123'})
        
        try:
            self.assertEqual(user_object.id, int(self.client.session['_auth_user_id']), f"{FAILURE_HEADER}We attempted to log a user in with an ID of {user_object.id}, but instead logged a user in with an ID of {self.client.session['_auth_user_id']}. Please check your login() view.{FAILURE_FOOTER}")
        except KeyError:
            self.assertTrue(False, f"{FAILURE_HEADER}When attempting to log in with your login() view, it didn't seem to log the user in. Please check your login() view implementation, and try again.{FAILURE_FOOTER}")

        self.assertEqual(response.status_code, 302, f"{FAILURE_HEADER}Testing your login functionality, logging in was successful. However, we expected a redirect; we got a status code of {response.status_code} instead. Check your login() view implementation.{FAILURE_FOOTER}")
        self.assertEqual(response.url, reverse('rango:index'), f"{FAILURE_HEADER}We were not redirected to the Rango homepage after logging in. Please check your login() view implementation, and try again.{FAILURE_FOOTER}")

    def test_login_template(self):
        """
        Does the login.html template exist in the correct place, and does it make use of template inheritance?
        """
        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'rango')
        template_path = os.path.join(template_base_path, 'login.html')
        self.assertTrue(os.path.exists(template_path), f"{FAILURE_HEADER}We couldn't find the 'login.html' template in the 'templates/rango/' directory. Did you put it in the right place?{FAILURE_FOOTER}")

        template_str = get_template(template_path)
        full_title_pattern = r'<title>(\s*|\n*)Rango(\s*|\n*)-(\s*|\n*)Login(\s*|\n*)</title>'
        block_title_pattern = r'{% block title_block %}(\s*|\n*)Login(\s*|\n*){% (endblock|endblock title_block) %}'

        request = self.client.get(reverse('rango:login'))
        content = request.content.decode('utf-8')

        self.assertTrue(re.search(full_title_pattern, content), f"{FAILURE_HEADER}The <title> of the response for 'rango:login' is not correct. Check your login.html template, and try again.{FAILURE_FOOTER}")
        self.assertTrue(re.search(block_title_pattern, template_str), f"{FAILURE_HEADER}Is login.html using template inheritance? Is your <title> block correct?{FAILURE_FOOTER}")
    
    def test_login_template_content(self):
        """
        Some simple checks for the login.html template. Is the required text present?
        """
        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'rango')
        template_path = os.path.join(template_base_path, 'login.html')
        self.assertTrue(os.path.exists(template_path), f"{FAILURE_HEADER}We couldn't find the 'login.html' template in the 'templates/rango/' directory. Did you put it in the right place?{FAILURE_FOOTER}")
        
        template_str = get_template(template_path)
        self.assertTrue('<h1>Login to Rango</h1>' in template_str, f"{FAILURE_HEADER}We couldn't find the '<h1>Login to Rango</h1>' in the login.html template.{FAILURE_FOOTER}")
        self.assertTrue('action="{% url \'rango:login\' %}"' in template_str, f"{FAILURE_HEADER}We couldn't find the url lookup for 'rango:login' in your login.html <form>.{FAILURE_FOOTER}")
        self.assertTrue('<input type="submit" value="submit" />' in template_str, f"{FAILURE_HEADER}We couldn't find the submit button in your login.html template. Check it matches what is in the book, and try again.{FAILURE_FOOTER}")
    
    def test_homepage_greeting(self):
        """
        Checks to see if the homepage greeting changes when a user logs in.
        """
        content = self.client.get(reverse('rango:index')).content.decode()
        self.assertTrue('hey there partner!' in content, f"{FAILURE_HEADER}We didn't see the generic greeting for a user not logged in on the Rango homepage. Please check your index.html template.{FAILURE_FOOTER}")

        create_user_object()
        self.client.login(username='testuser', password='testabc123')
        
        content = self.client.get(reverse('rango:index')).content.decode()
        self.assertTrue('howdy testuser!' in content, f"{FAILURE_HEADER}After logging a user, we didn't see the expected message welcoming them on the homepage. Check your index.html template.{FAILURE_FOOTER}")


class Chapter9RestrictedAccessTests(TestCase):
    """
    Some tests to test the restricted access view. Can users who are not logged in see it?
    """
    def test_restricted_url_exists(self):
        """
        Checks to see if the new restricted view exists in the correct place, with the correct name.
        """
        url = ''

        try:
            url = reverse('rango:restricted')
        except:
            pass
        
        self.assertEqual(url, '/rango/restricted/', f"{FAILURE_HEADER}Have you created the rango:restricted URL mapping correctly? It should point to the new restricted() view, and have a URL of '/rango/restricted/' Remember the first part of the URL (/rango/) is handled by the project's urls.py module, and the second part (restricted/) is handled by the Rango app's urls.py module.{FAILURE_FOOTER}")
    
    def test_bad_request(self):
        """
        Tries to access the restricted view when not logged in.
        This should redirect the user to the login page.
        """
        response = self.client.get(reverse('rango:restricted'))
        
        self.assertEqual(response.status_code, 302, f"{FAILURE_HEADER}We tried to access the restricted view when not logged in. We expected to be redirected, but were not. Check your restricted() view.{FAILURE_FOOTER}")
        self.assertTrue(response.url.startswith(reverse('rango:login')), f"{FAILURE_HEADER}We tried to access the restricted view when not logged in, and were expecting to be redirected to the login view. But we were not! Please check your restricted() view.{FAILURE_FOOTER}")
    
    def test_good_request(self):
        """
        Attempts to access the restricted view when logged in.
        This should not redirect. We cannot test the content here. Only links in base.html can be checked -- we do this in the exercise tests.
        """
        create_user_object()
        self.client.login(username='testuser', password='testabc123')

        response = self.client.get(reverse('rango:restricted'))
        self.assertTrue(response.status_code, 200)


class Chapter9LogoutTests(TestCase):
    """
    A few tests to check the functionality of logging out. Does it work? Does it actually log you out?
    """
    def test_bad_request(self):
        """
        Attepts to log out a user who is not logged in.
        This should according to the book redirect you to the login page.
        """
        response = self.client.get(reverse('rango:logout'))
        self.assertTrue(response.status_code, 302)
        self.assertTrue(response.url, reverse('rango:login'))
    
    def test_good_request(self):
        """
        Attempts to log out a user who IS logged in.
        This should succeed -- we should be able to login, check that they are logged in, logout, and perform the same check.
        """
        user_object = create_user_object()
        self.client.login(username='testuser', password='testabc123')

        try:
            self.assertEqual(user_object.id, int(self.client.session['_auth_user_id']), f"{FAILURE_HEADER}We attempted to log a user in with an ID of {user_object.id}, but instead logged a user in with an ID of {self.client.session['_auth_user_id']}. Please check your login() view. This happened when testing logout functionality.{FAILURE_FOOTER}")
        except KeyError:
            self.assertTrue(False, f"{FAILURE_HEADER}When attempting to log a user in, it failed. Please check your login() view and try again.{FAILURE_FOOTER}")
        
        # Now lot the user out. This should cause a redirect to the homepage.
        response = self.client.get(reverse('rango:logout'))
        self.assertEqual(response.status_code, 302, f"{FAILURE_HEADER}Logging out a user should cause a redirect, but this failed to happen. Please check your logout() view.{FAILURE_FOOTER}")
        self.assertEqual(response.url, reverse('rango:index'), f"{FAILURE_HEADER}When logging out a user, the book states you should then redirect them to the homepage. This did not happen; please check your logout() view.{FAILURE_FOOTER}")
        self.assertTrue('_auth_user_id' not in self.client.session, f"{FAILURE_HEADER}Logging out with your logout() view didn't actually log the user out! Please check yout logout() view.{FAILURE_FOOTER}")


class Chapter9LinkTidyingTests(TestCase):
    """
    Some checks to see whether the links in base.html have been tidied up and change depending on whether a user is logged in or not.
    We don't check for category/page links here; these are done in the exercises.
    """
    def test_omnipresent_links(self):
        """
        Checks for links that should always be present, regardless of user state.
        """
        content = self.client.get(reverse('rango:index')).content.decode()
        self.assertTrue('href="/rango/about/"' in content)
        self.assertTrue('href="/rango/"' in content)

        user_object = create_user_object()
        self.client.login(username='testuser', password='testabc123')

        # These should be present.
        content = self.client.get(reverse('rango:index')).content.decode()
        self.assertTrue('href="/rango/about/"' in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
        self.assertTrue('href="/rango/"' in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
    
    def test_logged_in_links(self):
        """
        Checks for links that should only be displayed when the user is logged in.
        """
        user_object = create_user_object()
        self.client.login(username='testuser', password='testabc123')
        content = self.client.get(reverse('rango:index')).content.decode()

        # These should be present.
        self.assertTrue('href="/rango/restricted/"' in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
        self.assertTrue('href="/rango/logout/"' in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")

        # These should not be present.
        self.assertTrue('href="/rango/login/"' not in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
        self.assertTrue('href="/rango/register/"' not in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
    
    def test_logged_out_links(self):
        """
        Checks for links that should only be displayed when the user is not logged in.
        """
        content = self.client.get(reverse('rango:index')).content.decode()

        # These should be present.
        self.assertTrue('href="/rango/login/"' in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
        self.assertTrue('href="/rango/register/"' in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
        
        # These should not be present.
        self.assertTrue('href="/rango/restricted/"' not in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
        self.assertTrue('href="/rango/logout/"' not in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")


class Chapter9ExerciseTests(TestCase):
    """
    A series of tests to check whether the exercises in Chapter 9 have been implemented correctly.
    We check that there is a restricted.html template, whether it uses inheritance, and checks that adding cateories and pages can only be done by a user who is logged in.
    """
    def test_restricted_template_exists(self):
        """
        Checks whether the restricted.html template exists.
        """
        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'rango')
        template_path = os.path.join(template_base_path, 'restricted.html')
        self.assertTrue(os.path.exists(template_path), f"{FAILURE_HEADER}We couldn't find the 'restricted.html' template in the 'templates/rango/' directory. Did you put it in the right place? Did you complete the exercises?{FAILURE_FOOTER}")
    
    def test_restricted_template_inherits(self):
        """
        Checks for template inheritance in restricted.html.
        """
        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'rango')
        template_path = os.path.join(template_base_path, 'restricted.html')

        template_str = get_template(template_path)
        full_title_pattern = r'<title>(\s*|\n*)Rango(\s*|\n*)-(\s*|\n*)Restricted Page(\s*|\n*)</title>'
        block_title_pattern = r'{% block title_block %}(\s*|\n*)Restricted Page(\s*|\n*){% (endblock|endblock title_block) %}'

        user_object = create_user_object()
        self.client.login(username='testuser', password='testabc123')
        request = self.client.get(reverse('rango:restricted'))
        content = request.content.decode('utf-8')

        self.assertTrue(re.search(full_title_pattern, content), f"{FAILURE_HEADER}The <title> of the response for 'rango:restricted' is not correct. Check your restricted.html template, and try again.{FAILURE_FOOTER}")
        self.assertTrue(re.search(block_title_pattern, template_str), f"{FAILURE_HEADER}Is restricted.html using template inheritance? Is your <title> block correct?{FAILURE_FOOTER}")
    
    def test_bad_add_page(self):
        """
        Tests to see if a page cannot be added when not logged in.
        """
        populate()
        response = self.client.get(reverse('rango:add_page', kwargs={'category_name_slug': 'python'}))
        
        self.assertEqual(response.status_code, 302, f"{FAILURE_HEADER}When not logged in and attempting to add a page, we should be redirected. But we weren't. Check your add_page() implementation.{FAILURE_FOOTER}")
        self.assertTrue(response.url.startswith(reverse('rango:login')), f"{FAILURE_HEADER}When not logged in and attempting to add a page, we should be redirected to the login page. But we weren't. Check your add_page() implementation.{FAILURE_FOOTER}")
    
    def test_bad_add_category(self):
        """
        Tests to see if a category cannot be added when not logged in.
        """
        response = self.client.get(reverse('rango:add_category'))
        
        self.assertEqual(response.status_code, 302, f"{FAILURE_HEADER}When attempting to add a category when not logged in, we weren't redirected when we should be. Check your add_category() implementation.{FAILURE_FOOTER}")
        self.assertTrue(response.url.startswith(reverse('rango:login')), f"{FAILURE_HEADER}When attempting to add a category when not logged in, we weren't redirected to the login view. Check your add_category() implementation, and try again.{FAILURE_FOOTER}")

    def test_good_add_page(self):
        """
        Tests to see if a page can be added when logged in.
        """
        populate()
        user_object = create_user_object()
        self.client.login(username='testuser', password='testabc123')
        response = self.client.get(reverse('rango:add_page', kwargs={'category_name_slug': 'python'}))
        
        self.assertEqual(response.status_code, 200, f"{FAILURE_HEADER}We weren't greeted with a HTTP status code when attempting to add a page when logged in. Check your add_page() view.{FAILURE_FOOTER}")
        
        content = response.content.decode()
        self.assertTrue('Add a Page' in content, f"{FAILURE_HEADER}When adding a page (when logged in), we didn't see the expected page. Please check your add_page() view.{FAILURE_FOOTER}")
    
    def test_good_add_category(self):
        """
        Tests to see if a category can be added when logged in.
        """
        user_object = create_user_object()
        self.client.login(username='testuser', password='testabc123')
        response = self.client.get(reverse('rango:add_category'))
        
        self.assertEqual(response.status_code, 200, f"{FAILURE_HEADER}When adding a category (when logged in), we didn't get a HTTP 200 response. Please check your add_category() view.{FAILURE_FOOTER}")

        content = response.content.decode()
        self.assertTrue('Add a Category' in content, f"{FAILURE_HEADER}When adding a category (when logged in), we didn't see the page we expected. Please check your add_category() view.{FAILURE_FOOTER}")

    def test_add_category_link(self):
        """
        Tests to see if the Add Category link only appears when logged in.
        """
        content = self.client.get(reverse('rango:index')).content.decode()

        self.assertTrue(reverse('rango:add_category') not in content, f"{FAILURE_HEADER}The Add Category link was present on Rango's homepage when a user is not logged in. This shouldn't be the case! Please check your base.html template.{FAILURE_FOOTER}")

        user_object = create_user_object()
        self.client.login(username='testuser', password='testabc123')
        content = self.client.get(reverse('rango:index')).content.decode()

        self.assertTrue(reverse('rango:add_category') in content, f"{FAILURE_HEADER}The Add Category link was not present on Rango's homepage when the user was logged in. It should be visible! Please check base.html.{FAILURE_FOOTER}")

    def test_add_page_link(self):
        """
        Tests to see if the Add Page link only appears when logged in.
        """
        populate()
        content = self.client.get(reverse('rango:show_category', kwargs={'category_name_slug': 'python'})).content.decode()
        
        self.assertTrue(reverse('rango:add_page', kwargs={'category_name_slug': 'python'}) not in content, f"{FAILURE_HEADER}The Add Page link was present in the show_category() response when a user was not logged in. It shouldn't be there. Did you do the exercises?{FAILURE_FOOTER}")

        user_object = create_user_object()
        self.client.login(username='testuser', password='testabc123')
        content = self.client.get(reverse('rango:show_category', kwargs={'category_name_slug': 'python'})).content.decode()

        self.assertTrue(reverse('rango:add_page', kwargs={'category_name_slug': 'python'}) in content, f"{FAILURE_HEADER}The Add Page link was not present when a user was logged in, and looking at the show_category() view. Did you make a mistake in your category.html template?{FAILURE_FOOTER}")
