Introduction
============

``collective.geo.wms`` is a product which enables you to embed
WMS, TMS and WMTS layers in your `Plone`_ website using `collective.geo`_.

It is designed to make adding WMS, TMS or WMTS layers as easy as possible.


Why WMS/TMS/WMTS
-----------------

You will find thousands of public Map Servers with interesting and
valuable information which you can display on your website. Many of these
services provide WMS,TMS or WMTS only.


Usage
------

First you have to add a WMS Server to your site. The initial
add form only allows you to enter the URL and type of a webservice. The title,
description and keywords are taken from the service if it produces a valid response
to the getCapabilities query. When the server could be successfully added
you can change the title, description and keywords. You are not allowed to change
the server URL or protocol. A list of layers that are available on this server will
be requested directly from the server. The list of layers will be cached
for 100 minutes so if layers are added on the server you may have to wait
up to 2 hours for them to refresh.

After you added the servers you can add layers to your website. Layers
are displayed as a Map.

In the add form you choose the service for your maps. You cannot change
the server later by editing the layer. After you added the layer you have
to choose the layers of the service you want to display in your map. Some
WMS Servers do not support overlaying layers on the server side if this is
the case for the server you are connecting to you have to check
'Single Layers' for them to display.

When you click on a feature on the map a request is sent to the server to
get information about this feature (or features) which are displayed in
a pop up. This behavior can be disabled by unchecking 'Feature Info'

You need the latest version of OWSLib (currently 0.7.2) to use TMS and
WMTS.


Documentation
=============

Full documentation for end users can be found in the "docs" folder.
It is also available online at https://collectivegeo.readthedocs.io/


Translations
============

This product has been translated into

- Spanish.

You can contribute for any message missing or other new languages, join us at 
`Plone Collective Team <https://www.transifex.com/plone/plone-collective/>`_ 
into *Transifex.net* service with all world Plone translators community.


Tests status
============

This add-on is tested using Travis CI. The current status of the add-on is:

.. image:: https://img.shields.io/travis/collective/collective.geo.wms/master.svg
    :target: https://travis-ci.org/collective/collective.geo.wms

.. image:: http://img.shields.io/pypi/v/collective.geo.wms.svg
   :target: https://pypi.org/project/collective.geo.wms


Contribute
==========

Have an idea? Found a bug? Let us know by `opening a ticket`_.

- Issue Tracker: https://github.com/collective/collective.geo.wms/issues
- Source Code: https://github.com/collective/collective.geo.wms
- Documentation: https://collectivegeo.readthedocs.io/


License
=======

The project is licensed under the GPLv2.

.. _Plone: https://plone.org/
.. _collective.geo: https://pypi.org/project/collective.geo.bundle
.. _`opening a ticket`: https://github.com/collective/collective.geo.bundle/issues
