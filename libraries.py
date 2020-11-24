

from flask import request
from flask import Flask, render_template
import requests, json, os

app_token = os.environ.get('APP_TOKEN')
# url = "https://data.austintexas.gov/resource/tc36-hn4j.json?$$app_token=" + app_token
url = "https://data.austintexas.gov/resource/tc36-hn4j.json?$$app_token=0JoiklSJY0REW0qECZAITOz61"
data = requests.get(url=url)
data_json = data.json()
data_list = json.loads(json.dumps(data_json))

application = Flask(__name__)
app = application

global_list = []
wifi = ""
computers = ""
district = ""

@app.route("/static/search_libraries", methods=['POST'])
def get_libraries():
    global wifi
    global computers
    global district
    global global_list

    # Extract all the form fields
    wifi = request.form['wifi']
    computers = request.form['computers']
    district = request.form['district']
    print("Wifi:" + wifi)
    print("Computers:" + computers)
    print("District:" + district)

    # Insert into database.
    if not computers:
        computers = -1
    else:
        computers = int(computers)

    if not district:
        district = -1
    else:
        district = int(district)
    
    if wifi:
        wifi = wifi.lower()
        if wifi == "yes":
            wifi = "Yes"
        elif wifi == "no":
                wifi = "no"

    print("wifi after proccessed is " + wifi)
    
    filtered_list = []

    for library in data_list:
        # get the wifi, computers, district of this library
        currentWifi = library.get('wifi')
        currentComputers = library.get('computers')
        currentDistrict = library.get('district')
        addLibrary = False

        # check for None
        if currentComputers == None:
            currentComputers = -1
        
        currentComputers = int(currentComputers)
        if currentDistrict == None:
            currentDistrict = -1
        
        currentDistrict = int(currentDistrict)

        # if this library matches the search criteria, append it to the new list
        if wifi:
            print("Wifi if")
            if computers >= 0:
                if district > 0:
                    if currentWifi == wifi and currentComputers == computers and currentDistrict == district:
                        print('wifi, computers, district')
                        addLibrary = True
                elif currentWifi == wifi and currentComputers == computers:
                    print('wifi, computers')
                    addLibrary = True
            elif district > 0:
                if currentWifi == wifi and currentDistrict == district:
                    addLibrary = True
            elif currentWifi == wifi:
                print('wifi')
                addLibrary = True
        elif computers >= 0:
            print("computers if")
            if district > 0:
                if currentComputers == computers and currentDistrict == district:
                    addLibrary = True
            elif currentComputers == computers:
                print("Should hit here")
                addLibrary = True
        elif district > 0:
            print("district if")
            if currentDistrict == district:
                addLibrary = True

        if addLibrary:
            filtered_list.append(library)

    # now extract the wanted info from filtered_list
    return_list = []
    for library in filtered_list:
        libraryDict = dict()
        libraryDict["name"] = library.get('name')
        libraryDict["phone"] = library.get('phone')
        libraryDict["human_address"] = library.get('address').get('human_address')
        # added this
        libraryDict["district"] = library.get('district')
        libraryDict["computers"] = library.get('computers')
        libraryDict["wifi"] = library.get('wifi')
        return_list.append(libraryDict)

    global_list = return_list
    return render_template('display_libraries.html')

@app.route("/display_libraries")
def sanity():
    global global_list
    return json.dumps(global_list)


@app.route("/")
def pool_info_website():
    return render_template('index.html')


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')