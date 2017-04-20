# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def do_POST(self):
    print "got post!!"
    content_len = int(self.headers.getheader('content-length', 0))
    post_body = self.rfile.read(content_len)
    test_data = simplejson.loads(post_body)
    print "post_body(%s)" % (test_data)
    return SimpleHTTPRequestHandler.do_POST(self)
