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
