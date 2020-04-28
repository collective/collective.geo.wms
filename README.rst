Introduction
============

collective.geo.wms is a product which enables you to embed
WMS, TMS and WMTS layers in your website.

It is designed to make adding WMS, TMS or WMTS layers as easy as possible.



Why WMS/TMS/WMTS
-----------------

You will find thousands of public Map Servers with interesting and
valuable information which you can display on your website. Many of these
services provide WMS,TMS or WMTS only.


Usage
------

First you have to add a WMS Server to your site. The initial
add form only allows you to enter the url and type of a webservice. The title,
description and keywords are taken from the service if it produces a valid response
to the getCapabilities query. When the server could be successfully added
you can change the title, descripton and keywords. You are not allowed to change
the server url or protocol. A list of layers that are available on this server will
be requested directly from the server. The list of layers will be cached
for 100 minutes so if layers are added on the server you may have to wait
up to 2 hours for them to refresh.

After you added the servers you can add layers to your website. Layers
are displayed as a Map.

In the add form you choose the service for your maps. You cannot change
the server later by editing the layer. After you added the layer you have
to choose the layers of the service you want to display in your map. Some
WMS Servers do not support overlaying layers on the serverside if this is
the case for the server you are connecting to you have to check
'Single Layers' for them to display.

When you click on a feature on the map a request is sent to the server to
get information about this feature (or features) which are displayed in
a pop up. This behaviour can be disabled by unchecking 'Feature Info'

You need the latest version of OWSLib (currently 0.7.2) to use TMS and
WMTS


Translations
------------

This product has been translated into

- Spanish.

You can contribute for any message missing or other new languages, join us at 
`Plone Collective Team <https://www.transifex.com/plone/plone-collective/>`_ 
into *Transifex.net* service with all world Plone translators community.
