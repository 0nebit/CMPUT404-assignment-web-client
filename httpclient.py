#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

import time

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    #def get_host_port(self,url):

    def connect(self, host, port):
        # use sockets!
        if (not port):
            self.sock.connect((host, 80))
        else:
            self.sock.connect((host, port))
        
        return None

    def get_code(self, data):
        code = data.split("\r\n")[0].split(" ")[1]
        return code

    def get_headers(self, data):
        headers = data.split("\r\n\r\n")[0]
        return headers

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        sock.settimeout(4)
        while not done:
            try:
                part = sock.recv(1024)
            except socket.timeout, e:
                done = True
            else:
                if (part):
                    buffer.extend(part)
                else:
                    done = not part
        return str(buffer)

    def GET(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.parse_url(url)

        if (host == "localhost"):
            self.connect("127.0.0.1", port)
        else:
            self.connect(host, port)
        
        request = self.format_request("GET", host, port, path)
        
        self.sock.sendall(request)
        response = self.recvall(self.sock)

        # to deal with bad file descriptors
        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # format response
        code = int(self.get_code(response))
        body = self.get_body(response)

        # print response body to output
        print body
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.parse_url(url)

        if (host == "localhost"):
            self.connect("127.0.0.1", port)
        else:
            self.connect(host, port)

        request = self.format_request("POST", host, port, path, args)
        
        self.sock.sendall(request)
        response = self.recvall(self.sock)

        # to deal with bad file descriptors
        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # format response
        code = int(self.get_code(response))
        body = self.get_body(response)

        # print response body to output
        print body
        
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

    # returns the hostname, port number, and path of an URL string
    # host: string
    # port: int
    # path: string
    def parse_url(self, url):
        host = None
        port = None
        path = None

        if (url[0:7] == "http://"):
            host = url[7:]
        else:
            host = url

        # url may still include port and path
        
        if ("/" in host):
            index = host.index("/")
            path = host[index:]
            host = host[0:index]
        
        if (":" in host):
            index = host.index(":")
            port = int(host[index+1:])
            host = host[0:index]

        # default root path
        if (not path):
            path = "/"
            
        return host, port, path

    def format_request(self, command, host, port, path, args=None):
        if (command == "GET"):
            request_template = "GET {path_var} HTTP/1.1\r\n" \
                               "Host: {host_var}\r\n" \
                               "Connection: keep-alive\r\n"
        elif (command == "POST"):
            request_template = "POST {path_var} HTTP/1.1\r\n" \
                               "Host: {host_var}\r\n" \
                               "Connection: keep-alive\r\n"

        if (port):
            request = request_template.format(path_var = path,
                                              host_var = host+":"+str(port))
        else:
            request = request_template.format(path_var = path,
                                              host_var = host)

        if (command == "POST"):
            request += "Content-Type: application/x-www-form-urlencoded\r\n"
            if (isinstance(args, dict) and args.keys() != []):
                args = urllib.urlencode(args)
                request += "Content-Length: "+str(len(args))+"\r\n\r\n"
                request += args+"\r\n"
            else: # no POST data given
                request += "Content-Length: 0\r\n"

        request += "\r\n"
        
        return request

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    print sys.argv
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( command, sys.argv[1] )
