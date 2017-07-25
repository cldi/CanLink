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
import traceback
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

                for enc in ["cp1252", "utf-8"]:
                    try:
                        raw_records = file.decode(enc)
                        break
                    except:
                        continue

                    return(HttpResponse(json.dumps({"status":1, "errors":["Error processing file - Please make sure it is in proper MARC format"], "submissions":[], "total_records": 0})))

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


def processRecords(raw_records, lac_upload, silent_output=False):
    encoding = ""
    for enc in ["cp1252", "utf-8"]:
        try:
            records_file = io.BytesIO(raw_records.encode(enc))
            encoding = enc
            break
        except:
            continue
        # next two lines wouldn't run properly since we don't have the encoding - leave this for later
        # error_file_name = saveErrorFile(raw_records.encode(encoding))
        # submitGithubIssue("Error Finding Encoding", "File: " + error_file_name, "BUG")

    try:
        response = process(records_file, lac_upload, silent_output)
    except Exception as e:
        # save file locally 
        error_file_name = saveErrorFile(raw_records.encode(encoding))
        # submit github issue
        python_stacktrace = traceback.format_exc()
        title = "Error Processing File"
        body = "File: " + error_file_name + "\nPython Stacktrace:\n\n" + python_stacktrace
        label = "BUG"
        submitGithubIssue(title, body, label, silent_output=False)

        # there was some type of error processing the file
        return({"status":1, "errors":["Error processing file - Please make sure it is in proper MARC format"], "submissions":[], "total_records": 0})
    
    status = 1      # 1 = recaptcha successful
    errors = response[0]
    submissions = response[1]
    total_records = response[2]

    return_response = {"status":status, "errors":errors, "submissions":submissions, "total_records": total_records}
    # print(return_response)

    return(return_response)

@csrf_exempt
def updateUri(request):
    if request.method == "POST":
        response = json.loads(request.body.decode('utf-8'))
        # only check for comment creations - not deletions
        if response["action"] == "deleted":
            return HttpResponse(1)

        issue_title = response["issue"]["title"]
        issue = response["issue"]["body"]
        comment = response["comment"]["body"]

        if issue_title == "Missing University URL":
            # take the university name from the issue and not the comment
            # so we don't need to worry about spelling mistakes
            university_name = issue.split("[")[1].split("]")[0].strip()
            university_uri = comment.strip()
            record_file = issue.split("Record File: ")[1].strip()
            print(response)
            
            print(university_name)
            print(university_uri)
            print(record_file)

            # add the new uri to the universities.pickle file
            with open("website/processing/files/testing.pickle", "rb") as handle:
                testing_universities = pickle.load(handle)

            testing_universities[university_name] = university_uri

            with open("website/processing/files/testing.pickle", "wb") as handle:
                pickle.dump(testing_universities, handle, protocol=pickle.HIGHEST_PROTOCOL)
                print("Saved:", university_name, university_uri)

            # reprocess the file
            with open("website/processing/errors/"+record_file, "rb") as error_file:
                data = error_file.read()
                
                for enc in ["cp1252", "utf-8"]:
                    try:
                        raw_records = data.decode(enc)
                        processRecords(raw_records, False, silent_output=True)
                        break
                    except:
                        continue
            print("fixed university")

        elif issue_title == "Missing Degree URL":
            degree_name = issue.split("[")[1].split("]")[0].strip()
            degree_label, degree_uri = comment.split()
            record_file = issue.split("Record File: ")[1].strip()
            
            degree_name = ''.join([i for i in degree_name if i.isalpha()]).lower()
            print(degree_name)
            print(degree_uri)
            print(record_file)
            
            # save the new degree
            with open("website/processing/files/degrees_new.pickle", "rb") as handle:
                testing_degrees = pickle.load(handle)

            # TODO this is a temporary fix for multiple issues with the same missing degree url
            # need to make it so that duplicate universities don't occur
            if degree_name not in testing_degrees:
                testing_degrees[degree_name] = [degree_label, degree_uri]

                with open("website/processing/files/degrees_new.pickle", "wb") as handle:
                    pickle.dump(testing_degrees, handle, protocol=pickle.HIGHEST_PROTOCOL)
                    print("Saved:", degree_name, degree_uri)

             # reprocess the file
            with open("website/processing/errors/"+record_file, "rb") as error_file:
                data = error_file.read()
                
                for enc in ["cp1252", "utf-8"]:
                    try:
                        raw_records = data.decode(enc)
                        processRecords(raw_records, False, silent_output=True)
                        break
                    except:
                        continue

            print("fixed degree")

        return HttpResponse(1)











            
