#
import json, urllib
from five import grok
from collective.geo.mapwidget.browser.widget import MapLayers
from collective.geo.mapwidget.maplayers import MapLayer


MAX_EXTENT= "maxExtent: new OpenLayers.Bounds(%f, %f, %f, %f).transform(geographic, mercator),"

class TMSMapLayer(MapLayer):

    def __init__(self, context):
        self.context = context

    @property
    def jsfactory(self):
        context_url = self.context.absolute_url()
        if not context_url.endswith('/'):
            context_url += '/'
        tms = self.context.server.to_object.get_service()
        layers = self.context.layers
        format = self.context.img_format
        baselayer = str(self.context.baselayer).lower()
        opacity = self.context.opacity
        projection = self.context.srs
        ollayers = []
        base_url = urllib.unquote(tms.url.rstrip('/'))
        base_url = base_url.rstrip(tms.version)
        for layer in layers:
            layername = tms.contents[layer].title
            layer_id = urllib.unquote(layer).lstrip(base_url
                            ).lstrip(tms.version).lstrip('/')
            ollayers.append(u"""
            function() {
                return new OpenLayers.Layer.TMS('%(name)s',
                    '%(url)s',
                    {layername: '%(layer)s',
                    serviceVersion: '%(version)s', type: '%(format)s',
                    transitionEffect: 'resize',
                    projection: new OpenLayers.Projection("%(projection)s"),
                    isBaseLayer: %(baselayer)s /*opacity: %(opacity).1f*/})
                    }
            """ % {'name': layername,
                    'url': base_url,
                    'layer': layer_id,
                    'version': tms.version,
                    'format': format,
                    'baselayer': baselayer,
                    'opacity': opacity,
                    'projection': projection,}

            )
            baselayer = 'false'
        return ', '.join(ollayers)


class WMSMapLayer(MapLayer):


    def __init__(self, context):
        self.context = context

    @property
    def jsfactory(self):
        context_url = self.context.absolute_url()
        if not context_url.endswith('/'):
            context_url += '/'
        server_url = self.context.server.to_object.remote_url
        baselayer = str(self.context.baselayer).lower()
        transparent = str(not self.context.baselayer).lower()
        projection = self.context.srs
        opacity = self.context.opacity
        if self.context.singlelayers:
            wms = self.context.server.to_object.get_service()
            ollayers = []
            for layer in self.context.layers:
                layername = wms.contents[layer].title
                ollayers.append(
                u"""
                function() {
                    return new OpenLayers.Layer.WMS('%(name)s',
                    '%(url)s',
                    {layers: '%(layer)s', transparent: %(transparent)s,
                    transitionEffect: 'resize',
                    projection: new OpenLayers.Projection("%(projection)s"),
                    isBaseLayer: %(baselayer)s, opacity: %(opacity).1f});
                    }""" % {'name': layername,
                            'url': server_url,
                            'layer': layer,
                            'transparent': transparent,
                            'baselayer': baselayer,
                            'opacity': opacity,
                            'projection': projection,
                            }
                )
                baselayer = 'false'
                transparent = 'true'
            return ', '.join(ollayers)
        else:
            layers = ', '.join(self.context.layers)
            return u"""
            function() {
                    return new OpenLayers.Layer.WMS('%(name)s',
                    '%(url)s',
                    {layers: '%(layers)s', transparent: %(transparent)s,
                    transitionEffect:'resize',
                    projection: new OpenLayers.Projection("%(projection)s"),
                    isBaseLayer: %(baselayer)s, opacity: %(opacity).1f});
                    }""" % {'name': self.context.Title().replace("'", "&apos;"),
                            'url': server_url,
                            'layers': layers,
                            'transparent': transparent,
                            'baselayer': baselayer,
                            'opacity': opacity,
                            'projection': projection,
                            }




class WMTSMapLayer(MapLayer):


    def __init__(self, context):
        self.context = context

    @property
    def jsfactory(self):
        context_url = self.context.absolute_url()
        if not context_url.endswith('/'):
            context_url += '/'
        server_url = self.context.server.to_object.remote_url
        wmts = self.context.server.to_object.get_service()
        layers = self.context.layers
        format = self.context.img_format
        baselayer = str(self.context.baselayer).lower()
        opacity = self.context.opacity
        projection = self.context.srs
        ollayers = []
        for layer in layers:
            style = wmts.contents[layer].styles.keys()[0]
            layername = wmts.contents[layer].title.replace("'", "&apos;")
            #if wmts.contents[layer].boundingBoxWGS84:
            #    max_extent = MAX_EXTENT % wmts.contents[layer].boundingBoxWGS84
            #else:
            #    max_extent =''
            tilematrixset = None
            for tms in  wmts.contents[layer].tilematrixsets:
                if tms == self.context.srs:
                    tilematrixset = tms
            if tilematrixset:
                tilematrixids = []
                for tm in wmts.tilematrixsets[tilematrixset].tilematrix.values():
                    tilematrixids.append({
                    'identifier': tm.identifier,
                    'scaleDenominator': tm.scaledenominator,
                    #'topLeftCorner': tm.topleftcorner,
                    'tileWidth': tm.tilewidth,
                    'tileHeight': tm.tileheight,
                    })
            else:
                raise ValueError('No TileMatrix found')

            ollayers.append(
            u"""
            function() {
                return new OpenLayers.Layer.WMTS({
                    name: "%(name)s",
                    url: "%(url)s",
                    layer: '%(layer)s',
                    style: '%(style)s',
                    matrixSet: '%(matrixset)s',
                    matrixIds: %(matrixids)s,
                    format:'image/%(format)s',
                    projection: new OpenLayers.Projection("%(projection)s"),
                    opacity: %(opacity).1f,
                    transitionEffect:'resize',
                    isBaseLayer: %(baselayer)s });
                    }""" % {'name': layername,
                            'url': server_url,
                            'layer': layer,
                            'matrixset': tilematrixset,
                            'matrixids': json.dumps(tilematrixids),
                            'style': style,
                            'format': format,
                            'opacity': opacity,
                            'projection': projection,
                            'baselayer': baselayer
                            })
            baselayer = 'false'
        return ', '.join(ollayers)


class WMSMapLayers(MapLayers):
    '''
    create all layers for this view.
    the file itself as a layer +
    the layer defined by the annotations (if any)
    '''

    def layers(self):
        if self.context.defaultlayers:
            layers = super(WMSMapLayers, self).layers()
        else:
            layers=[]
        if self.context.server.to_object.protocol == 'wms':
            layers.append(WMSMapLayer(self.context))
        elif  self.context.server.to_object.protocol == 'wmts':
            layers.append(WMTSMapLayer(self.context))
        elif  self.context.server.to_object.protocol == 'tms':
            layers.append(TMSMapLayer(self.context))
        return layers


