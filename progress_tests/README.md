# Tango with Django 2 Progress Tests
We have included a number of different tests for you to run against your implementation of Rango as you progress through *Tango with Django 2*. You can find them all in this repository.

Files are named `tests_chapterX.py`, where you replace `X` with the chapter number you're looking to test.

## Running the Tests
In order to run the tests for, say, Chapter 3, this is what you need to do.

1. Make sure your `rangoenv` virtual environment is active.
2. Download the `tests_chapter3.py` module from this directory. You can do this by either cloning this repository to your disk, or downloading each file from the GitHub web interface.
    * To do the latter, click the `tests_chapter3.py` module, then click the `Raw` button. Save this page to your disk.
3. Place the `tests_chapter3.py` module inside your project's `rango` directory.
4. In your terminal or Command Prompt, enter the command `$ python manage.py test rango.tests_chapter3.py`. This should execute the tests.

If you see `OK` at the end of the output, everything passed. Congratulations! If you don't see `OK`, something failed -- look through the output of the tests to see what test failed, and why. Sometimes, you might have missed something which causes an exception to be raised before the test can be carried out. In instances like this, you'll need to look at what is expected, and go back and fill it in.

**Note that we assume you have completed all of the exercises for the chapter you are testing!**

## Important Notes
**You should also be aware that it is important that you need to test your codebase against the correct test module for the stage you are at.** Earlier tests will begin to fail as you develop the Rango app. For example, if you complete up to the end of Chapter 10 but run the tests for Chapter 3 over your codebase, *tests will fail.* This is because as you progress through the book, you will chop and change code, meaning that tests that would have passed at the end of Chapter 3 now won't pass!

You should also make sure that you delete the test module you copied in when you are finished running those tests. Make sure your repository does not fill up with `test_chapterX.py` modules!

Last updated: January 12, 2020 (David Maxwell)
