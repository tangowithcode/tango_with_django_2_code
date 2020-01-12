# 
# Tango with Django 2 Progress Tests
# By Leif Azzopardi and David Maxwell
# With assistance from Enzo Roiz (https://github.com/enzoroiz)
# 
# Chapter 5 -- Models and Databases
# Last updated: October 3rd, 2019
# Revising Author: David Maxwell
# 

#
# In order to run these tests, copy this module to your tango_with_django_project/rango/ directory.
# Once this is complete, run $ python manage.py test rango.tests_chapter5
# 
# The tests will then be run, and the output displayed -- do you pass them all?
# 
# Once you are done with the tests, delete the module. You don't need to put it in your Git repository!
#

import os
import warnings
import importlib
from rango.models import Category, Page
from django.urls import reverse
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

FAILURE_HEADER = f"{os.linesep}{os.linesep}{os.linesep}================{os.linesep}TwD TEST FAILURE =({os.linesep}================{os.linesep}"
FAILURE_FOOTER = f"{os.linesep}"


class Chapter5DatabaseConfigurationTests(TestCase):
    """
    Is your database configured as the book states?
    These tests should pass if you haven't tinkered with the database configuration.
    N.B. Some of the configuration values we could check are overridden by the testing framework -- so we leave them.
    """
    def setUp(self):
        pass
    
    def does_gitignore_include_database(self, path):
        """
        Takes the path to a .gitignore file, and checks to see whether the db.sqlite3 database is present in that file.
        """
        f = open(path, 'r')
        
        for line in f:
            line = line.strip()
            
            if line.startswith('db.sqlite3'):
                return True
        
        f.close()
        return False
    
    def test_databases_variable_exists(self):
        """
        Does the DATABASES settings variable exist, and does it have a default configuration?
        """
        self.assertTrue(settings.DATABASES, f"{FAILURE_HEADER}Your project's settings module does not have a DATABASES variable, which is required. Check the start of Chapter 5.{FAILURE_FOOTER}")
        self.assertTrue('default' in settings.DATABASES, f"{FAILURE_HEADER}You do not have a 'default' database configuration in your project's DATABASES configuration variable. Check the start of Chapter 5.{FAILURE_FOOTER}")
    
    def test_gitignore_for_database(self):
        """
        If you are using a Git repository and have set up a .gitignore, checks to see whether the database is present in that file.
        """
        git_base_dir = os.popen('git rev-parse --show-toplevel').read().strip()
        
        if git_base_dir.startswith('fatal'):
            warnings.warn("You don't appear to be using a Git repository for your codebase. Although not strictly required, it's *highly recommended*. Skipping this test.")
        else:
            gitignore_path = os.path.join(git_base_dir, '.gitignore')
            
            if os.path.exists(gitignore_path):
                self.assertTrue(self.does_gitignore_include_database(gitignore_path), f"{FAILURE_HEADER}Your .gitignore file does not include 'db.sqlite3' -- you should exclude the database binary file from all commits to your Git repository.{FAILURE_FOOTER}")
            else:
                warnings.warn("You don't appear to have a .gitignore file in place in your repository. We ask that you consider this! Read the Don't git push your Database paragraph in Chapter 5.")


