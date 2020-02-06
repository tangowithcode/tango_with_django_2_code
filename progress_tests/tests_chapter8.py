# 
# Tango with Django 2 Progress Tests
# By Leif Azzopardi and David Maxwell
# With assistance from Gerardo A-C (https://github.com/gerac83) and Enzo Roiz (https://github.com/enzoroiz)
# 
# Chapter 8 -- Working with Templates
# Last updated: February 6th, 2020
# Revising Author: David Maxwell
# 

#
# In order to run these tests, copy this module to your tango_with_django_project/rango/ directory.
# Once this is complete, run $ python manage.py test rango.tests_chapter8
# 
# The tests will then be run, and the output displayed -- do you pass them all?
# 
# Once you are done with the tests, delete the module. You don't need to put it in your Git repository!
#

import os
import re
import inspect
from rango.models import Category, Page
from populate_rango import populate
from django.test import TestCase
from django.conf import settings
from django.urls import reverse, resolve
from django.forms import fields as django_fields

FAILURE_HEADER = f"{os.linesep}{os.linesep}{os.linesep}================{os.linesep}TwD TEST FAILURE =({os.linesep}================{os.linesep}"
FAILURE_FOOTER = f"{os.linesep}"


class Chapter8TemplateTests(TestCase):
    """
    I don't think it's possible to test every aspect of templates from this chapter without delving into some crazy string checking.
    So, instead, we can do some simple tests here: check that the base template exists, and that each page in the templates/rango directory has a title block.
    Based on the idea by Gerardo -- beautiful idea, cheers big man.
    """
    def get_template(self, path_to_template):
        """
        Helper function to return the string representation of a template file.
        """
        f = open(path_to_template, 'r')
        template_str = ""

        for line in f:
            template_str = f"{template_str}{line}"

        f.close()
        return template_str
    
    def test_base_template_exists(self):
        """
        Tests whether the base template exists.
        """
        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'rango', 'base.html')
        self.assertTrue(os.path.exists(template_base_path), f"{FAILURE_HEADER}We couldn't find the new base.html template that's required in the templates/rango directory. Did you create the template in the right place?{FAILURE_FOOTER}")
    
    def test_base_title_block(self):
        """
        Checks if Rango's new base template has the correct value for the base template.
        """
        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'rango', 'base.html')
        template_str = self.get_template(template_base_path)
        
        title_pattern = r'<title>(\s*|\n*)Rango(\s*|\n*)-(\s*|\n*){% block title_block %}(\s*|\n*)How to Tango with Django!(\s*|\n*){% (endblock|endblock title_block) %}(\s*|\n*)</title>'
        self.assertTrue(re.search(title_pattern, template_str), f"{FAILURE_HEADER}When searching the contents of base.html, we couldn't find the expected title block. We're looking for '<title>Rango - {{% block title_block %}}How to Tango with Django!{{% endblock %}}</title>' with any combination of whitespace.{FAILURE_FOOTER}")
    
    def test_template_usage(self):
        """
        Check that each view uses the correct template.
        """
        populate()
        
        urls = [reverse('rango:about'),
                reverse('rango:add_category'),
                reverse('rango:add_page', kwargs={'category_name_slug': 'python'}),
                reverse('rango:show_category', kwargs={'category_name_slug': 'python'}),
                reverse('rango:index'),]

        templates = ['rango/about.html',
                     'rango/add_category.html',
                     'rango/add_page.html',
                     'rango/category.html',
                     'rango/index.html',]
        
        for url, template in zip(urls, templates):
            response = self.client.get(url)
            self.assertTemplateUsed(response, template)

    def test_title_blocks(self):
        """
        Tests whether the title blocks in each page are the expected values.
        This is probably the easiest way to check for blocks.
        """
        populate()
        template_base_path = os.path.join(settings.TEMPLATE_DIR, 'rango')
        
        mappings = {
            reverse('rango:about'): {'full_title_pattern': r'<title>(\s*|\n*)Rango(\s*|\n*)-(\s*|\n*)About Rango(\s*|\n*)</title>',
                                     'block_title_pattern': r'{% block title_block %}(\s*|\n*)About Rango(\s*|\n*){% (endblock|endblock title_block) %}',
                                     'template_filename': 'about.html'},
            reverse('rango:add_category'): {'full_title_pattern': r'<title>(\s*|\n*)Rango(\s*|\n*)-(\s*|\n*)Add a Category(\s*|\n*)</title>',
                                            'block_title_pattern': r'{% block title_block %}(\s*|\n*)Add a Category(\s*|\n*){% (endblock|endblock title_block) %}',
                                            'template_filename': 'add_category.html'},
            reverse('rango:add_page', kwargs={'category_name_slug': 'python'}): {'full_title_pattern': r'<title>(\s*|\n*)Rango(\s*|\n*)-(\s*|\n*)Add a Page(\s*|\n*)</title>',
                                                                                 'block_title_pattern': r'{% block title_block %}(\s*|\n*)Add a Page(\s*|\n*){% (endblock|endblock title_block) %}',
                                                                                 'template_filename': 'add_page.html'},
            reverse('rango:show_category', kwargs={'category_name_slug': 'python'}): {'full_title_pattern': r'<title>(\s*|\n*)Rango(\s*|\n*)-(\s*|\n*)Python(\s*|\n*)</title>',
                                                                                      'block_title_pattern': r'{% block title_block %}(\s*|\n*){% if category %}(\s*|\n*){{ category.name }}(\s*|\n*){% else %}(\s*|\n*)Unknown Category(\s*|\n*){% endif %}(\s*|\n*){% (endblock|endblock title_block) %}',
                                                                                      'template_filename': 'category.html'},
            reverse('rango:index'): {'full_title_pattern': r'<title>(\s*|\n*)Rango(\s*|\n*)-(\s*|\n*)Homepage(\s*|\n*)</title>',
                                     'block_title_pattern': r'{% block title_block %}(\s*|\n*)Homepage(\s*|\n*){% (endblock|endblock title_block) %}',
                                     'template_filename': 'index.html'},
        }

        for url in mappings.keys():
            full_title_pattern = mappings[url]['full_title_pattern']
            template_filename = mappings[url]['template_filename']
            block_title_pattern = mappings[url]['block_title_pattern']

            request = self.client.get(url)
            content = request.content.decode('utf-8')
            template_str = self.get_template(os.path.join(template_base_path, template_filename))

            self.assertTrue(re.search(full_title_pattern, content), f"{FAILURE_HEADER}When looking at the response of GET '{url}', we couldn't find the correct <title> block. Check the exercises on Chapter 8 for the expected title.{FAILURE_FOOTER}")
            self.assertTrue(re.search(block_title_pattern, template_str), f"{FAILURE_HEADER}When looking at the source of template '{template_filename}', we couldn't find the correct template block. Are you using template inheritence correctly, and did you spell the title as in the book? Check the exercises on Chapter 8 for the expected title.{FAILURE_FOOTER}")
    
    def test_for_links_in_base(self):
        """
        There should be three hyperlinks in base.html, as per the specification of the book.
        Check for their presence, along with correct use of URL lookups.
        """
        template_str = self.get_template(os.path.join(settings.TEMPLATE_DIR, 'rango', 'base.html'))

        look_for = [
            '<a href="{% url \'rango:add_category\' %}">Add a New Category</a>',
            '<a href="{% url \'rango:about\' %}">About</a>',
            '<a href="{% url \'rango:index\' %}">Index</a>',
        ]
        
        for lookup in look_for:
            self.assertTrue(lookup in template_str, f"{FAILURE_HEADER}In base.html, we couldn't find the hyperlink '{lookup}'. Check your markup in base.html is correct and as written in the book.{FAILURE_FOOTER}")