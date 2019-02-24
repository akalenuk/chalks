#!/usr/bin/python

import os
import re
import sys
import cgi
import time
import random
import tempfile
import webbrowser

separators = " @(){}[],.:;\"\'`<>=+-*/\t\n\\?|&#%!"
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


def match(pattern, line):       # works for '*' and '?'
        def find_with_question(pattern, line, start = 0):
                if len(pattern) > len(line):
                        return -1
                differences = [1 for (a,b) in zip(pattern, line) if a != b and a != '?']
                if differences == []:
                        return start
                return find_with_question(pattern, line[1:], start+1)

        chunks = ('\0' + pattern + '\0').split("*") 
        
        def check_order(chunks, line):
                if chunks == []:
                        return True
                n = find_with_question(chunks[0], line)
                if n < 0:
                        return False
                return check_order(chunks[1:], line[n + len(chunks[0]):])
        
        return check_order(chunks, '\0' + line + '\0')

        
ls = os.listdir(".")
names = []
for arg in sys.argv[1:]:
        names += [name for name in ls if match(arg, name)]

if names == []:
        print "None of files match."    
        exit(1)

style = """
a {color:#777; text-decoration:none;}
a.ten {color:#BBB; text-decoration:none;}
a:hover {color:#CBC}
body {background-color:#000; color:#BAB;} 
"""
new_text = "<html><head><title>" + str(names) + "</title><style>" + style + "</style></head><body>"

LOC = 0
NELOC = 0
for name in names:

        file_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(name)))
        new_text += "<br><br><font color=#AAA size=6>" + name + "</font><br>"
        new_text += "<font color=#777 size=3> " + file_time + "</font><br><br>"

        f = open(name)
        lines = f.readlines()
        f.close()

        lines = [line.rstrip() + "\n" for line in lines]
        LOC += len(lines)
        NELOC += len([line for line in lines if line != "\n"])

        word = ""
        for line, n in zip(lines, range(1, len(lines)+1)):
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



        
        new_text += "<table><tr>"

        # numbers
        new_text += "<td valign='top'><pre>"
        for line, n in zip(lines, range(1, len(lines)+1)):
                if n % 10 == 0:
                        cls = " class=\"ten\""
                else:
                        cls = ""
                new_text += "<a id=\"" + name + ':' + str(n) + "\"><a href=\"#" + name + ':' + str(n) + "\"" + cls + ">"
                new_text += " " + str(n) + 3*" "
                new_text += "</a></a><br>"
        new_text += "</pre></td>"

        # code
        word = ""
        new_text += "<td valign='top'><pre>"
        for line, n in zip(lines, range(1, len(lines)+1)):
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

                                if c == '\t':
                                        new_text += "<span style=\"background-color: #050505;\">"
                                new_text += safe_separators[c]
                                if c == '\t':
                                        new_text += "</span>"
                        else:
                                word += c
                n += 1
        new_text += "</pre></td>"
        
        new_text += "</tr></table>"
        
def prettify(number):
        if len(number) < 3:
                return number
        return prettify(number[:-3]) + " " + number[-3:]

new_text += "<br><font color=#777 size=4>Total not empty lines count: "+ prettify(str(NELOC)) +"</font><br>"

new_text += "</body></html>"


# temp file left undeleted
f = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
f.write(new_text)
f.close()

webbrowser.open(url=f.name)
