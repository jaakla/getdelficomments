#!/usr/local/bin/python2.7
# encoding: utf-8
'''
Created on Dec 22, 2015

@author: jaak
'''

from lxml import html
import requests
import HTMLParser
import sys

# siia artiklite algesed url-id, üks rea kohta:
ariklid = '''
http://publik.delfi.ee/news/inimesed/video-blogi-ja-fotod-luisa-roivas-oma-abikaasa-umber-lahvatanud-ahistamisskandaalist-olen-hairitud-ja-taavis-pettunud?id=79814146&com=1&reg=0&no=0&s=1
'''

# http://www.delfi.ee/news/paevauudised/eesti/pealtnagija-eesti-pagulasvastased-vandenouteoreetikud-jalitavad-valismaalasi?id=73224487

separator = u"\t"

def printComments(of, h, artikkel, reg, url):
    
    page = requests.get(url)
    tree = html.fromstring(page.content)
    comments = tree.xpath('//div[@class="comment-content-inner"]')
    authors = tree.xpath('//div[@class="comment-author"]')
    commentDates = tree.xpath('//div[@class="comment-date"]/text()')
    commentVotesUp = tree.xpath('//div[@class="comment-votes-up"]/a/span[@class="comment-votes-count"]/text()')
    commentVotesDown = tree.xpath('//div[@class="comment-votes-down"]/a/span[@class="comment-votes-count"]/text()')
    commentsPagerNext = tree.xpath('//div[@class="comments-pager comments-pager-top"]/a[@class="comments-pager-arrow-last"]')
    
# trüki üldtulemused, kontrolliks lihtsalt
#print "comments: ",len(comments)
#print "authors: ",len(authors)
#print "commentDates: ",len(commentDates)
#print "commentVotesUp: ",len(commentVotesUp)
#print "commentVotesDown: ",len(commentVotesDown)
#print "url:",url
#    exit()

    # trüki kõik leitud kommentaarid välja
    for i in range(len(commentDates)):
        # vote-d on kaks korda miskipärast, seega 
        ii = i * 2 + 1
        
        # puhasta comment erinevast HTML läbust, reavahe jms
        #comment = comments[i]
        comment = h.unescape(html.tostring(comments[i])).replace("</div>", "").replace("<div class=\"comment-content-inner\">", "").strip()
        
        # reavahe asendus
        comment = comment.replace("<br>\n", u'⏎')
        # DELFI spam ära
        comment = comment.replace('<font class="delfiCoB">D</font><font class="delfiCoY">E</font><font class="delfiCoB">LFI</font>', 'DELFI')
        # puhasta autor HTML-ist
        author = h.unescape(html.tostring(authors[i])).replace("</div>", "").replace("<div class=\"comment-author\">", "").replace('<a href="javascript:void(1)" onclick="CommentList.showUserComments(this)">', "").replace("</a>", "").strip()
        
        print >> of, artikkel, separator, reg, separator, i, separator, author.encode('utf-8'),separator, commentDates[i].strip(), separator, commentVotesUp[i].strip(), separator, commentVotesDown[i].strip(), separator , comment.encode('utf-8')

    # kui on veel kommentaaride lehti, sisi võta pager-ist URL-id ja päri neid ka, kasutades sama funktsiooni (1-kordne rekursioon)
    for pager in commentsPagerNext: # seal on 1 tegelikult alati vaid, või 0 kui pole järgmist lehekülge
        newUrl = pager.attrib.get('href')
            
        printComments(of, h, artikkel, reg, newUrl) # rekursiivne

# MAIN program start

if len(sys.argv)<2:
    print "Pane väljundi failinimi käsu parameetriks, näiteks 'python getcomments.py output.csv' !"
    exit()

outputFileName = sys.argv[1]

outputFile=open(outputFileName, 'w+')

h = HTMLParser.HTMLParser()

for artikkel in ariklid.split( ):
    
    for reg in range(2): # 0 - anon, 1 - registered user
        
        url = artikkel + "&com=1&reg=%s&no=0&s=1" % (reg)
        
        printComments(outputFile, h, artikkel, reg, url)
    

