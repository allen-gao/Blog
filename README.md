Blog
====
A simple blog created with the webapp2 Python framework in Google App Engine, with the help of CS253 on Udacity. You can check out the site here: http://allengao-blog.appspot.com/

**(For developers) To host this webapp locally:**

1. Download and install [Google App Engine](https://developers.google.com/appengine/downloads) for Python
2. Download and Install [Python 2.7x](https://www.python.org/downloads/)
3. Clone this repo
4. Create a new .py file called userkey.py and define a constant "key" to be a random string, and place it in the root directory of the repo
5. From the Google App Engine Launcher, go to File -> 'Add Existing Application' and choose the local repo folder
6. Click Run and go to localhost:xxxx where xxxx is the port # (default should be localhost:8080)

**This site uses:**
- webapp2 Python framework for the backend
- Google Datastore (Google's NoSQL database)
- Raw HTML/CSS (Jinja2 for templating)
****

No authentication library was used for this webapp so hashing, salting, and cookies were implemented manually.
