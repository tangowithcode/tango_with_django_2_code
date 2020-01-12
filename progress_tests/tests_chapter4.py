# 
# Tango with Django 2 Progress Tests
# By Leif Azzopardi and David Maxwell
# With assistance from Enzo Roiz (https://github.com/enzoroiz)
# 
# Chapter 4 -- Templates and Media Files
# Last updated October 3rd, 2019
# Revising Author: David Maxwell
# 

#
# In order to run these tests, copy this module to your tango_with_django_project/rango/ directory.
# Once this is complete, run $ python manage.py test rango.tests_chapter4
# 
# The tests will then be run, and the output displayed -- do you pass them all?
# 
# Once you are done with the tests, delete the module. You don't need to put it in your Git repository!
#

import os
import importlib
from django.urls import reverse
from django.test import TestCase
from django.conf import settings

FAILURE_HEADER = f"{os.linesep}{os.linesep}{os.linesep}================{os.linesep}TwD TEST FAILURE =({os.linesep}================{os.linesep}"
FAILURE_FOOTER = f"{os.linesep}"

class Chapter4TemplatesStructureTests(TestCase):
    """
    Have you set templates, static files and media files up correctly, as per the book?
    """
    def setUp(self):
        self.project_base_dir = os.getcwd()
        self.templates_dir = os.path.join(self.project_base_dir, 'templates')
        self.rango_templates_dir = os.path.join(self.templates_dir, 'rango')
    
    def test_templates_directory_exists(self):
        """
        Does the templates/ directory exist?
        """
        directory_exists = os.path.isdir(self.templates_dir)
        self.assertTrue(directory_exists, f"{FAILURE_HEADER}Your project's templates directory does not exist.{FAILURE_FOOTER}")
    
    def test_rango_templates_directory_exists(self):
        """
        Does the templates/rango/ directory exist?
        """
        directory_exists = os.path.isdir(self.rango_templates_dir)
        self.assertTrue(directory_exists, f"{FAILURE_HEADER}The Rango templates directory does not exist.{FAILURE_FOOTER}")
    
    def test_template_dir_setting(self):
        """
        Does the TEMPLATE_DIR setting exist, and does it point to the right directory?
        """
        variable_exists = 'TEMPLATE_DIR' in dir(settings)
        self.assertTrue(variable_exists, f"{FAILURE_HEADER}Your settings.py module does not have the variable TEMPLATE_DIR defined!{FAILURE_FOOTER}")
        
        template_dir_value = os.path.normpath(settings.TEMPLATE_DIR)
        template_dir_computed = os.path.normpath(self.templates_dir)
        self.assertEqual(template_dir_value, template_dir_computed, f"{FAILURE_HEADER}Your TEMPLATE_DIR setting does not point to the expected path. Check your configuration, and try again.{FAILURE_FOOTER}")
    
    def test_template_lookup_path(self):
        """
        Does the TEMPLATE_DIR value appear within the lookup paths for templates?
        """
        lookup_list = settings.TEMPLATES[0]['DIRS']
        found_path = False
        
        for entry in lookup_list:
            entry_normalised = os.path.normpath(entry)
            
            if entry_normalised == os.path.normpath(settings.TEMPLATE_DIR):
                found_path = True
        
        self.assertTrue(found_path, f"{FAILURE_HEADER}Your project's templates directory is not listed in the TEMPLATES>DIRS lookup list. Check your settings.py module.{FAILURE_FOOTER}")
    
    def test_templates_exist(self):
        """
        Do the index.html and about.html templates exist in the correct place?
        """
        index_path = os.path.join(self.rango_templates_dir, 'index.html')
        about_path = os.path.join(self.rango_templates_dir, 'about.html')
        
        self.assertTrue(os.path.isfile(index_path), f"{FAILURE_HEADER}Your index.html template does not exist, or is in the wrong location.{FAILURE_FOOTER}")
        self.assertTrue(os.path.isfile(about_path), f"{FAILURE_HEADER}Your about.html template does not exist, or is in the wrong location.{FAILURE_FOOTER}")


