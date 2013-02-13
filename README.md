# SERVER

## Steps to run it locally

1. Download and install [Google AppEngine SDK](https://www.google.com/search?q=google+appengine+sdk) for your platform.

2. Install `python-memcache`:

    `sudo apt-get install python-memcache`

3. Clone the server repository:

    `git clone https://github.com/omg-insa/server`    
    `cd server`

4. Create a new super user for the first time:

    `./manage.py createsuperuser`

5. Run the server locally:

    `./manage.py runserver`

6. Deploy the server to appspot.com (Only for developers and owners)

    `./manage.py deploy`


## Tips for Windows

1. To install 'python-memcache' follow this tutorial to install 'easy_install'
    [Easy_install Tuto](http://blog.sadphaeton.com/2009/01/20/python-development-windows-part-2-installing-easyinstallcould-be-easier.html)

2. Open a command line:

    'easy_install python-memcached'
