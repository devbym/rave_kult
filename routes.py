from flask import  current_app as app, render_template, redirect, g,request, render_template_string,jsonify,after_this_request,appcontext_pushed
from datetime import datetime as dt

#Local Import 
from models import Users,Location,Event,EventType,UserRole
from database import sesh


@app.route("/")
def home():
    return render_template("index.html",locations=[loc for loc in Location.query.all()],roles=list(UserRole))

@app.route("/api", methods=["GET", "POST"])
def api():
    if request.method == "POST":
        r = request.form
        print(r)
        new_user = Users(name=r.get("name"),email=r.get("email"),pwd=r.get('pass'),func=None,salt="1234")
        sesh.add(new_user)
        return jsonify(dict(status="OK",request=request.form.items()))

    return jsonify(dict(status="OK"))

@app.route("/api/location",methods=["POST"])
def location():
    if request.method == "POST":
        r = request.form
        print(r)
        new_location = Location(r.get("locationName"),r.get("streetname"),r.get("streetnumber"),r.get("city"),r.get("country"))
        sesh.add(new_location)
        print(f"Location {new_location.name} added!")
        locs = Location.query.all()
        print([loc.name for loc in locs])
        return jsonify(dict(request="OK",data=request.form))

@app.teardown_appcontext
def shutdown_session(exception=None):
    sesh.flush()
    sesh.remove()