class Chapter4IndexPageTests(TestCase):
    """
    A series of tests to ensure that the index page/view has been updated to work with templates.
    Image tests are in the Chapter4StaticMediaTests suite.
    """
    def setUp(self):
        self.response = self.client.get(reverse('rango:index'))
    
    def test_index_uses_template(self):
        """
        Checks whether the index view uses a template -- and the correct one!
        """
        self.assertTemplateUsed(self.response, 'rango/index.html', f"{FAILURE_HEADER}Your index() view does not use the expected index.html template.{FAILURE_FOOTER}")
    
    def test_index_uses_context_dictionary(self):
        """
        Tests whether the index view uses the context dictionary correctly.
        Crunchy, creamy cookie, anyone?
        """
        self.assertTrue('boldmessage' in self.response.context, f"{FAILURE_HEADER}In your index view, the context dictionary is not passing the boldmessage key. Check your context dictionary in the index() view, located in rango/views.py, and try again.{FAILURE_FOOTER}")
        
        message = self.response.context['boldmessage']
        expected = 'Crunchy, creamy, cookie, candy, cupcake!'
        self.assertEqual(message, expected,  f"{FAILURE_HEADER}The boldmessage being sent to the index.html template does not match what is expected. Check your index() view. Make sure you match up cases, and don't miss any punctuation! Even one missing character will cause the test to fail.{FAILURE_FOOTER}")
    
    def test_index_starts_with_doctype(self):
        """
        Is the <!DOCTYPE html> declaration on the first line of the index.html template?
        """
        self.assertTrue(self.response.content.decode().startswith('<!DOCTYPE html>'), f"{FAILURE_HEADER}Your index.html template does not start with <!DOCTYPE html> -- this is requirement of the HTML specification.{FAILURE_FOOTER}")
    
    def test_about_link_present(self):
        """
        Is the about hyperlink present and correct on the index.html template?
        """
        expected = "<a href=\"/rango/about/\">About</a><br />"
        self.assertTrue(expected in self.response.content.decode(), f"{FAILURE_HEADER}Your index.html template doesn't contain the /rango/about/ link -- or it is not correct. Make sure you have the linebreak in, too!{FAILURE_FOOTER}")
        

class Chapter4StaticMediaTests(TestCase):
    """
    A series of tests to check whether static files and media files have been setup and used correctly.
    Also tests for the two required files -- rango.jpg and cat.jpg.
    """
    def setUp(self):
        self.project_base_dir = os.getcwd()
        self.static_dir = os.path.join(self.project_base_dir, 'static')
        self.media_dir = os.path.join(self.project_base_dir, 'media')
    
    def test_does_static_directory_exist(self):
        """
        Tests whether the static directory exists in the correct location -- and the images subdirectory.
        Also checks for the presence of rango.jpg in the images subdirectory.
        """
        does_static_dir_exist = os.path.isdir(self.static_dir)
        does_images_static_dir_exist = os.path.isdir(os.path.join(self.static_dir, 'images'))
        does_rango_jpg_exist = os.path.isfile(os.path.join(self.static_dir, 'images', 'rango.jpg'))
        
        self.assertTrue(does_static_dir_exist, f"{FAILURE_HEADER}The static directory was not found in the expected location. Check the instructions in the book, and try again.{FAILURE_FOOTER}")
        self.assertTrue(does_images_static_dir_exist, f"{FAILURE_HEADER}The images subdirectory was not found in your static directory.{FAILURE_FOOTER}")
        self.assertTrue(does_rango_jpg_exist, f"{FAILURE_HEADER}We couldn't locate the rango.jpg image in the /static/images/ directory. If you think you've included the file, make sure to check the file extension. Sometimes, a JPG can have the extension .jpeg. Be careful! It must be .jpg for this test.{FAILURE_FOOTER}")
    
    def test_does_media_directory_exist(self):
        """
        Tests whether the media directory exists in the correct location.
        Also checks for the presence of cat.jpg.
        """
        does_media_dir_exist = os.path.isdir(self.media_dir)
        does_cat_jpg_exist = os.path.isfile(os.path.join(self.media_dir, 'cat.jpg'))
        
        self.assertTrue(does_media_dir_exist, f"{FAILURE_HEADER}We couldn't find the /media/ directory in the expected location. Make sure it is in your project directory (at the same level as the manage.py module).{FAILURE_FOOTER}")
        self.assertTrue(does_cat_jpg_exist, f"{FAILURE_HEADER}We couldn't find the cat.jpg image in /media/. Check the file extension; this is a common pitfall. It should .jpg. Not .png, .gif, or .jpeg!{FAILURE_FOOTER}")
    
    def test_static_and_media_configuration(self):
        """
        Performs a number of tests on your Django project's settings in relation to static files and user upload-able files..
        """
        static_dir_exists = 'STATIC_DIR' in dir(settings)
        self.assertTrue(static_dir_exists, f"{FAILURE_HEADER}Your settings.py module does not have the variable STATIC_DIR defined.{FAILURE_FOOTER}")
        
        expected_path = os.path.normpath(self.static_dir)
        static_path = os.path.normpath(settings.STATIC_DIR)
        self.assertEqual(expected_path, static_path, f"{FAILURE_HEADER}The value of STATIC_DIR does not equal the expected path. It should point to your project root, with 'static' appended to the end of that.{FAILURE_FOOTER}")
        
        staticfiles_dirs_exists = 'STATICFILES_DIRS' in dir(settings)
        self.assertTrue(staticfiles_dirs_exists, f"{FAILURE_HEADER}The required setting STATICFILES_DIRS is not present in your project's settings.py module. Check your settings carefully. So many students have mistyped this one.{FAILURE_FOOTER}")
        self.assertEqual([static_path], settings.STATICFILES_DIRS, f"{FAILURE_HEADER}Your STATICFILES_DIRS setting does not match what is expected. Check your implementation against the instructions provided.{FAILURE_FOOTER}")
        
        staticfiles_dirs_exists = 'STATIC_URL' in dir(settings)
        self.assertTrue(staticfiles_dirs_exists, f"{FAILURE_HEADER}The STATIC_URL variable has not been defined in settings.py.{FAILURE_FOOTER}")
        self.assertEqual('/static/', settings.STATIC_URL, f"{FAILURE_HEADER}STATIC_URL does not meet the expected value of /static/. Make sure you have a slash at the end!{FAILURE_FOOTER}")
        
        media_dir_exists = 'MEDIA_DIR' in dir(settings)
        self.assertTrue(media_dir_exists, f"{FAILURE_HEADER}The MEDIA_DIR variable in settings.py has not been defined.{FAILURE_FOOTER}")
        
        expected_path = os.path.normpath(self.media_dir)
        media_path = os.path.normpath(settings.MEDIA_DIR)
        self.assertEqual(expected_path, media_path, f"{FAILURE_HEADER}The MEDIA_DIR setting does not point to the correct path. Remember, it should have an absolute reference to tango_with_django_project/media/.{FAILURE_FOOTER}")
        
        media_root_exists = 'MEDIA_ROOT' in dir(settings)
        self.assertTrue(media_root_exists, f"{FAILURE_HEADER}The MEDIA_ROOT setting has not been defined.{FAILURE_FOOTER}")
        
        media_root_path = os.path.normpath(settings.MEDIA_ROOT)
        self.assertEqual(media_path, media_root_path, f"{FAILURE_HEADER}The value of MEDIA_ROOT does not equal the value of MEDIA_DIR.{FAILURE_FOOTER}")
        
        media_url_exists = 'MEDIA_URL' in dir(settings)
        self.assertTrue(media_url_exists, f"{FAILURE_HEADER}The setting MEDIA_URL has not been defined in settings.py.{FAILURE_FOOTER}")
        
        media_url_value = settings.MEDIA_URL
        self.assertEqual('/media/', media_url_value, f"{FAILURE_HEADER}Your value of the MEDIA_URL setting does not equal /media/. Check your settings!{FAILURE_FOOTER}")
    
    def test_context_processor_addition(self):
        """
        Checks to see whether the media context_processor has been added to your project's settings module.
        """
        context_processors_list = settings.TEMPLATES[0]['OPTIONS']['context_processors']
        self.assertTrue('django.template.context_processors.media' in context_processors_list, f"{FAILURE_HEADER}The 'django.template.context_processors.media' context processor was not included. Check your settings.py module.{FAILURE_FOOTER}")
        

