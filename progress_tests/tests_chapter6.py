# 
# Tango with Django 2 Progress Tests
# By Leif Azzopardi and David Maxwell
# With assistance from Enzo Roiz (https://github.com/enzoroiz)
# 
# Chapter 6 -- Models, Templates and Views
# Last updated: October 15th, 2019
# Revising Author: David Maxwell
# 

#
# In order to run these tests, copy this module to your tango_with_django_project/rango/ directory.
# Once this is complete, run $ python manage.py test rango.tests_chapter6
# 
# The tests will then be run, and the output displayed -- do you pass them all?
# 
# Once you are done with the tests, delete the module. You don't need to put it in your Git repository!
#

import os
import re  # We use regular expressions to do more in-depth checks on generated HTML output from views.
import warnings
import importlib
from rango.models import Category, Page
from populate_rango import populate
from django.urls import reverse
from django.test import TestCase
from django.conf import settings
from django.db.models.query import QuerySet

FAILURE_HEADER = f"{os.linesep}{os.linesep}{os.linesep}================{os.linesep}TwD TEST FAILURE =({os.linesep}================{os.linesep}"
FAILURE_FOOTER = f"{os.linesep}"


class Chapter6PopulationScriptTest(TestCase):
    """
    A few simple tests to examine whether the population script has been updated to include the requested changes (views for pages).
    """
    def setUp(self):
        populate()
    
    def test_page_objects_have_views(self):
        """
        Checks the basic requirement that all pages must have a positive view count.
        """
        pages = Page.objects.filter()

        for page in pages:
            self.assertTrue(page.views > 0, f"{FAILURE_HEADER}The page '{page.title}' has a negative/zero view count. The exercises for Chapter 6 stated that all view values must be greater than zero. Update your population script, and try again.{FAILURE_FOOTER}")


