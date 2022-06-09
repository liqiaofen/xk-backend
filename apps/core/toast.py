# https://smarty.stepofweb.com/5.0.0/html_frontend/documentation/plugins-sow-toasts.html
TYPE_DEFAULT = 'default'
TYPE_SUCCESS = 'success'

POS_TOP_CENTER = 'top-center'


class Toast(object):

    def __init__(self, t_title, t_body, t_type=TYPE_SUCCESS, t_pos=POS_TOP_CENTER, t_delay=2000, t_bg_fill=True):
        self.t_type = t_type
        self.t_title = t_title
        self.t_body = t_body
        self.t_pos = t_pos
        self.t_delay = t_delay
        self.t_bg_fill = t_bg_fill
