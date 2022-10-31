import requests
import yaml
import json
import datetime
import flask
from geocodio import GeocodioClient

app = flask.Flask(__name__)

@app.route('/')
def index():
    return "Hello World"

@app.route('/api/getInfo/<name>/<level>/')
def getCandidateInfo(name, level):
    try:
        if level == "federal":
            today = datetime.date.today()
            filename = 'CandidateData/' + today.strftime('%Y-%m-%d') + '.json'

            def accessJSONFile():
                try:
                    with open(filename, 'r') as f:
                        pass
                except:
                    url = 'https://raw.githubusercontent.com/unitedstates/congress-legislators/main/legislators-current.yaml'
                    response = requests.get(url)
                    data = yaml.safe_load(response.text)
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)

            accessJSONFile()

            def getData(name):
                with open(filename, 'r') as f:
                    data = json.load(f)
                    for i in data:
                        if i['name']['official_full'] == name:
                            try:
                                phonenumber =  i['terms'][0]['phone']
                            except:
                                phonenumber = "None"
                            try:
                                opensecrets = i['id']['opensecrets']
                            except:
                                phonenumber = "None"
                            try:
                                address = i['terms'][0]['office']
                            except:
                                address = "None"
                            return phonenumber, opensecrets, address

            legislatorData = getData(name)

            print(legislatorData[0])
            print(legislatorData[1])
            print(legislatorData[2])

            def getOrganizations(cid):
                try:
                    with open('Candidates/Organizations/' + cid + '.json', 'r') as f:
                        pass
                except:
                    url = 'https://www.opensecrets.org/api/?method=candContrib&cid=' + cid + '&cycle=2022&apikey=c5d1d02a93919b2845a095e52c2af67a&output=json'
                    response = requests.get(url)
                    data = response.text
                    jsonData = json.loads(data)
                    orgs = {}
                    for i in jsonData['response']['contributors']['contributor']:
                        org = i['@attributes']['org_name']
                        total = i['@attributes']['total']
                        if int(total) > 0:
                            orgs[org] = total
                        elif int(total) <= 0:
                            pass
                        else:
                            pass
                    with open('Candidates/Organizations/' + cid + '.json', 'w') as f:
                       json.dump(orgs, f, indent=2)

            def getSectors(cid):
                try:
                    with open('Candidates/Sectors/' + cid + '.json', 'r') as f:
                        pass
                except:
                    url = 'https://www.opensecrets.org/api/?method=candSector&cid=' + cid + '&cycle=2022&apikey=c5d1d02a93919b2845a095e52c2af67a&output=json'
                    response = requests.get(url)
                    data = response.text
                    jsonData = json.loads(data)
                    sectors = {}
                    for i in jsonData['response']['sectors']['sector']:
                        sector = i['@attributes']['sector_name']
                        total = i['@attributes']['total']
                        if int(total) > 0:
                            sectors[sector] = total
                        elif int(total) <= 0:
                            pass
                        else:
                            pass
                    with open('Candidates/Sectors/' + cid + '.json', 'w') as f:
                        json.dump(sectors, f, indent=2)

            candidateID = legislatorData[1]
            if candidateID != "None":
                getOrganizations(candidateID)
                getSectors(candidateID)
            else:
                pass

            topsupporters = {}
            topsectors = {}

            def accessFiles(candidateID):
                with open('Candidates/Organizations/' + candidateID + '.json', 'r') as f:
                    organizations = json.load(f)
                    for organization in organizations:
                        topsupporters[organization] = organizations[organization]
                with open('Candidates/Sectors/' + candidateID + '.json', 'r') as f:
                    sectors = json.load(f)
                    for sector in sectors:
                        topsectors[sector] = sectors[sector]
                return topsupporters, topsectors

            if candidateID != "None":
                topinfo = accessFiles(candidateID)
            else:
                pass

            return flask.jsonify(legislatorData[0], legislatorData[1], legislatorData[2], topinfo[0], topinfo[1])

        elif level == "state":
            def checkIfFileExists(name):
                try:
                    nameForSearch = name.replace(" ", "_")
                    with open('StateCandidateData/' + nameForSearch + '.json', 'r') as f:
                        data = json.load(f)
                        return data
                except:
                    def searchName(name):
                        url = "https://api.github.com/search/code?q=filename:{}+repo:openstates/people".format(name)
                        response = requests.get(url)
                        response = response.json()
                        filepath = response["items"][0]["path"]
                        return filepath

                    def getContentsOfFile(filepath):
                       url = "https://raw.githubusercontent.com/openstates/people/master/{}".format(filepath)
                       response = requests.get(url)
                       response = response.text
                       jsonData = yaml.safe_load(response)
                       jsonData = json.dumps(jsonData, indent=2, sort_keys=True, default=str)
                       return jsonData

                    link = searchName(name)
                    data = getContentsOfFile(link)
                    nameForSearch = name.replace(" ", "_")
                    with open('StateCandidateData/' + nameForSearch + '.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    return data

            def getDataFromFile(data):
                data = json.loads(data)
                try:
                    voice = data["offices"][0]["voice"]
                except:
                    voice = "None"
                try:
                    address = data["offices"][0]["address"]
                except:
                    address = "None"
                try:
                    id = data["id"]
                except:
                    id = "None"
                if ';' in address:
                    address = address.split(";")
                    address = address[-2:]
                    address = "".join(address)
                else:
                    pass   
                return voice, address, id

            data = checkIfFileExists(name)
            initialData = getDataFromFile(data)
            return flask.jsonify(initialData)

        else:
            return "Invalid level"
            
    except Exception as e:
        return str(e)

@app.route('/api/getMisconduct/<name>/')
def getRepresenativeMisconduct(name):
    try:
        today = datetime.date.today()
        filename = 'CandidateData/' + today.strftime('%Y-%m-%d') + '.json'
        todayFile = 'Candidates/Misconduct/' + today.strftime('%Y-%m-%d') + '.json'

        def accessJSONFile():
            try:
                with open(filename, 'r') as f:
                    pass
            except:
                url = 'https://raw.githubusercontent.com/unitedstates/congress-legislators/main/legislators-current.yaml'
                response = requests.get(url)
                data = yaml.safe_load(response.text)
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
        accessJSONFile()
        
        def searchCandidateName(name):
            with open(filename, 'r') as f:
                data = json.load(f)
                for i in data:
                    if i['name']['official_full'] == name:
                        return i['id']['govtrack']
                    else:
                        pass

        candidateID = searchCandidateName(name)
        print(candidateID)

        def get_misconduct():
            misconduct_yaml = requests.get("https://raw.githubusercontent.com/govtrack/misconduct/master/misconduct.yaml")
            misconduct_yaml = misconduct_yaml.text
            misconduct = yaml.load(misconduct_yaml, Loader=yaml.FullLoader)
            with open(todayFile, "w+") as json_file:
                json.dump(misconduct, json_file, indent=4, sort_keys=True, default=str)
            return misconduct

        def parse_misconduct():
            try:
                with open(todayFile, "r") as json_file:
                    misconduct = json.load(json_file)
            except:
                misconduct = get_misconduct()

            with open(todayFile, "r") as json_file:
                misconduct = json.load(json_file)

            incidents = []
            for i in range(len(misconduct)):
                if str(misconduct[i]["person"]) == str(candidateID):
                    text = misconduct[i]["text"]
                    allegation = misconduct[i]["allegation"]
                    tags = misconduct[i]["tags"]
                    incidents.append([allegation, text, tags])
            return incidents

        get_misconduct()
        misconduct = parse_misconduct()
        return flask.jsonify(misconduct)

    except:
        return 'Error'

@app.route('/api/getRepresentatives/<lat>/<lon>/')
def getRepresentatives(lat, lon):
    try:
        client = GeocodioClient("f9956323926f2353565a3bf62366fff95353223")
        geocoded_location = client.reverse((lat, lon), fields=["cd"])
        reps = geocoded_location['results'][0]['fields']['congressional_districts'][0]['current_legislators']
        dictionaryofreps = {}
        for rep in reps:
            fullname = rep['bio']['first_name'] + ' ' + rep['bio']['last_name']
            type = rep['type'].title()
            phone = rep['contact']['phone']
            url = rep['contact']['url']
            address = rep['contact']['address']
            dictionaryofreps[fullname] = {'type': type, 'phone': phone, 'url': url, 'address': address}

        print(dictionaryofreps)
        return flask.jsonify(dictionaryofreps)
    except:
        return 'Error'

if __name__ == '__main__':
    app.run()
