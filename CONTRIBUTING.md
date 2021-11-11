Lux is a project undergoing active development. If you are interested in contributing to Lux, the open tasks on [GitHub issues](https://github.com/lux-org/lux/issues), esp. issues labelled with the tag [`easy`](https://github.com/lux-org/lux/labels/easy), are good places for newcomers to contribute. This guide contains information on the workflow for contributing to the Lux codebase. For more information on the Lux architecture, see this [documentation page](https://lux-api.readthedocs.io/en/latest/source/advanced/architecture.html). 


# Setting up Build and Installation Process

To setup Lux manually for development purposes, you should [fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) the Github repo and clone the forked version.

```bash
git clone https://github.com/USERNAME/lux.git
```

You can install Lux by building from the source code in your fork directly:

```bash
cd lux/
pip install --user -r requirements.txt
pip install --user -r requirements-dev.txt
python setup.py install
```

When you make a change to the source code in the `lux/` folder, you can rebuild by doing this: 

```bash
python setup.py install
```

# Debugging and Testing with Jupyter

It is often useful to test your code changes via Jupyter notebook. To debug your code changes, you can import a "local" copy of Lux without having to rebuild the changes everytime.

For example, you can have a test notebook `test.ipynb` that imports. Note that when you do `import lux` at this path, it imports the local lux/ module instead of your global installation (either system-wide or in your virtual environment).

```
lux/
    - test.ipynb
    - lux/
```

# Code Formatting
In order to keep our codebase clean and readible, we are using PEP8 guidelines. To help us maintain and check code style currently we use the following `pre-commit` hooks to automatically format the code on every commit and enforce its formatting on CI:

* [black](https://github.com/psf/black)

Precommit hooks are installed for you as part of [requirements-dev.txt](https://github.com/lux-org/lux/blob/master/requirements-dev.txt). To ensure precommit hooks run on every commit, run the install command:

```bash
pre-commit install
```

To manually run precommit hooks use:

```bash
pre-commit run --all-files
``` 

# Running the Test Suite

There is a suite of test files for ensuring that Lux is working correctly. These tests are triggered to run via [Travis CI](https://travis-ci.com/lux-org/lux) whenever there is a commit made to the lux repository. You can run them locally to make sure that your changes are working and do not break any of the existing tests.

To run all the tests, including checking for code formatting, run:

```
make test
```

To run a single test file, run:

```
python -m pytest tests/<test_file_name>.py
```
# Commit Guidelines

## Commit Message formatting

To ensure that all commit messages in the master branch follow a specific format, we
enforce that all commit messages must follow the following format:

.. code-block:: bash

    FEAT-#9999: Add new functionality for feature XYZ

The ``FEAT`` component represents the type of commit. This component of the commit
message can be one of the following:

* FEAT: A new feature that is added
* DOCS: Documentation improvements or updates
* FIX: A bugfix contribution
* REFACTOR: Moving or removing code without change in functionality
* TEST: Test updates or improvements

The ``#9999`` component of the commit message should be the issue number in the 
GitHub issue tracker: https://github.com/lux-org/lux/issues. This is important
because it links commits to their issues.

The commit message should follow a colon (:) and be descriptive and succinct.

## Sign-off Procedure

To keep a clear track of who did what, we use a `sign-off` procedure on patches or pull requests that are being sent. This signed-off process is the same procedures used by many open-source projects, including the [Linux kernel](https://www.kernel.org/doc/html/v4.17/process/submitting-patches.html). The sign-off is a simple line at the end of the explanation
for the patch, which certifies that you wrote it or otherwise have the right to pass it
on as an open-source patch. If you can certify the below:

```
CERTIFICATE OF ORIGIN V 1.1
By making a contribution to this project, I certify that:

1.) The contribution was created in whole or in part by me and I have the right to
submit it under the open source license indicated in the file; or
2.) The contribution is based upon previous work that, to the best of my knowledge, is
covered under an appropriate open source license and I have the right under that license
to submit that work with modifications, whether created in whole or in part by me, under
the same open source license (unless I am permitted to submit under a different
license), as indicated in the file; or
3.) The contribution was provided directly to me by some other person who certified (a),
(b) or (c) and I have not modified it.
4.) I understand and agree that this project and the contribution are public and that a
record of the contribution (including all personal information I submit with it,
including my sign-off) is maintained indefinitely and may be redistributed consistent
with this project or the open source license(s) involved.
```

then you can add the signoff line at the end of your commit as follows: 

```bash
This is my commit message

Signed-off-by: Awesome Developer <developer@example.org>
```

Code without a proper signoff cannot be merged into the
master branch. You must use your real name and working email in the commit signature.

The signoff line can either be manually added to your commit body, or you can add either ``-s``
or ``--signoff`` to your usual ``git commit`` commands:

```bash
git commit --signoff
git commit -s
```

This will use your default git configuration which is found in `.git/config`. To change
this, you can use the following commands:

```bash
git config --global user.name "Awesome Developer"
git config --global user.email "awesome.developer@example.org"
```

If you have authored a commit that is missing the signed-off-by line, you can amend your
commits and push them to GitHub.

```bash
git commit --amend --signoff
```

If you've pushed your changes to GitHub already you'll need to force push your branch
after this with ``git push -f``.

# Submitting a Pull Request

You can commit your code and push to your forked repo. Once all of your local changes have been tested and formatted, you are ready to submit a PR. For Lux, we use the "Squash and Merge" strategy to merge in PR, which means that even if you make a lot of small commits in your PR, they will all get squashed into a single commit associated with the PR. Please make sure that comments and unnecessary file changes are not committed as part of the PR by looking at the "File Changes" diff view on the pull request page.
    
Once the pull request is submitted, the maintainer will get notified and review your pull request. They may ask for additional changes or comment on the PR. You can always make updates to your pull request after submitting it.

# Building Documentation

Lux uses [Sphinx](https://www.sphinx-doc.org/en/master/) to generate the documentations, which contains both the docstring and the written documentation in the `doc/` folder. To build the documentation in HTML, you can run this command locally in the `doc/` folder:

```bash
make html
```

This generates all the HTML documentation files in `doc/_build/html/`. The configuration file `conf.py` contains information related to Sphinx settings. The Sphinx documentations are written as ReStructuredText (`*.rst` files) and mostly stored in the `source/` folder. The documentation inside `source/reference` is auto-generated by Sphinx. The repository is linked with [ReadTheDocs](https://readthedocs.org/projects/lux-api/), which triggers the build for the latest documentation based on the most recent commit. As a result, we do not commit anything inside `doc/_build` in the Github repository.

# Updating the Conda Recipe

In order to update the conda recipe on conda forge, you can follow the steps [here](https://conda-forge.org/#update_recipe). The conda recipe needs to be updated when either a new dependency is added or when the version number needs to be updated in the case of a new release. 
