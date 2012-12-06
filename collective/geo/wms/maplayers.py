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
        layers = ', '.join(self.context.layers)
        baselayer = str(self.context.baselayer).lower()
        transparent = str(not self.context.baselayer).lower()
        return u"""
        function() {
                return new OpenLayers.Layer.WMS("%s",
                "%s",
                {layers: '%s', transparent: %s},
                {isBaseLayer: %s });
                }""" % (self.context.Title().replace("'", "&apos;"),
                        server_url,
                        layers,
                        transparent,
                        baselayer,
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
        layers = self.context.layers
        format = self.context.img_format
        baselayer = str(self.context.baselayer).lower()
        ollayers = []
        for layer in layers:
            ollayers.append(
            u"""
            function() {
                    return new OpenLayers.Layer.TMS("%s",
                    "%s",
                    {layername: '%s', type:'%s'},
                    {isBaseLayer: %s });
                    }""" % (layer,
                            server_url, layer, format, baselayer
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
