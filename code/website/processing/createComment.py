import traceback
import requests

def createComment(issue_number, body):
    try:
        # access_token = os.environ.get("GITHUB_TOKEN")
        access_token = "9662588fdf84525ca3372486ac73d0c8137d4a59"
        r = requests.post("https://api.github.com/repos/maharshmellow/CanLink_website/issues/"+str(issue_number)+"/comments?access_token=" + access_token, json = {"body":body.strip()})
        # r = requests.post("https://api.github.com/repos/cldi/CanLink/issues?access_token=" + access_token,
                    # json = {"title":title.strip(), "body":body.strip(), "labels":[label.strip()]})
        print(r.text)
    except Exception as e:
        print(traceback.format_exc())

def closeIssue(issue_number):
    try:
        # access_token = os.environ.get("GITHUB_TOKEN")
        access_token = "9662588fdf84525ca3372486ac73d0c8137d4a59"
        r = requests.patch("https://api.github.com/repos/maharshmellow/CanLink_website/issues/"+str(issue_number)+"?access_token=" + access_token, json = {"state":"closed"})
        # r = requests.post("https://api.github.com/repos/cldi/CanLink/issues?access_token=" + access_token,
                    # json = {"title":title.strip(), "body":body.strip(), "labels":[label.strip()]})
        print(r.text)
    except Exception as e:
        print(traceback.format_exc())



# createComment(100, "> The record has been updated with this information.\n> Closing Issue")
closeIssue(99)