server
===========

## Steps to run it locally

Download and install Google AppEngine SDK for your platform

    git clone https://github.com/omg-insa/server

Clone the server repository

    cd server
    
Enter the repository

    ./manage.py createsuperuser

Create a new super user for the first time

    ./manage.py runserver
    
Run the server locally

    ./manage.py deploy 
    
Deploy the server to appspot.com (Only for developers and owners)
