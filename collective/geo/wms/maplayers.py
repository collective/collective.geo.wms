#
from five import grok
from collective.geo.mapwidget.browser.widget import MapLayers
from collective.geo.mapwidget.maplayers import MapLayer

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
        opacity = self.context.opacity
        if self.context.singlelayers:
            ollayers = []
            for layer in self.context.layers:
                ollayers.append(
                u"""
                function() {
                    return new OpenLayers.Layer.WMS("%s",
                    "%s",
                    {layers: '%s', transparent: %s},
                    {isBaseLayer: %s, opacity: %.1f});
                    }""" % (layer,
                            server_url,
                            layer,
                            transparent,
                            baselayer,
                            opacity,
                            )
                )
                baselayer = 'false'
                transparent = 'true'
            return ', '.join(ollayers)
        else:
            layers = ', '.join(self.context.layers)
            return u"""
            function() {
                    return new OpenLayers.Layer.WMS("%s",
                    "%s",
                    {layers: '%s', transparent: %s},
                    {isBaseLayer: %s, opacity: %.1f});
                    }""" % (self.context.Title().replace("'", "&apos;"),
                            server_url,
                            layers,
                            transparent,
                            baselayer,
                            opacity,
                            )



class WMSMapLayers(MapLayers):
    '''
    create all layers for this view.
    the file itself as a layer +
    the layer defined by the annotations (if any)
    '''

    def layers(self):
        layers = super(WMSMapLayers, self).layers()
        layers.append(WMSMapLayer(self.context))
        return layers




class WMTSMapLayer(MapLayer):


    def __init__(self, context):
        self.context = context

    @property
    def jsfactory(self):
        context_url = self.context.absolute_url()
        if not context_url.endswith('/'):
            context_url += '/'
        server_url = self.context.server.to_object.remote_url
        wmts = self.context.server.to_object.get_wmts_service()
        layers = self.context.layers
        format = self.context.img_format
        baselayer = str(self.context.baselayer).lower()
        ollayers = []
        for layer in layers:
            style = wmts.contents[layer].styles.keys()[0]
            ollayers.append(
            u"""
            function() {

                var matrixIds = new Array(26);
                for (var i=0; i<26; ++i) {
                    matrixIds[i] = "EPSG:900913:" + i;
                }

                    return new OpenLayers.Layer.WMTS({
                    name: "%s",
                    url: "%s",
                    layer: '%s',
                    style: '%s',
                    matrixSet: 'EPSG:900913',
                    matrixIds: matrixIds,
                    zoomOffset: 0,
                    format:'image/%s',
                    opacity: 0.7,
                    isBaseLayer: %s });
                    }""" % (layer,
                            server_url, layer, style, format, baselayer
                            ))
            baselayer = 'false'
        return ', '.join(ollayers)



class WMTSMapLayers(MapLayers):
    '''
    create all layers for this view.
    the file itself as a layer +
    the layer defined by the annotations (if any)
    '''

    def layers(self):
        layers = super(WMTSMapLayers, self).layers()
        layers.append(WMTSMapLayer(self.context))
        return layers