class Chapter6IndexViewTests(TestCase):
    """
    A series of tests that examine the behaviour of the index view and its corresponding template.
    Tests to see if the context dictionary is correctly formed, and whether the response is correct, too.
    For these tests, we rely on the populate_rango module. We assume that this is now fully correct and working.
    If tests fail and you can't understand why, maybe it's worth checking out your population script!
    And yes, we assume that all exercises have been completed, too.
    """
    def setUp(self):
        populate()
        self.response = self.client.get(reverse('rango:index'))
        self.content = self.response.content.decode()
    
    def test_template_filename(self):
        """
        Still using a template?
        """
        self.assertTemplateUsed(self.response, 'rango/index.html', f"{FAILURE_HEADER}Are you using index.html for your index() view? Why not?!{FAILURE_FOOTER}")

    def test_index_context_dictionary(self):
        """
        Runs some assertions to check if the context dictionary has the correct key/value pairings.
        """
        expected_boldmessage = 'Crunchy, creamy, cookie, candy, cupcake!'
        expected_categories_order = list(Category.objects.order_by('-likes')[:5])
        expected_pages_order = list(Page.objects.order_by('-views')[:5])  # From the exercises section of Chapter 6 -- we cannot assume a set order, because the developer can set the number of views to whatever they wish.

        # Does the boldmessage still exist? A surprising number of people delete it here.
        self.assertTrue('boldmessage' in self.response.context, f"{FAILURE_HEADER}The 'boldmessage' variable couldn't be found in the context dictionary for the index() view. Did you delete it?{FAILURE_FOOTER}")
        self.assertEquals(expected_boldmessage, self.response.context['boldmessage'], f"{FAILURE_HEADER}Where did {expected_boldmessage} go in the index() view?{FAILURE_FOOTER}")

        # Check that categories exists in the context dictionary, that it references the correct objects, and the order is spot on.
        self.assertTrue('categories' in self.response.context, f"{FAILURE_HEADER}We couldn't find a 'categories' variable in the context dictionary within the index() view. Check the instructions in the book, and try again.{FAILURE_FOOTER}")
        self.assertEqual(type(self.response.context['categories']), QuerySet, f"{FAILURE_HEADER}The 'categories' variable in the context dictionary for the index() view didn't return a QuerySet object as expected.{FAILURE_FOOTER}")
        self.assertEqual(expected_categories_order, list(self.response.context['categories']), f"{FAILURE_HEADER}Incorrect categories/category order returned from the index() view's context dictionary -- expected {expected_categories_order}; got {list(self.response.context['categories'])}.{FAILURE_FOOTER}")

        # Repeat, but for the pages variable. Note that order cannot be verfified (no instructions in book to use certain values).
        self.assertTrue('pages' in self.response.context, f"{FAILURE_HEADER}We couldn't find a 'pages' variable in the index() view's context dictionary. Did you complete the Chapter 6 exercises?{FAILURE_FOOTER}")
        self.assertEqual(type(self.response.context['pages']), QuerySet, f"{FAILURE_HEADER}The 'pages' variable in the index() view's context dictionary doesn't return a QuerySet as expected.{FAILURE_FOOTER}")
        self.assertEqual(expected_pages_order, list(self.response.context['pages']), f"{FAILURE_HEADER}The 'pages' context dictionary variable for the index() view didn't return the QuerySet we were expectecting: got {list(self.response.context['pages'])}, expected {expected_pages_order}. Did you apply the correct ordering to the filtered results?{FAILURE_FOOTER}")
    
    def test_index_categories(self):
        """
        Checks the response generated by the index() view -- does it render the categories correctly?
        Regular expressions are used here (yikes) to try and be as fair as possible when checking the markup received from the developer's project.
        """
        category_li_entries_regex = [  # 0 = regex match, 1 = title of category, 2 = sanitised markup for error message
            [r'<li>(\s*|\n*)<a(\s+)href(\s*)=(\s*)("/rango/category/python/"|\'/rango/category/python/\')(\s*)>(\s*|\n*)Python(\s*|\n*)</a>(\s*|\n*)</li>', 'Python', '<li><a href="/rango/category/python/">Python</a></li>'],
            [r'<li>(\s*|\n*)<a(\s+)href(\s*)=(\s*)("/rango/category/django/"|\'/rango/category/django/\')(\s*)>(\s*|\n*)Django(\s*|\n*)</a>(\s*|\n*)</li>', 'Django', '<li><a href="/rango/category/django/">Django</a></li>'],
            [r'<li>(\s*|\n*)<a(\s+)href(\s*)=(\s*)("/rango/category/other-frameworks/"|\'/rango/category/other-frameworks/\')(\s*)>(\s*|\n*)Other Frameworks(\s*|\n*)</a>(\s*|\n*)</li>', 'Other Frameworks', '<li><a href="/rango/category/other-frameworks/">Other Frameworks</a></li>'],
        ]

        # Check for the presence of each entry.
        for entry in category_li_entries_regex:
            self.assertTrue(re.search(entry[0], self.content), f"{FAILURE_HEADER}We couldn't find the expected markup '{entry[2]}' (for the {entry[1]} category) in the response of your index() view. Check your template, and try again.{FAILURE_FOOTER}")
    
    def test_index_pages(self):
        """
        Checks the response generated by the index() view -- does it render the pages correctly?
        As you can set view values to whatever you like for pages (in the population script), we need to be a bit more clever working out what five of the pages should be displayed.
        """
        page_li_entries_regex = {
            'Official Python Tutorial': r'<li>(\s*|\n*)<a(\s+)href(\s*)=(\s*)("http://docs.python.org/3/tutorial/"|\'http://docs.python.org/3/tutorial/\')(\s*)>(\s*|\n*)Official Python Tutorial(\s*|\n*)</a>(\s*|\n*)</li>',
            'How to Think like a Computer Scientist': r'<li>(\s*|\n*)<a(\s+)href(\s*)=(\s*)("http://www.greenteapress.com/thinkpython/"|\'http://www.greenteapress.com/thinkpython/\')(\s*)>(\s*|\n*)How to Think like a Computer Scientist(\s*|\n*)</a>(\s*|\n*)</li>',
            'Learn Python in 10 Minutes': r'<li>(\s*|\n*)<a(\s+)href(\s*)=(\s*)("http://www.korokithakis.net/tutorials/python/"|\'http://www.korokithakis.net/tutorials/python/\')(\s*)>(\s*|\n*)Learn Python in 10 Minutes(\s*|\n*)</a>(\s*|\n*)</li>',
            'Official Django Tutorial': r'<li>(\s*|\n*)<a(\s+)href(\s*)=(\s*)("https://docs.djangoproject.com/en/2.1/intro/tutorial01/"|\'https://docs.djangoproject.com/en/2.1/intro/tutorial01/\')(\s*)>(\s*|\n*)Official Django Tutorial(\s*|\n*)</a>(\s*|\n*)</li>',
            'Django Rocks': r'<li>(\s*|\n*)<a(\s+)href(\s*)=(\s*)("http://www.djangorocks.com/"|\'http://www.djangorocks.com/\')(\s*)>(\s*|\n*)Django Rocks(\s*|\n*)</a>(\s*|\n*)</li>',
            'How to Tango with Django': r'<li>(\s*|\n*)<a(\s+)href(\s*)=(\s*)("http://www.tangowithdjango.com/"|\'http://www.tangowithdjango.com/\')(\s*)>(\s*|\n*)How to Tango with Django(\s*|\n*)</a>(\s*|\n*)</li>',
            'Bottle': r'<li>(\s*|\n*)<a(\s+)href(\s*)=(\s*)("http://bottlepy.org/docs/dev/"|\'http://bottlepy.org/docs/dev/\')(\s*)>(\s*|\n*)Bottle(\s*|\n*)</a>(\s*|\n*)</li>',
            'Flask': r'<li>(\s*|\n*)<a(\s+)href(\s*)=(\s*)("http://flask.pocoo.org"|\'http://flask.pocoo.org\')(\s*)>(\s*|\n*)Flask(\s*|\n*)</a>(\s*|\n*)</li>',
        }

        expected_pages_order = list(Page.objects.order_by('-views')[:5])
        expected_pages_li = []

        # Populate expected_pages_li, picking out the entry from page_li_entries_regex.
        for expected_page in expected_pages_order:
            expected_pages_li.append(page_li_entries_regex[expected_page.title])
        
        # Now we have the five entries regex to match, we can loop over and check each one exists.
        for expected_regex in expected_pages_li:
            print(self.content)
            self.assertTrue(re.search(expected_regex, self.content), f"{FAILURE_HEADER}Checks for the top five pages in the index() view's response failed. Check you are using the correct list of objects, the correct HTML markup, and try again. '{expected_regex}'{FAILURE_FOOTER}")
        
    def test_index_response_titles(self):
        """
        Checks whether the correct titles are used (including <h2> tags) for categories and pages.
        This is listed as an exercise at the end of Chapter 6.
        """
        expected_category_h2 = '<h2>Most Liked Categories</h2>'
        expected_page_h2 = '<h2>Most Viewed Pages</h2>'

        self.assertIn(expected_category_h2, self.content, f"{FAILURE_HEADER}We couldn't find the markup '{expected_category_h2}' in your index.html template. Check you completed the Chapter 6 exercises as requested, and try again.{FAILURE_FOOTER}")
        self.assertIn(expected_page_h2, self.content, f"{FAILURE_HEADER}We couldn't find the markup '{expected_page_h2}' in your index.html template. Check you completed the Chapter 6 exercises as requested, and try again.{FAILURE_FOOTER}")


