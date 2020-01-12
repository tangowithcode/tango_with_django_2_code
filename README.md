# Tango with Django 2 Codebase
This is a model solution for the *Tango with Django 2* book. Included are model solutions to all of the exercises included through each chapter. Screenshots that appear in the book were taken from a browser when executing this code.

If you notice something that doesn't work -- or you think there's a better way to solve something -- it would be great to hear from you. Add an [*issue*](https://github.com/maxwelld90/tango_with_django_2_code/issues) to this repository, and myself or Leif will get back to you!

Everything is working as of January 10, 2020.

David Maxwell (maxwelld90 at acm dot org)

**Note:** if you are a student looking for a quick way to complete your Rango assignment, you should be aware that there are a few little things in here which, if you blindly copy and paste, will demonstrate that you did just that. You have been warned. It's always better to spend your time actually learning about what everything does -- rather than blindly copying and pasting someone else's work, and flogging it off as your own. Have fun!

## How to Use this Repository
It's easy to use this repository. We've split our implementations of each chapter into a separate branch. If something needs to be changed later, we can simply update a specific branch -- rather than getting stuck and being unable to undo an old commit.

In the `master` branch, we keep our tests for the end of different chapters, along with this `README`, and the project's `requirements.txt` file. You can `checkout` the appropriate branch for the chapter you're interested in. Let's say you want to see what our sample solution looked like at the end of Chapter 5.

1. Make a copy of the repository on your device with `$ git clone https://github.com/maxwelld90/tango_with_django_2_code`.
2. Change into the directory that you've just created with `$ cd tango_with_django_2_code`.
3. Run the `checkout` command to switch your workspace to the correct branch with `$ git checkout remotes/origin/chapter5`.

You can view a full list of the available branches by issuing the command `git branch -a`. Substitute `chapter5` in Step 3 above with the name of the branch you want to view. Commits are made as we add each individual new feature -- not at the end of every chapter. This means each branch will have several commits for each chapter, so you can see how we build Rango up!

## End of Chapter Tests
We've also implemented some unit tests that can be run at the end of each chapter. We've currently got tests up to the end of Chapter 10. If there is demand for further chapters to be covered, let us know!

Test modules are located in the `master` branch, `progress_tests` directory. In order to run these tests, check out the Tango with Django book. Section 2.6 details exactly what you need to do. If you are stuck, reach out to us with a [*new issue*](https://github.com/maxwelld90/tango_with_django_2_code/issues).