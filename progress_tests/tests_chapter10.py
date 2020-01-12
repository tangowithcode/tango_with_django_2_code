# 
# Tango with Django 2 Progress Tests
# By Leif Azzopardi and David Maxwell
# With assistance from Gerardo A-C (https://github.com/gerac83) and Enzo Roiz (https://github.com/enzoroiz)
# 
# Chapter 10 -- Cookies and Sessions
# Last updated: January 10th, 2020
# Revising Author: David Maxwell
# 

#
# In order to run these tests, copy this module to your tango_with_django_project/rango/ directory.
# Once this is complete, run $ python manage.py test rango.tests_chapter10
# 
# The tests will then be run, and the output displayed -- do you pass them all?
# 
# Once you are done with the tests, delete the module. You don't need to put it in your Git repository!
#

import os
import re
import rango.models
from rango import forms
from populate_rango import populate
from datetime import datetime, timedelta
from django.db import models
from django.test import TestCase
from django.conf import settings
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.forms import fields as django_fields

FAILURE_HEADER = f"{os.linesep}{os.linesep}{os.linesep}================{os.linesep}TwD TEST FAILURE =({os.linesep}================{os.linesep}"
FAILURE_FOOTER = f"{os.linesep}"

f"{FAILURE_HEADER} {FAILURE_FOOTER}"


class Chapter10ConfigurationTests(TestCase):
    """
    Tests the configuration of the Django project -- can cookies be used, at least on the server-side?
    """
    def test_middleware_present(self):
        """
        Tests to see if the SessionMiddleware is present in the project configuration.
        """
        self.assertTrue('django.contrib.sessions.middleware.SessionMiddleware' in settings.MIDDLEWARE)
    
    def test_session_app_present(self):
        """
        Tests to see if the sessions app is present.
        """
        self.assertTrue('django.contrib.sessions' in settings.INSTALLED_APPS)


class Chapter10SessionPersistenceTests(TestCase):
    """
    Tests to see if session data is persisted by counting up the number of accesses, and examining last time since access.
    """
    def test_visits_counter(self):
        """
        Tests the visits counter.
        Artificially tweaks the last_visit variable to force a counter increment.
        """
        for i in range(0, 10):
            response = self.client.get(reverse('rango:index'))
            session = self.client.session

            self.assertIsNotNone(session['visits'])
            self.assertIsNotNone(session['last_visit'])

            # Get the last visit, and subtract one day.
            # Forces an increment of the counter.
            last_visit = datetime.now() - timedelta(days=1)

            session['last_visit'] = str(last_visit)
            session.save()

            self.assertEquals(session['visits'], i+1)

class Chapter10ViewTests(TestCase):
    """
    Tests the views manipulated for Chapter 10.
    Specifically, we look for changes to the index and about views.
    """
    def test_index_view(self):
        """
        Checks that the index view doesn't contain any presentational logic for showing the number of visits.
        This should be removed in the final exercise.
        """
        response = self.client.get(reverse('rango:index'))
        content = response.content.decode()

        self.assertTrue('visits:' not in content.lower(), f"{FAILURE_HEADER}The index.html template should not contain any logic for displaying the number of views. Did you complete the exercises?{FAILURE_FOOTER}")
    
    def test_about_view(self):
        """
        Checks to see if the about view has the correct presentation for showing the number of visits.
        """
        response = self.client.get(reverse('rango:index'))  # Call this first to ensure the counter is set.
        response = self.client.get(reverse('rango:about'))
        content = response.content.decode()

        self.assertTrue('Visits: 1' in content, f"{FAILURE_HEADER}In your about.html template, please check that you have the correct output for displaying the number of visits. Capital letters matter. Otherwise, check your about() view and the cookie handling logic.{FAILURE_FOOTER}")
    
    def test_visits_passed_via_context(self):
        """
        Checks that the context dictionary contains the correct values.
        """
        response = self.client.get(reverse('rango:index'))  # Set the counter!
        self.assertNotIn('visits', response.context, f"{FAILURE_HEADER}The 'visits' variable appeared in the context dictionary passed by index(). This should be removed, as per the exercises for Chapter 10.{FAILURE_FOOTER}")

        response = self.client.get(reverse('rango:about'))
        self.assertIn('visits', response.context, f"{FAILURE_HEADER}We couldn't find the 'visits' variable in the context dictionary for about(). Check your about() implementation.{FAILURE_FOOTER}")