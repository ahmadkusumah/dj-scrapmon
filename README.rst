=====
Scrapmon
=====

Scrapmon is a simple Django app to run dedicated scrapy in using command line console

Quick start
-----------

1. Add "scrapmon" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'scrapmon',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('scrapmon/', include('scrapmon.urls')),

3. Run `python manage.py migrate` to create the scrapmon models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a scrapmon (you'll need the Admin app enabled).