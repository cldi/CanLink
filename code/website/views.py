from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings
import os
import requests
from ipware.ip import get_ip
import time
import codecs
import json
import io
from .processing import *
from .processing.processing import *
from django.views.decorators.csrf import csrf_exempt
# import processing.processing
# Create your views here.

def index(request):
    return render(request, "website/header.html")


def thesisSubmission(request):
    # called when the presses the submit button after pasting the records
    if request.method == 'POST':
        if request.is_ajax():

            if len(request.FILES) != 0:
                # a file was uploaded
                file = request.FILES["records_file"].read()
                try:
                    raw_records = file.decode("utf-8")
                except:
                    raw_records = file.decode("cp1252")

            else:
                # copy and paste
                raw_records = request.POST.get("records") 

            # recaptcha_response = request.POST.get("recaptcha")
            user_ip = get_ip(request)

            # convert js true/false to python True/False
            if request.POST.get("lac") == "false":
                lac_upload = False
            else:
                lac_upload = True
            

            # print(recaptcha_response, raw_records, user_ip)

            # if validateRecaptcha(recaptcha_response, user_ip):
            #     # process the records
            #     processRecords(raw_records)
            #     return HttpResponse("1")
            # else:
            #     return HttpResponse("0")

            return_values = processRecords(raw_records, lac_upload)
            
            return(HttpResponse(json.dumps(return_values)))     # success
    
    if request.method == "GET":
        return(render(request, "website/thesisSubmission.html"))
    return HttpResponse("Server Error")

def validateRecaptcha(recaptcha_response, user_ip):

    data = {
        'secret': settings.RECAPTCHA_SECRET,
        'response': recaptcha_response,
        'remoteip': user_ip
    }

    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = r.json()

    if result['success']:
        print("Validation Successful")
        return(True)
    else:
        print(result)
        return(False)


def processRecords(raw_records, lac_upload):
    # convert the string to a "file" but without actually saving on disk
    try:
        records_file = io.BytesIO(raw_records.encode("cp1252"))
    except:
        records_file = io.BytesIO(raw_records.encode("utf-8"))
    
    try:
        response = process(records_file, lac_upload)
    except:
        # there was some type of error processing the file
        return({"status":1, "errors":["Error processing file - Please make sure it is in proper MARC format"], "submissions":[], "total_records": 0})
    
    status = 1      # 1 = recaptcha successful
    errors = response[0]
    submissions = response[1]
    total_records = response[2]

    return_response = {"status":status, "errors":errors, "submissions":submissions, "total_records": total_records}
    # print(return_response)

    return(return_response)

            
