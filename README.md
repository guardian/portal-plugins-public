# portal-plugins-public
Plugins for Cantemo Portal developed by the Guardian


* gnmawsgr - Restoring media that had been archived to S3/Glacier from Final Cut Server
* gnmextprojecthelper - helper API functions for Pluto projects
* gnmgridintegration - sending Portal thumbnail snaps to The Grid image management system
* gnmlibrarytool - technical UI to help when working with large Vidispine libraries for media management
* gnmlogsearch - technical UI to search/present more information from the Vidispine logs
* gnmplutoconverter - gearbox plugin to convert any item into a Portal master
* gnmplutostats - admin UI to show how many Pluto projects are in which state
* gnmpropagation - backend task plugin to ensure that metadata values are propagated from commissions to projects to media
* gnmsyndication - views of published material for non Video producers
* gnmuploadprofiler - uses Vidispine changesets to measure the time taken through the upload chain
* gnmyoutube - utility functions for working with Youtube, including creating a local cache of youtube categories
* gnmzeitgeist - widgets for showing popular field values, intended for search pages
* helloworld - basic "hello world" boilerplate code
* rabbitmon - monitoring rabbitmq state


# Setting up a Test Environment on MacOS X

When testing on a virtualenv on MacOS X the following commands are useful: -

`/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

`brew install swig`

`brew install openssl`

`LDFLAGS="-L$(brew --prefix openssl)/lib" CFLAGS="-I$(brew --prefix openssl)/include" SWIG_FEATURES="-I$(brew --prefix openssl)/include" pip install m2crypto==0.22.3`

What does all that do?

1. Installs a useful package manager for Mac OS X called Homebrew
2. Installs Swig
3. Installs OpenSSL (if not present)
4. Installs M2Crypto

You should then be able to run the command below to install the rest of the requirements: -

`pip install -r test-requirements.txt`

'Why is this needed?', you may ask. At the time of writing Mac OS versions older than 10.12 have an older version of OpenSSL installed than M2Crypto wants. We install a newer version of OpenSSL, then tell M2Crypto to use it when it compiles the C code routines. 

