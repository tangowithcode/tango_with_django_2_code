# 
# Tango with Django 2 Progress Tests
# By Leif Azzopardi and David Maxwell
# With assistance from Enzo Roiz (https://github.com/enzoroiz) and Gerardo A-C (https://github.com/gerac83)
# 
# Chapter 7 -- Forms
# Last updated: January 7th, 2020
# Revising Author: David Maxwell
# 

#
# In order to run these tests, copy this module to your tango_with_django_project/rango/ directory.
# Once this is complete, run $ python manage.py test rango.tests_chapter7
# 
# The tests will then be run, and the output displayed -- do you pass them all?
# 
# Once you are done with the tests, delete the module. You don't need to put it in your Git repository!
#

import os
import inspect
from rango.models import Category, Page
from populate_rango import populate
from django.test import TestCase
from django.urls import reverse, resolve
from django.forms import fields as django_fields

FAILURE_HEADER = f"{os.linesep}{os.linesep}{os.linesep}================{os.linesep}TwD TEST FAILURE =({os.linesep}================{os.linesep}"
FAILURE_FOOTER = f"{os.linesep}"


class Chapter7FormClassTests(TestCase):
    """
    Do the Form classes exist, and do they contain the correct instance variables?
    """
    def test_module_exists(self):
        """
        Tests that the forms.py module exists in the expected location.
        """
        project_path = os.getcwd()
        rango_app_path = os.path.join(project_path, 'rango')
        forms_module_path = os.path.join(rango_app_path, 'forms.py')

        self.assertTrue(os.path.exists(forms_module_path), f"{FAILURE_HEADER}We couldn't find Rango's new forms.py module. This is required to be created at the top of Section 7.2. This module should be storing your two form classes.{FAILURE_FOOTER}")
    
    def test_category_form_class(self):
        """
        Does the CategoryForm implementation exist, and does it contain the correct instance variables?
        """
        # Check that we can import CategoryForm.
        import rango.forms
        self.assertTrue('CategoryForm' in dir(rango.forms), f"{FAILURE_HEADER}The class CategoryForm could not be found in Rango's forms.py module. Check you have created this class in the correct location, and try again.{FAILURE_FOOTER}")

        from rango.forms import CategoryForm
        category_form = CategoryForm()

        # Do you correctly link Category to CategoryForm?
        self.assertEqual(type(category_form.__dict__['instance']), Category, f"{FAILURE_HEADER}The CategoryForm does not link to the Category model. Have a look in the CategoryForm's nested Meta class for the model attribute.{FAILURE_FOOTER}")

        # Now check that all the required fields are present, and of the correct form field type.
        fields = category_form.fields

        expected_fields = {
            'name': django_fields.CharField,
            'views': django_fields.IntegerField,
            'likes': django_fields.IntegerField,
            'slug': django_fields.CharField,
        }

        for expected_field_name in expected_fields:
            expected_field = expected_fields[expected_field_name]

            self.assertTrue(expected_field_name in fields.keys(), f"{FAILURE_HEADER}The field '{expected_field_name}' was not found in your CategoryForm implementation. Check you have all required fields, and try again.{FAILURE_FOOTER}")
            self.assertEqual(expected_field, type(fields[expected_field_name]), f"{FAILURE_HEADER}The field '{expected_field_name}' in CategoryForm was not of the expected type '{type(fields[expected_field_name])}'.{FAILURE_FOOTER}")