class Chapter5ModelTests(TestCase):
    """
    Are the models set up correctly, and do all the required attributes (post exercises) exist?
    """
    def setUp(self):
        category_py = Category.objects.get_or_create(name='Python', views=123, likes=55)
        Category.objects.get_or_create(name='Django', views=187, likes=90)
        
        Page.objects.get_or_create(category=category_py[0],
                                   title='Tango with Django',
                                   url='https://www.tangowithdjango.com',
                                   views=156)
    
    def test_category_model(self):
        """
        Runs a series of tests on the Category model.
        Do the correct attributes exist?
        """
        category_py = Category.objects.get(name='Python')
        self.assertEqual(category_py.views, 123, f"{FAILURE_HEADER}Tests on the Category model failed. Check you have all required attributes (including those specified in the exercises!), and try again.{FAILURE_FOOTER}")
        self.assertEqual(category_py.likes, 55, f"{FAILURE_HEADER}Tests on the Category model failed. Check you have all required attributes (including those specified in the exercises!), and try again.{FAILURE_FOOTER}")
        
        category_dj = Category.objects.get(name='Django')
        self.assertEqual(category_dj.views, 187, f"{FAILURE_HEADER}Tests on the Category model failed. Check you have all required attributes (including those specified in the exercises!), and try again.{FAILURE_FOOTER}")
        self.assertEqual(category_dj.likes, 90, f"{FAILURE_HEADER}Tests on the Category model failed. Check you have all required attributes (including those specified in the exercises!), and try again.{FAILURE_FOOTER}")
    
    def test_page_model(self):
        """
        Runs some tests on the Page model.
        Do the correct attributes exist?
        """
        category_py = Category.objects.get(name='Python')
        page = Page.objects.get(title='Tango with Django')
        self.assertEqual(page.url, 'https://www.tangowithdjango.com', f"{FAILURE_HEADER}Tests on the Page model failed. Check you have all required attributes (including those specified in the exercises!), and try again.{FAILURE_FOOTER}")
        self.assertEqual(page.views, 156, f"{FAILURE_HEADER}Tests on the Page model failed. Check you have all required attributes (including those specified in the exercises!), and try again.{FAILURE_FOOTER}")
        self.assertEqual(page.title, 'Tango with Django', f"{FAILURE_HEADER}Tests on the Page model failed. Check you have all required attributes (including those specified in the exercises!), and try again.{FAILURE_FOOTER}")
        self.assertEqual(page.category, category_py, f"{FAILURE_HEADER}Tests on the Page model failed. Check you have all required attributes (including those specified in the exercises!), and try again.{FAILURE_FOOTER}")
    
    def test_str_method(self):
        """
        Tests to see if the correct __str__() method has been implemented for each model.
        """
        category_py = Category.objects.get(name='Python')
        page = Page.objects.get(title='Tango with Django')
        
        self.assertEqual(str(category_py), 'Python', f"{FAILURE_HEADER}The __str__() method in the Category class has not been implemented according to the specification given in the book.{FAILURE_FOOTER}")
        self.assertEqual(str(page), 'Tango with Django', f"{FAILURE_HEADER}The __str__() method in the Page class has not been implemented according to the specification given in the book.{FAILURE_FOOTER}")


class Chapter5AdminInterfaceTests(TestCase):
    """
    A series of tests that examines the authentication functionality (for superuser creation and logging in), and admin interface changes.
    Have all the admin interface tweaks been applied, and have the two models been added to the admin app?
    """
    def setUp(self):
        """
        Create a superuser account for use in testing.
        Logs the superuser in, too!
        """
        User.objects.create_superuser('testAdmin', 'email@email.com', 'adminPassword123')
        self.client.login(username='testAdmin', password='adminPassword123')
        
        category = Category.objects.get_or_create(name='TestCategory')[0]
        Page.objects.get_or_create(title='TestPage1', url='https://www.google.com', category=category)
    
    def test_admin_interface_accessible(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200, f"{FAILURE_HEADER}The admin interface is not accessible. Check that you didn't delete the 'admin/' URL pattern in your project's urls.py module.{FAILURE_FOOTER}")
    
    def test_models_present(self):
        """
        Checks whether the two models are present within the admin interface homepage -- and whether Rango is listed there at all.
        """
        response = self.client.get('/admin/')
        response_body = response.content.decode()
        
        # Is the Rango app present in the admin interface's homepage?
        self.assertTrue('Models in the Rango application' in response_body, f"{FAILURE_HEADER}The Rango app wasn't listed on the admin interface's homepage. You haven't added the models to the admin interface.{FAILURE_FOOTER}")
        
        # Check each model is present.
        self.assertTrue('Categories' in response_body, f"{FAILURE_HEADER}The Category model was not found in the admin interface. If you did add the model to admin.py, did you add the correct plural spelling (Categories)?{FAILURE_FOOTER}")
        self.assertTrue('Pages' in response_body, f"{FAILURE_HEADER}The Page model was not found in the admin interface. If you did add the model to admin.py, did you add the correct plural spelling (Pages)?{FAILURE_FOOTER}")
    
    def test_page_display_changes(self):
        """
        Checks to see whether the Page model has had the required changes applied for presentation in the admin interface.
        """
        response = self.client.get('/admin/rango/page/')
        response_body = response.content.decode()
        
        # Headers -- are they all present?
        self.assertTrue('<div class="text"><a href="?o=1">Title</a></div>' in response_body, f"{FAILURE_HEADER}The 'Title' column could not be found in the admin interface for the Page model -- if it is present, is it in the correct order?{FAILURE_FOOTER}")
        self.assertTrue('<div class="text"><a href="?o=2">Category</a></div>' in response_body, f"{FAILURE_HEADER}The 'Category' column could not be found in the admin interface for the Page model -- if it is present, is it in the correct order?{FAILURE_FOOTER}")
        self.assertTrue('<div class="text"><a href="?o=3">Url</a></div>' in response_body, f"{FAILURE_HEADER}The 'Url' (stylised that way!) column could not be found in the admin interface for the Page model -- if it is present, is it in the correct order?{FAILURE_FOOTER}")
        
        # Is the TestPage1 page present, and in order?
        expected_str = '<tr class="row1"><td class="action-checkbox"><input type="checkbox" name="_selected_action" value="1" class="action-select"></td><th class="field-title"><a href="/admin/rango/page/1/change/">TestPage1</a></th><td class="field-category nowrap">TestCategory</td><td class="field-url">https://www.google.com</td></tr>'
        self.assertTrue(expected_str in response_body, f"{FAILURE_HEADER}We couldn't find the correct output in the Page view within the admin interface for page listings. Did you complete the exercises, adding extra columns to the admin view for this model? Are the columns in the correct order?{FAILURE_FOOTER}")


