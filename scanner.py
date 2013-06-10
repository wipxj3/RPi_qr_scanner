#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'dexter'
# Time Library
import time
import RPi.GPIO as GPIO

def getTime():  # Function that returns a Timestamp %H_%M_%S
    t = time.localtime()
    timestamp = str(t.tm_hour) + '_' + str(t.tm_min) + '_' + str(t.tm_sec)
    return timestamp


def captureImage():  # Function for capturing GRAY image and threshold transformation
    # OpenCV 2.4.3 compiled with python bindings
    import cv2
    capture = cv2.VideoCapture(0)
    time.sleep(2)

    ret, img = capture.read()
    # RGB -> GRAY color filter
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    imagePath = 'capture/'
    imageIndex = imagePath + getTime() + '_capture'
    cv2.imwrite(imageIndex + '.png', img_gray)
    return imageIndex


def decodeQr(imageIndex):
    
    from PIL import Image 
    pil = Image.open(imageIndex +'.png').convert('L')
    width, height = pil.size
    raw = pil.tostring()

    import zbar
    image = zbar.Image(width, height, 'Y800', raw)
    scanner = zbar.ImageScanner()
    scanner.scan(image)
    
    for symbol in image:
    # do something useful with results
        info = symbol.data
    
    try:
	   decodedData = str(info)
	   return decodedData
    except Exception:
	   print "No data found"
	   return 'error'


def checkValidity(value):
    import urllib2
    req = urllib2.Request('http://pinteav.starnet.md:8000/request/check/?ticket=' + str(value))
    
    try: 
        response = urllib2.urlopen(req)
    except URLError as e:
        print e.reason 
    
    the_page = response.read()
    
    flag = fetchResult(the_page)
    #print '\n' + getTime() + ' >> CHECKING VALIDITY ' + str(value)
    #flag = 'VALID'
    return flag

def fetchResult(html):
    import re
    rex = re.findall('<div class="hero-unit".*?>(.*?)</div>', html, re.S)
    validity = re.search('<h2>(.*?)</h2>', rex[0])
    shortHash = re.search('<h3>(.*?)</h3>', rex[0])
    return validity.group(), shortHash.group()

if __name__ == '__main__':
    dataList = []
    payload = None
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT)
    # Regular Expression Library
    import re
    CHECK_RE = re.compile('[a-zA-Z0-9]')
    count = 0
    while True:
        count += 1
        GPIO.output(11, False)
        capture = captureImage()
        payload = decodeQr(capture)
        print '----------------------------------------'
        print payload
        print '----------------------------------------'
        if (len(payload) == 54) and (CHECK_RE.match(payload)):
            response, shortHash = checkValidity(payload)
            print '========================================'
            print 'STATUS >> ' + response + ' ' + shortHash
            print '========================================'
	    GPIO.output(11, True)
        time.sleep(1)