class Chapter7CategoryFormAncillaryTests(TestCase):
    """
    Performs checks to see if all the additional requirements in Chapter 7 for adding a CategoryForm have been implemented correctly.
    Checks URL mappings and server output.
    """
    def test_add_category_url_mapping(self):
        """
        Tests whether the URL mapping for adding a category is resolvable.
        """
        try:
            resolved_name = resolve('/rango/add_category/').view_name
        except:
            resolved_name = ''
        
        self.assertEqual(resolved_name, 'rango:add_category', f"{FAILURE_HEADER}The lookup of URL '/rango/add_category/' didn't return a mapping name of 'rango:add_category'. Check you have the correct URL mapping for adding a category, and try again.{FAILURE_FOOTER}")
    
    def test_index_link_added(self):
        """
        Checks whether a link has been added as required on the index page, taking a user to the add category page.
        """
        response = self.client.get(reverse('rango:index'))
        content = response.content.decode()

        self.assertTrue('<a href="/rango/add_category/">Add a New Category</a><br />' in content)

    def test_add_category_template(self):
        """
        Checks whether a template was used for the add_category() view.
        """
        response = self.client.get(reverse('rango:add_category'))
        self.assertTemplateUsed(response, 'rango/add_category.html', f"{FAILURE_HEADER}The add_category.html template is not used for the add_category() view. The specification requires this.{FAILURE_FOOTER}")

    def test_add_category_form_response(self):
        """
        Checks the response from the initial add category response (i.e. check the page/form is correct).
        """
        response = self.client.get(reverse('rango:add_category'))
        context = response.context
        content = response.content.decode()

        self.assertTrue('form' in context)

        self.assertTrue('<h1>Add a Category</h1>' in content, f"{FAILURE_HEADER}Couldn't find 'Add a Category' header in the add_category() response. Check the template add_category.html.{FAILURE_FOOTER}")
        self.assertTrue('name="name"' in content, f"{FAILURE_HEADER}We couldn't find the form field 'name' in the rendered add_category() response. Check that your form is being created correctly.{FAILURE_FOOTER}")
        self.assertTrue('<input type="submit" name="submit" value="Create Category" />' in content, f"{FAILURE_HEADER}Couldn't find the button for 'Create Category' in the add_category() response. Check the template add_category.html.{FAILURE_FOOTER}")
        self.assertTrue('action="/rango/add_category/"' in content, f"{FAILURE_HEADER}Couldn't find the correct action URL for the form in add_category.html. Check that the correct URL is provided!{FAILURE_FOOTER}")
    
    def test_add_category_functionality(self):
        """
        Adds a category using the form, submits the request, and checks that the new category then exists.
        """
        self.client.post(reverse('rango:add_category'),
                         {'name': 'Erlang', 'views': 0, 'likes': 0})
        
        categories = Category.objects.filter(name='Erlang')
        self.assertEqual(len(categories), 1, f"{FAILURE_HEADER}When adding a new category, it does not appear in the list of categories after being created. Check your add_category() view as the start of a debugging point.{FAILURE_FOOTER}")
    
    def test_category_exists(self):
        """
        Attempts to add a category that already exists.
        """
        populate()

        response = self.client.post(reverse('rango:add_category'),
                                            {'name': 'Python', 'views': 0, 'likes': 0})
        
        self.assertTrue('Category with this Name already exists.' in response.content.decode(), f"{FAILURE_HEADER}When attempting to add a category that already exists, we didn't get the error message we were expecting. Please check your add_category() view and add_category.html template.{FAILURE_FOOTER}")

class Chapter7PageFormClassTests(TestCase):
    """
    Checks whether the PageForm class has been implemented correctly.
    """
    def test_page_form_class(self):
        """
        Does the PageForm implementation exist, and does it contain the correct instance variables?
        """
        # Check that we can import PageForm.
        import rango.forms
        self.assertTrue('PageForm' in dir(rango.forms), f"{FAILURE_HEADER}The class PageForm could not be found in Rango's forms.py module. Check you have created this class in the correct location, and try again.{FAILURE_FOOTER}")

        from rango.forms import PageForm
        page_form = PageForm()

        # Do you correctly link Page to PageForm?
        self.assertEqual(type(page_form.__dict__['instance']), Page, f"{FAILURE_HEADER}The PageForm does not link to the Page model. Have a look in the PageForm's nested Meta class for the model attribute.{FAILURE_FOOTER}")

        # Now check that all the required fields are present, and of the correct form field type.
        fields = page_form.fields

        expected_fields = {
            'title': django_fields.CharField,
            'url': django_fields.URLField,
            'views': django_fields.IntegerField,
        }

        for expected_field_name in expected_fields:
            expected_field = expected_fields[expected_field_name]

            self.assertTrue(expected_field_name in fields.keys(), f"{FAILURE_HEADER}The field '{expected_field_name}' was not found in your PageForm implementation. Check you have all required fields, and try again.{FAILURE_FOOTER}")
            self.assertEqual(expected_field, type(fields[expected_field_name]), f"{FAILURE_HEADER}The field '{expected_field_name}' in PageForm was not of the expected type '{type(fields[expected_field_name])}'.{FAILURE_FOOTER}")
    
