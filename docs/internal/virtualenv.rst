virtualenv
==========

Follow the steps below to get the source files from BitBucket and to setup a
development virtual environment.


Get the Project
---------------

To clone the `project source <https://www.bitbucket.org/denisgomes/arackpy>`_
from BitBucket type the following into the terminal:

.. code-block:: bash

    cd ~/Projects
    hg clone https://denisgomes@bitbucket.org/denisgomes/arackpy
    cd arackpy


Setup virtualenv
----------------

It is recommended you install **arackpy** into a virtual environment before
doing any development work. First install virualenvwrapper to manage your
environments:

.. code-block:: bash

    pip install virtualenvwrapper


Read the `virtualenvwrapper documentation
<https://virtualenvwrapper.readthedocs.io/en/latest/>`_ to learn more about how
to source the initialization shell script to use the commands used below.

.. note:: On Windows the pip package is called *virtualenvwrapper-win*.


Next, create a virtual environment called *spider* and set the project
directory:

.. code-block:: bash

    mkvirtualenv spider
    setvirtualenvproject


Finally, install the development dependencies and the project itself so that
it is editable:

.. code-block:: bash

    pip install -r requirements.txt
    pip install -e arackpy


*That's it!* You are ready to make changes and push them to the development
branch, but first read about how to contribute to the project.