class Chapter6NoItemsIndexViewTests(TestCase):
    """
    A few tests to complement the Chapter6IndexViewTests.
    This time, we purposefully do not prepopulate the sample database with data from populate_rango.
    As such, these tests examine whether the app being tested produces the correct output when no categories/pages are present.
    """
    def setUp(self):
        self.response = self.client.get(reverse('rango:index'))
        self.content = self.response.content.decode()

    def test_empty_index_context_dictionary(self):
        """
        Runs assertions on the context dictionary, ensuring the categories and pages variables exist, but return empty (zero-length) QuerySet objects.
        """
        self.assertTrue('categories' in self.response.context, f"{FAILURE_HEADER}The 'categories' variable does not exist in the context dictionary for index(). (Empty check){FAILURE_FOOTER}")
        self.assertEqual(type(self.response.context['categories']), QuerySet, f"{FAILURE_HEADER}The 'categories' variable in the context dictionary for index() does yield a QuerySet object. (Empty check){FAILURE_FOOTER}")
        self.assertEqual(len(self.response.context['categories']), 0, f"{FAILURE_HEADER}The 'categories' variable in the context dictionary for index() is not empty. (Empty check){FAILURE_FOOTER}")

        self.assertTrue('pages' in self.response.context, f"{FAILURE_HEADER}The 'pages' variable does not exist in the context dictionary for index(). (Empty check){FAILURE_FOOTER}")
        self.assertEqual(type(self.response.context['pages']), QuerySet, f"{FAILURE_HEADER}The 'pages' variable in the context dictionary for index() does yield a QuerySet object. (Empty check){FAILURE_FOOTER}")
        self.assertEqual(len(self.response.context['pages']), 0, f"{FAILURE_HEADER}The 'pages' variable in the context dictionary for index() is not empty. (Empty check){FAILURE_FOOTER}")
    
    def test_empty_index_response(self):
        """
        Checks to see whether the correct messages appear for no categories and pages.
        """
        self.assertIn('<strong>There are no categories present.</strong>', self.content, f"{FAILURE_HEADER}When no categories are present, we can't find the required '<strong>There are no categories present.</strong>' markup in your index() view's output.{FAILURE_FOOTER}")
        self.assertIn('<strong>There are no pages present.</strong>', self.content, f"{FAILURE_HEADER}When no categories are present, we can't find the required '<strong>There are no pages present.</strong>' markup in your index() view's output. Read the Chapter 6 exercises carefully.{FAILURE_FOOTER}")
    
    def test_sample_category(self):
        """
        Checks to see if the correct output is displayed when a sample Category object is added.
        For this test, we disregard the instance variable response.
        """
        Category.objects.get_or_create(name='Test Category')
        updated_response = self.client.get(reverse('rango:index')).content.decode()

        category_regex = r'<li>(\s*|\n*)<a(\s+)href(\s*)=(\s*)("/rango/category/test-category/"|\'/rango/category/test-category/\')(\s*)>(\s*|\n*)Test Category(\s*|\n*)</a>(\s*|\n*)</li>'
        self.assertTrue(re.search(category_regex, updated_response), f"{FAILURE_HEADER}When adding a test category, we couldn't find the markup for it in the output of the index() view. Check you have included all the code correctly for displaying categories.{FAILURE_FOOTER}")
        self.assertIn('<strong>There are no pages present.</strong>', self.content, f"{FAILURE_HEADER}When no categories are present, we can't find the required '<strong>There are no pages present.</strong>' markup in your index() view's output. Read the Chapter 6 exercises carefully.{FAILURE_FOOTER}")

