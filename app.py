import requests
import yaml
import json
import datetime
import flask

app = flask.Flask(__name__)

@app.route('/')
def index():
    return "Hello World"

@app.route('/api/getInfo/<name>/')
def getCandidateInfo(name):
    try:
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
                            address = i['terms'][0]['address']
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
                    data = json.load(f)
                    return data
            except:
                url = 'https://www.opensecrets.org/api/?method=candContrib&cid=' + cid + '&cycle=2022&apikey=c5d1d02a93919b2845a095e52c2af67a&output=json'
                response = requests.get(url)
                data = response.text
                jsonData = json.loads(data)
                orgs = {}
                for i in jsonData['response']['contributors']['contributor']:
                    org = i['@attributes']['org_name']
                    total = i['@attributes']['total']
                    orgs[org] = total
                with open('Candidates/Organizations/' + cid + '.json', 'w') as f:
                   json.dump(orgs, f, indent=2)
                return orgs

        def getSectors(cid):
            try:
                with open('Candidates/Sectors/' + cid + '.json', 'r') as f:
                    data = json.load(f)
                    return data
            except:
                url = 'https://www.opensecrets.org/api/?method=candSector&cid=' + cid + '&cycle=2022&apikey=c5d1d02a93919b2845a095e52c2af67a&output=json'
                response = requests.get(url)
                data = response.text
                jsonData = json.loads(data)
                sectors = {}
                for i in jsonData['response']['sectors']['sector']:
                    sector = i['@attributes']['sector_name']
                    total = i['@attributes']['total']
                    sectors[sector] = total
                with open('Candidates/Sectors/' + cid + '.json', 'w') as f:
                    json.dump(sectors, f, indent=2)
                return sectors

        candidateID = legislatorData[1]

        topsupporters = getOrganizations(candidateID)
        print(topsupporters)

        topsectors = getSectors(candidateID)
        print(topsectors)

        return flask.jsonify(legislatorData[0], legislatorData[1], legislatorData[2], topsupporters, topsectors)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run()
