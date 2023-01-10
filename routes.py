from sqlalchemy.exc import IntegrityError
from flask import current_app as app, render_template, request, jsonify, redirect, url_for, flash, session, render_template_string, g, make_response
from datetime import datetime as dt

from sqlalchemy.sql import text


from app import logging

# Local Import
from models import Country, Users, Location, Event, EventType, UserRole, Organisation, City, Badge
from models_dev import User, Address
from database import sesh
import json
from controller import Geo, CountryCode, C2

#sesh.execute("DROP TABLE location")


@app.template_global('preload')
def preload(category: str, path="static/cities.json"):
    with open(path, "r") as fo:
        pre: dict = json.load(fo)
        countries = pre.get("Europe")
    ll = []
    for country in Country.query.all():
        if countries[country.name]:
            cities = countries[country.name]
            for c in cities:
                print(c)
                x = City(c, country)
                sesh.add(x)
    sesh.commit()
    return ll


@ app.template_filter("dtSplit")
def dtSplit(datetime):
    d = dt(datetime).date()
    t = dt(datetime).time()
    return dict(date=d, time=t)


@ app.template_global("NOW")
def now():
    return str(dt.now().date().isoformat())


@ app.template_filter()
def rnd4(n: float):
    return round(n, 4)


@ app.context_processor
def context_processor():
    return dict(
        events=[event for event in Event.query.all()],
        users=Users.getAll()
    )


@ app.route("/")
def home():
    rdata = {"ua": request.environ.get(
        "HTTP_USER_AGENT"), 'host': request.host_url}
    print(rdata)
    return render_template("index.html",
                           eventtypes=EventType.__members__,
                           locations=sesh.query(Location).all(),
                           countries=sesh.query(Country).all(),
                           orgs=Organisation.query.all(),
                           badges=Badge.query.all(),
                           events=sesh.query(Event).all(),
                           footer='',
                           )


# @app.route("/api/<command>", methods=["GET", "POST","PUT"])

@ app.route("/user/<name>", methods=["GET"])
def getUser(name):
    if name is not None:
        user = Users.query.filter_by(name=name).first()
        return jsonify(dict(name=user.name, id=user.id, email=user.email, role=user.role, created=user.created))
    else:
        return jsonify(dict(result="User not found"))


@ app.route("/event/<org>")
def EbyO(org):
    ev = Event.query.filter_by(org=org)
    return render_template_string("<html><body>" +
                                  "<h1>{{org}}</h1><{% for x in ev %}<h1>{{x.name}}</h1><h2> {{x.date|replace('T',' ')}}</h2><h3>{{x.country}}</h3>{% endfor %}</body></html>", org=org, ev=ev)


@ app.route("/user/<id>/<action>", methods=['POST'])
def user(id, action):
    if request.method == "POST":
        r = request.form
        if action == "login":
            user = Users.login(id, form=r)

        new_user = Users(name=r.get("name"),
                         email=r.get("email"),
                         pwd=r.get('pass'),
                         func=None,
                         role=r.get("userrole-select"))
        sesh.add(new_user)
        return jsonify(dict(status="OK", request=request.form.items()))

    return jsonify(dict(status="OK"))


@ app.route("/api/location", methods=["GET", "POST"])
def location():
    if request.method == "GET":
        locs = sesh.query(Location).all()
        return jsonify([(x.name, x.city, x.country, x.events) for x in locs])
    elif request.method == "POST":
        r = request.form
        new_location = Location(name=r.get("locationName"),
                                city=r.get("city"),
                                country=r.get("locationcountry"),
                                x=r.get('x'),
                                y=r.get('y'))
        # streetname=r.get("streetname"), streetnumber=r.get("streetnumber"),
        sesh.add(new_location)
        sesh.commit()
        logging.info(f"Location {new_location.name} added!")
        locs = Location.query.all()
        print([loc.name for loc in locs])
        flash("Location created", "info")
        return redirect(url_for('home'))  # render_template('index.html')


