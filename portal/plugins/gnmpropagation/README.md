# portal.plugins.gnmpropagation

Simple metadata propagation plugin

This plugin relies on the Pluto Business Logic plugin.

It defines a BL rule (tickbox_propagation.xml) which calls a background task
whenever specific metadata fields change on a collection.  The task then 
propagates this down to child collections and items.

This has the effect of recursing, since the when the task sets the value on a child
item it causes the BL rule to be called again on said child item.

Setup
-----

NOTE - this will not work "out of the box!!!" Read this section!!!

The recursive nature of the operation means that this can quickly backlog
the default celery queue.

It therefore intentionally targets a different queue, called "propagator". 

You need to ensure that you have a Celery worker set up to listen to this
queue, which you can do by pasting the following into

``/etc/supervisor/conf.d/portal.conf``

``
[program:propagatorqueue]
command=/opt/cantemo/python/bin/newrelic-admin run-program /opt/cantemo/portal/manage.py celery worker --concurrency 1 -Q propagator -n pluto.propagator@%%h
directory=/opt/cantemo/portal/portal
environment=PYTHONPATH='/opt/cantemo/portal/',NEW_RELIC_CONFIG_FILE=/opt/cantemo/newrelic.ini
user=www-data
autostart=True
autorestart=True
numprocs=1
startsecs=10
stopwaitsecs=30
redirect_stderr=True
stdout_logfile=/var/log/cantemo/portal/celery_propagatorqueue.log
stderr_logfile=/var/log/cantemo/portal/celery_propagatorqueue.log
``

Then run:

``sudo service supervisor restart``

This should make the queue appear in Celery Flower.
Once you have done this, install the plugin from its RPM and it should
work.