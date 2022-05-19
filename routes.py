from flask import  current_app as app, render_template, redirect, g,request, render_template_string,jsonify,after_this_request,appcontext_pushed
from datetime import datetime as dt

#Local Import 
from models import Users,Location,Event,EventType,UserRole
from database import sesh


@app.route("/")
def home():
    return render_template("index.html",locations=[loc for loc in Location.query.all()],roles=list(UserRole))


