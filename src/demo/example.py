from TeaLeaf.CGI import CGI
from TeaLeaf.Html.Elements import *
from TeaLeaf.Html.JS import JS
from TeaLeaf.Html.MagicComponent import FetchComponent
import urllib.request

server = CGI()


contents = urllib.request.urlopen("http://example.org")
server.serve(contents.read())