class Chapter6CategoryViewTests(TestCase):
    """
    A series of tests for examining the show_category() view, looking at the context dictionary and rendered response.
    We use the 'Other Frameworks' category for these tests to check the slugs work correctly, too.
    """
    def setUp(self):
        populate()
        self.response = self.client.get(reverse('rango:show_category', kwargs={'category_name_slug': 'other-frameworks'}))
        self.content = self.response.content.decode()
    
    def test_template_filename(self):
        """
        Still using a template?
        """
        self.assertTemplateUsed(self.response, 'rango/category.html', f"{FAILURE_HEADER}The category.html template is not used for the show_category() view. The specification requires this.{FAILURE_FOOTER}")
    
    def test_slug_functionality(self):
        """
        Runs a simple test by changing the name of the "Other Frameworks" category to "Unscrupulous Nonsense".
        Checks to see whether the slug updates with the name change.
        """
        category = Category.objects.get_or_create(name='Other Frameworks')[0]
        category.name = "Unscrupulous Nonsense"
        category.save()

        self.assertEquals('unscrupulous-nonsense', category.slug, f"{FAILURE_HEADER}When changing the name of a category, the slug attribute was not updated (correctly) to reflect this change. Did you override the save() method in the Category model correctly?{FAILURE_FOOTER}")

    def test_context_dictionary(self):
        """
        Given the response, does the context dictionary match up with what is expected?
        Is the category object being passed correctly, and are the pages being filtered correctly?
        """
        other_frameworks_category = Category.objects.get_or_create(name='Other Frameworks')[0]
        page_list = list(Page.objects.filter(category=other_frameworks_category))
        
        self.assertTrue('category' in self.response.context, f"{FAILURE_HEADER}The 'category' variable in the context dictionary for the show_category() view was not found. Did you spell it correctly?{FAILURE_FOOTER}")
        self.assertTrue('pages' in self.response.context, f"{FAILURE_HEADER}The 'pages' variable in the context dictionary for the show_category() view was not found.{FAILURE_FOOTER}")

        self.assertEqual(self.response.context['category'], other_frameworks_category, f"{FAILURE_HEADER}The category returned in the context dictionary for the show_category() view did not match what was expected. We expect to see a Category object returned here (specifically the 'Other Frameworks' category, for our tests).{FAILURE_FOOTER}")
        self.assertEqual(list(self.response.context['pages']), page_list, f"{FAILURE_HEADER}The list of pages returned in the context dictionary of the show_category() view was not correct. Did you filter the pages correctly in your view?{FAILURE_FOOTER}")
    
    def test_response_markup(self):
        """
        Some simple tests to make sure the markup returned is on track. Specifically, we look at the title and list of pages returned.
        """
        expected_header = '<h1>Other Frameworks</h1>'
        bottle_markup = r'<li>(\s*|\n*)<a(\s+)href(\s*)=(\s*)("http://bottlepy.org/docs/dev/"|\'http://bottlepy.org/docs/dev/\')(\s*)>(\s*|\n*)Bottle(\s*|\n*)</a>(\s*|\n*)</li>'
        flask_markup = r'<li>(\s*|\n*)<a(\s+)href(\s*)=(\s*)("http://flask.pocoo.org"|\'http://flask.pocoo.org\')(\s*)>(\s*|\n*)Flask(\s*|\n*)</a>(\s*|\n*)</li>'

        self.assertIn(expected_header, self.content, f"{FAILURE_HEADER}The header tag '{expected_header}' was not found in the response for the show_category() view. Make sure the category.html template matches the specification.{FAILURE_FOOTER}")
        self.assertTrue(re.search(bottle_markup, self.content), f"{FAILURE_HEADER}Correctly formed <li> markup was not found for the pages to be displayed in the show_category() view. Make sure your category.html template is well-formed!{FAILURE_FOOTER}")
        self.assertTrue(re.search(flask_markup, self.content), f"{FAILURE_HEADER}Correctly formed <li> markup was not found for the pages to be displayed in the show_category() view. Make sure your category.html template is well-formed!{FAILURE_FOOTER}")

    def test_for_homepage_link(self):
        """
        Checks to see if a hyperlink to the homepage is present.
        We didn't enforce a strict label for the link; we are more interested here in correct syntax.
        """
        homepage_hyperlink_markup = r'<a(\s+)href="/rango/">(\w+)</a>'
        self.assertTrue(re.search(homepage_hyperlink_markup, self.content), f"{FAILURE_HEADER}We couldn't find a well-formed hyperlink to the Rango homepage in your category.html template. This is an exercise at the end of Chapter 6.{FAILURE_FOOTER}")

