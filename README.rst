Introduction
============

collective.geo.wms is a product which enables you to embed
WMS and TMS layers in your website.

It is designed to make adding WMS or WMTS layers as easy as possible.



Why WMS/TMS
------------

You will find thousands of public Map Servers with interesting and
valuable information which you can display on your website. Many of these
services provide WMS or WMTS only.


Usage
------

First you have to add a WMS or WMTS Server to your site. The initial
add form only allows you to enter the url and type of a webservice. The title,
description and keywords are taken from the service if it produces a valid response
to the getCapabilities query. When the server could be successfully added
you can change the title, descripton and keywords. You are not allowed to change
the server url or protocol. A list of layers that are available on this server will
be requested directly from the server.

After you added the servers you can add layers to your website. Layers
are displayed as a Map.

In the add form you choose the service for your maps. You cannot change
the server later by editing the layer. After you added the layer you have
to choose the layers of the service you want to display in your map.

When you click on a feature on the map a request is sent to the server to
get information about this feature (or features) which are displayed in
a pop up.


WTMS is currently only available if you use the latest unreleased version
of OWSLib from https://github.com/geopython/OWSLib