class Chapter4ExerciseTests(TestCase):
    """
    A series of tests to ensure that the exercise listing at the end of Chapter 4 has been completed.
    """
    def setUp(self):
        self.project_base_dir = os.getcwd()
        self.template_dir = os.path.join(self.project_base_dir, 'templates', 'rango')
        self.about_response = self.client.get(reverse('rango:about'))
    
    def test_about_template_exists(self):
        """
        Tests the about template -- if it exists, and whether or not the about() view makes use of it.
        """
        template_exists = os.path.isfile(os.path.join(self.template_dir, 'about.html'))
        self.assertTrue(template_exists, f"{FAILURE_HEADER}The about.html template was not found in the expected location.{FAILURE_FOOTER}")
    
    def test_about_uses_template(self):
        """
        Checks whether the index view uses a template -- and the correct one!
        """
        self.assertTemplateUsed(self.about_response, 'rango/about.html', f"{FAILURE_HEADER}The about() view does not use the about.html template.{FAILURE_FOOTER}")
    
    def test_about_starts_with_doctype(self):
        """
        Is the <!DOCTYPE html> declaration on the first line of the about.html template?
        """
        self.assertTrue(self.about_response.content.decode().startswith('<!DOCTYPE html>'), f"{FAILURE_HEADER}Your about.html template does not start with <!DOCTYPE html> -- this is requirement of the HTML specification.{FAILURE_FOOTER}")
    
    def test_about_contains_required_text(self):
        """
        Checks to see whether the required text is on the rendered about page.
        """
        required = [
            "here is the about page.",
            "This tutorial has been put together by "
        ]
        
        for required_str in required:
            self.assertTrue(required_str in self.about_response.content.decode(), f"{FAILURE_HEADER}The expected string '{required_str}' was not found in the rendered /rango/about/ response.{FAILURE_FOOTER}")
    
    def test_about_contains_rango(self):
        """
        Checks whether the rendered about view has the picture of Rango.
        """
        required_str = f"<img src=\"{settings.STATIC_URL}images/rango.jpg\" alt=\"Picture of Rango\" />"
        self.assertTrue(required_str in self.about_response.content.decode(), f"{FAILURE_HEADER}The HTML markup to include the image of Rango in the about template was not found. It needs to match exactly what we are looking for. Check the book.{FAILURE_FOOTER}")
        
    def test_about_contains_cat(self):
        """
        Checks whether the rendered about view has the picture of a cat.
        """
        required_str = f"<img src=\"{settings.MEDIA_URL}cat.jpg\" alt=\"Picture of a Cat\" />"
        self.assertTrue(required_str in self.about_response.content.decode(), f"{FAILURE_HEADER}The HTML markup to include the image of a cat in the about template was not found. It needs to match exactly what we are looking for. Check the book.{FAILURE_FOOTER}")