class Chapter6BadCategoryViewTests(TestCase):
    """
    A few tests to examine some edge cases where categories do not exist, for example.
    """
    def test_malformed_url(self):
        """
        Tests to see whether the URL patterns have been correctly entered; many students have fallen over at this one.
        Somehow.
        """
        response = self.client.get('/rango/category/')
        self.assertTrue(response.status_code == 404, f"{FAILURE_HEADER}The URL /rango/category/ should return a status of code of 404 (not found). Check to see whether you have correctly entered your urlpatterns.{FAILURE_FOOTER}")

    def test_nonexistent_category(self):
        """
        Attempts to lookup a category that does not exist in the database and checks the response.
        """
        response = self.client.get(reverse('rango:show_category', kwargs={'category_name_slug': 'nonexistent-category'}))
        lookup_string = 'The specified category does not exist.'
        self.assertIn(lookup_string, response.content.decode(), r"{FAILURE_HEADER}The expected message when attempting to access a non-existent category was not found. Check your category.html template.{FAILURE_FOOTER}")
    
    def test_empty_category(self):
        """
        Adds a Category without pages; checks to see what the response is.
        """
        category = Category.objects.get_or_create(name='Test Category')
        response = self.client.get(reverse('rango:show_category', kwargs={'category_name_slug': 'test-category'}))
        lookup_string = '<strong>No pages currently in category.</strong>'
        self.assertIn(lookup_string, response.content.decode(), r"{FAILURE_HEADER}The expected message when accessing a category without pages was not found. Check your category.html template.{FAILURE_FOOTER}")