class Chapter5PopulationScriptTests(TestCase):
    """
    Tests whether the population script puts the expected data into a test database.
    All values that are explicitly mentioned in the book are tested.
    Expects that the population script has the populate() function, as per the book!
    """
    def setUp(self):
        """
        Imports and runs the population script, calling the populate() method.
        """
        try:
            import populate_rango
        except ImportError:
            raise ImportError(f"{FAILURE_HEADER}The Chapter 5 tests could not import the populate_rango. Check it's in the right location (the first tango_with_django_project directory).{FAILURE_FOOTER}")
        
        if 'populate' not in dir(populate_rango):
            raise NameError(f"{FAILURE_HEADER}The populate() function does not exist in the populate_rango module. This is required.{FAILURE_FOOTER}")
        
        # Call the population script -- any exceptions raised here do not have fancy error messages to help readers.
        populate_rango.populate()
    
    def test_categories(self):
        """
        There should be three categories from populate_rango -- Python, Django and Other Frameworks.
        """
        categories = Category.objects.filter()
        categories_len = len(categories)
        categories_strs = map(str, categories)
        
        self.assertEqual(categories_len, 3, f"{FAILURE_HEADER}Expecting 3 categories to be created from the populate_rango module; found {categories_len}.{FAILURE_FOOTER}")
        self.assertTrue('Python' in categories_strs, f"{FAILURE_HEADER}The category 'Python' was expected but not created by populate_rango.{FAILURE_FOOTER}")
        self.assertTrue('Django' in categories_strs, f"{FAILURE_HEADER}The category 'Django' was expected but not created by populate_rango.{FAILURE_FOOTER}")
        self.assertTrue('Other Frameworks' in categories_strs, f"{FAILURE_HEADER}The category 'Other Frameworks' was expected but not created by populate_rango.{FAILURE_FOOTER}")
    
    def test_pages(self):
        """
        Tests to check whether each page for the three different categories exists in the database.
        Calls the helper check_category_pages() method for this.
        """
        details = {'Python':
                       ['Official Python Tutorial', 'How to Think like a Computer Scientist', 'Learn Python in 10 Minutes'],
                   'Django':
                       ['Official Django Tutorial', 'Django Rocks', 'How to Tango with Django'],
                   'Other Frameworks':
                       ['Bottle', 'Flask']}
        
        for category in details:
            page_titles = details[category]
            self.check_category_pages(category, page_titles)
    
    def test_counts(self):
        """
        Tests whether each category's likes and views values are the values that are stated in the book.
        Pukes when a value doesn't match.
        """
        details = {'Python': {'views': 128, 'likes': 64},
                   'Django': {'views': 64, 'likes': 32},
                   'Other Frameworks': {'views': 32, 'likes': 16}}
        
        for category in details:
            values = details[category]
            category = Category.objects.get(name=category)
            self.assertEqual(category.views, values['views'], f"{FAILURE_HEADER}The number of views for the '{category}' category is incorrect (got {category.views}, expected {values['views']}, generated from populate_rango).{FAILURE_FOOTER}")
            self.assertEqual(category.likes, values['likes'], f"{FAILURE_HEADER}The number of likes for the '{category}' category is incorrect (got {category.likes}, expected {values['likes']}, generated from populate_rango).{FAILURE_FOOTER}")
    
    def check_category_pages(self, category, page_titles):
        """
        Performs a number of tests on the database regarding pages for a given category.
        Do all the included pages in the population script exist?
        The expected page list is passed as page_titles. The name of the category is passed as category.
        """
        category = Category.objects.get(name=category)
        pages = Page.objects.filter(category=category)
        pages_len = len(pages)
        page_titles_len = len(page_titles)
        
        self.assertEqual(pages_len, len(page_titles), f"{FAILURE_HEADER}Expected {page_titles_len} pages in the Python category produced by populate_rango; found {pages_len}.{FAILURE_FOOTER}")
        
        for title in page_titles:
            try:
                page = Page.objects.get(title=title)
            except Page.DoesNotExist:
                raise ValueError(f"{FAILURE_HEADER}The page '{title}' belonging to category '{category}' was not found in the database produced by populate_rango.{FAILURE_FOOTER}")
            
            self.assertEqual(page.category, category)