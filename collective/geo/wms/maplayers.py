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
        return u"""
        function() {
                return new OpenLayers.Layer.WMS("%s",
                "%s",
                {layers: '%s', transparent: true},
                {isBaseLayer: %s });
                } """ % (self.context.Title().replace("'", "&apos;"),
                        server_url,
                        layers,
                        baselayer
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