class Chapter7PageFormAncillaryTests(TestCase):
    """
    Performs a series of tests to check the response of the server under different conditions when adding pages.
    """
    def test_add_page_url_mapping(self):
        """
        Tests whether the URL mapping for adding a page is resolvable.
        """
        try:
            resolved_url = reverse('rango:add_page', kwargs={'category_name_slug': 'python'})
        except:
            resolved_url = ''
        
        self.assertEqual(resolved_url, '/rango/category/python/add_page/', f"{FAILURE_HEADER}The lookup of URL name 'rango:add_page' didn't return a URL matching '/rango/category/python/add_page/', when using category 'python'. Check you have the correct mappings and URL parameters, and try again.{FAILURE_FOOTER}")
    
    def test_add_page_template(self):
        """
        Checks whether a template was used for the add_page() view.
        """
        populate()
        response = self.client.get(reverse('rango:add_page', kwargs={'category_name_slug': 'python'}))
        self.assertTemplateUsed(response, 'rango/add_page.html', f"{FAILURE_HEADER}The add_page.html template is not used for the add_page() view. The specification requires this.{FAILURE_FOOTER}")
    
    def test_add_page_form_response(self):
        """
        Checks whether the template rendering add_page() contains a form, and whether it points to the add_page view.
        """
        populate()
        response = self.client.get(reverse('rango:add_page', kwargs={'category_name_slug': 'django'}))
        context = response.context
        content = response.content.decode()

        self.assertTrue('<form' in content, f"{FAILURE_HEADER}We couldn't find a <form> element in the response for adding a page.{FAILURE_FOOTER}")
        self.assertTrue('action="/rango/category/django/add_page/"' in content, f"{FAILURE_HEADER}We couldn't find the correct action URL for adding a page in your add_page.html template. We expected to see 'action=\"/rango/django/add_page/\"' when adding a page to the 'python' category.{FAILURE_FOOTER}")
    
    def test_add_page_bad_category(self):
        """
        Tests whether the response for adding a page when specifying a non-existent category is per the specification.
        """
        response = self.client.get(reverse('rango:add_page', kwargs={'category_name_slug': 'non-existent'}))

        self.assertEquals(response.status_code, 302, f"{FAILURE_HEADER}When attempting to add a new page to a category that doesn't exist, we weren't redirected. We were expecting a redirect -- check you add_page() view.{FAILURE_FOOTER}")
        self.assertEquals(response.url, '/rango/', f"{FAILURE_HEADER}When attempting to add a new page to a category that doesn't exist, we were not redirected to the Rango homepage. Check your add_page() view, and try again.{FAILURE_FOOTER}")

    def test_add_page_functionality(self):
        """
        Given a category and a new page, tests whether the functionality implemented works as expected.
        """
        populate()

        response = self.client.post(reverse('rango:add_page', kwargs={'category_name_slug': 'python'}),
                                            {'title': 'New webpage', 'url': 'www.google.com', 'views': 0})

        python_pages = Page.objects.filter(title='New webpage')
        self.assertEqual(len(python_pages), 1, f"{FAILURE_HEADER}When adding a new page to a category with the add_page form, the new Page object that we were expecting wasn't created. Check your add_page() view for mistakes, and try again. You need to call .save() on the page you create!{FAILURE_FOOTER}")

        page = python_pages[0]
        self.assertEqual(page.url, 'http://www.google.com', f"{FAILURE_HEADER}We created a new page with a URL of 'www.google.com'. The saved object is expected to have a URL of 'http://www.google.com'. Is your clean() method in PageForm working correctly?{FAILURE_FOOTER}")
        self.assertEqual(page.title, 'New webpage', f"{FAILURE_HEADER}The new page we created didn't have the title we specified in the add_page form. Are you missing something in your PageForm implementation?{FAILURE_FOOTER}")