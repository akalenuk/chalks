#!/usr/bin/python
#
# Copyright 2013 Alexandr Kalenuk.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# mailto: akalenuk@gmail.com

import re
import sys
import cgi
import random
import tempfile
import webbrowser
import hashlib

separators = " @(){}[],.:;\"\'`<>=+-*/\t\n\\?|&#"
safe_separators = {}

for s in separators:
    safe_separators[s] = cgi.escape(s, quote = True)

n = 0
lines = []
chunks = set()
chunk_ns = {}
if len(sys.argv)==1:
    print "Select file."
    exit(1)

name = sys.argv[1]
f = open(name)
lines = f.readlines()
lines = [line.rstrip() + "\n" for line in lines]
f.close()


word = ""
for line in lines:
    for c in line:
        if c in separators:
            if word != "":
                chunks.add(word)
                if word in chunk_ns:
                    chunk_ns[word] += 1
                else:
                    chunk_ns[word] = 1
            word = ""
        else:
            word += c


def color_of(word):
    if ord(word[0]) >= 128:
        return "909090"
    def to_ff(x):
        y = hex( int(x) )[2:]
        if len(y) == 1:
            return "0"+y
        else:
            return y
    random.seed(word)
    word_n = random.random() * 2147483648
    r = (word_n % 140) + 100;
    g = (word_n / 140 % 130) + 100;
    b = (word_n / 140 / 130 % 140) + 100;
    return to_ff(r) + to_ff(g) + to_ff(b)

chunks_col = {}
for chunk in chunks:
    color = color_of(chunk);
    chunks_col[chunk] = color


mail = ""
for line in lines:
    mail_if_any = re.search(r"[\w.]+@[\w.]+", line)
    if mail_if_any != None:
        mail = mail_if_any.group(0)
        break
                

style = """
a {color:#777; text-decoration:none;}
a.ten {color:#BBB; text-decoration:none;}
a:hover {color:#CBC}
body {  
    background-color:#000; 
	color:#BAB; 
	background: linear-gradient(
	    to right, 
        #030303 10%, #040404 10%, 
        #040404 20%, #050505 20%, 
        #050505 30%, #060606 30%, 
        #060606 40%, #070707 40%, 
        #070707 50%, #080808 50%, 
        #080808 60%, #070707 60%, 
        #070707 70%, #060606 70%, 
        #060606 80%, #050505 80%, 
        #050505 90%, #040404 90% 
    );
} 
"""

def mailto(mail, subj, text):
    return "\"mailto:" + mail + "?subject=" + subj + " &body=" + cgi.escape(text, quote = True) + "\""
    
    
new_text = "<html><head><title>" + name + "</title><style>" + style + "</style></head><body>"
new_text += "<table><tr>"

# numbers
new_text += "<td><pre>"
for n, line in enumerate(lines, 1):
    if n % 10 == 0:
        cls = " class=\"ten\""
    else:
        cls = ""
    new_text += "<a href=" + mailto(mail, name + ": " + str(n), line) + cls + ">"
    new_text += " " + str(n) + 3*" "
    new_text += "</a><br>"
new_text += "</pre></td>"

# code
word = ""
new_text += "<td><pre>"
for n, line in enumerate(lines, 1):
    for c in line:
        if c in separators:
            if word != "":
                i = ""
                uni = ""
                if chunk_ns[word] == 1:
                    i = "<i>"
                    uni = "</i>"
                new_text += "<font color=\"#" + chunks_col[word] + "\">" + i + word + uni + "</font>"
                word = ""
            new_text += safe_separators[c]
        else:
            word += c
    n += 1
new_text += "</pre></td>"    

new_text += "</tr></table>"
new_text += "</body></html>"


# temp file left undeleted
f = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
f.write(new_text)
f.close()

webbrowser.open(url=f.name)
