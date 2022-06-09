import six
from nplusone.ext.django import NPlusOneMiddleware

from core.custom_nplusone.customer_listeners import custom_listeners


class CustomerNPlusOneMiddleware(NPlusOneMiddleware):

    def process_request(self, request):
        self.load_config()
        self.listeners[request] = self.listeners.get(request, {})
        for name, listener_type in six.iteritems(custom_listeners):
            self.listeners[request][name] = listener_type(self)
            self.listeners[request][name].setup(request=request)