@ app.route("/api/org/<orgname>")
def org(orgname):
    o = Organisation.query.filter_by(name=str(orgname)).first()
    return jsonify(country=o.country)


@ app.route("/city/<code>")
def city(code):
    res = Country.query.filter_by(code=code).first()
    if res:
        cit = {x.name for x in res.cities}
    else:
        cit = ""
    return jsonify(cit)


@app.route("/opt/<tablename>", methods=["GET"])
def opt(tablename, columns=None):
    if request.args.get('t'):
        tbl = tablename
        stmt = text(f"SELECT * FROM {tbl}")
        res = sesh.execute(stmt)
        # print([(x, y) for x, y in res.all()])
        return jsonify(res.all())
        opts = []
        if q:
            for y in q.items():
                res = f"<option value='{y}'>{y.name}</option> "
                opts += res
            print(opts)
            return opts
        else:
            print("No results")
            return None


@app.route("/api/t/loc/<x>/<y>", methods=["GET"])
def testLoc(x, y):
    if not session.get('geo'):
        g = Geo(float(x), float(y))
        session.update(geo=dict(x=g.x, y=g.y, address=g.address))
    else:
        app.logger.info("Session Geo already registered")
        print("Session Geo already registered")
    res = session['geo']
    #logging.info(f"X:{res.x} , Y:{res.y}")
    return jsonify(res)


@ app.route("/api/event", methods=["POST"])
def event():
    r = dict(request.form)
    print(request.origin, request.base_url, request.host, request.user_agent)
    try:
        bds = r.get('eventbadges')
        print(bds)
        if Badge.query.filter_by(id=bds).first():
            new = Event.add(r)
            new.badges.append(Badge.query.filter_by(id=bds).first())
            sesh.add(new)
            sesh.commit()
            logging.info(f"Event {new.name}")
            res = make_response(render_template("index.html"), 201)
            res.content_location = f"api/event/{new.name}"
            res.location = request.base_url
            res.autocorrect_location_header = True
            return res
        else:
            return render_template("index.html")
            # new = Event()
            pass
    except Exception:
        raise

        # pay = Badge(name="Cash Only", icon="💰")
        # sesh.add(pay)
        # print(list(sesh.query(Event).filter_by(name=ev['name'])))
    # res.autocorrect_location_header = True


@ app.route("/api/organisation", methods=["POST"])
def organisation():
    if request.headers.get("Referer"):
        origin = request.headers.get("Referer").split("/")[-1]
        print(origin)
        if origin == "":
            origin = "  "
    r = request.form
    # ref = request.referrer
    # ori = request.origin
    # print(ref,ori)
    if r.get('country'):
        result = Country.query.filter_by(name=r['country'])
        print(result)
        if not result:
            print("No country found")
            country = Country(r.get("country"), code=None)
            #logging.info(f"Country {country.name} created")
#            return jsonify(request.form),201
        else:
            country = result.first()
            print(country)
            print("Country exists")
        new = Organisation(name=r.get("orgname"),
                           country=r.get("country"), city=r.get("city"))
        sesh.add(new)
        logging.info(f"Org {new.name} added!")
        sesh.commit()
        res = make_response(render_template("index.html"), 201)
        res.headers['Location'] = f"api/event/{new.name}"
        return redirect(request.origin)
        #   sesh.flush(new)

    return redirect(url_for("home"))
    # ctr = Country(name=,abbrev=[:2])
    # cty = City(name="Prague",country=ctr)
    # return jsonify(r)


@ app.route("/about")
def about():
    return render_template("about.html")


@ app.route("/admin", methods=["GET"])
def adminpage():
    ctx = context_processor()
    return render_template("admin.html", users=Users.query.all(), roles=UserRole.members())


@ app.teardown_appcontext
def shutdown_session(exception=None):
    sesh.flush()
    sesh.remove()
