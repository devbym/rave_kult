window.addEventListener('load', (ev) => {
    var g;
    console.log('User Geo approval granted');
    g = getGeo(ev)
});


function getGeo(ev) {
    const GeoOptions = {
        enableHighAccuracy: true,
        timeout: 3000,
        maximumAge: 0
    }
    navigator.geolocation.getCurrentPosition(position => {
        const { latitude, longitude } = position.coords
        x = Number(latitude).toPrecision(6)
        y = Number(longitude).toPrecision(6)
        postGeo(x, y)
    }, err => {
        console.warn(`ERROR(${err.code}): ${err.message}`)
    }, GeoOptions)
}


function postGeo(x, y) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/api/t/loc/" + x + "/" + y, true);
    xhttp.send();
    xhttp.onreadystatechange = function (calls) {
        if (this.readyState == 4 && this.status == 200) {
            geo = JSON.parse(this.response);
            geo.addr = geo.addr.split(",")
            //console.log("Coords", geo)
            setGeo(geo.x, geo.y, geo.addr)
            //makeMap(geo.x,geo.y)
        }
    }
};

function setGeo(x, y, addr) {
    document.getElementById("locX").value = x;
    document.getElementById("locY").value = y;
    document.getElementById("geoAddress").innerHTML = addr;
    document.getElementById("userCountry").innerHTML = addr[5];
    document.getElementById("userCity").innerHTML = addr[3];
}

// END Geo

// Start ElementFill



function getData(inputElem, outputElem, route = 'org') {
    var inp = document.getElementById(inputElem).value;
    var out = document.getElementById(outputElem);
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            out.value = JSON.parse(this.response).data;
        }
    }
    xhttp.open("GET", "/api/" + route + "/" + inp, true);
    xhttp.send();
}

function DT(obj_id) {
    let d = new Date().toISOString();
    let elem = document.getElementsByName(obj_id);
    elem.value = obj_id;
}

const a = function (selectObjInput, selectObjOutput) {

};




function countryChange(country, city) {
    var idx = country.selectedIndex;
    var which = country.options[idx].value;

    // use the selected option value to retrieve the list of items from the countryLists array
    // get the country select element via its known id
    var cSelect = document.getElementById(city);
    // cSelect.style.display = "block"
    // remove the current options from the country select
    while (cSelect.options.length > 0) {
        cSelect.remove(0);
    }
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            //console.log(this.response)
            res = JSON.parse(this.response);
            for (c in res) {
                val = String(res[c]).trim()
                cSelect.add(new Option(val, val))
            }
        }
    }
    xhttp.open("GET", "/city/" + which, true);
    xhttp.send();


};
const setLabel = function (elem, value) {
    var lbl = document.createElement('label');
    lbl.innerHTML = value;
    elem.firstElementChild.replaceWith(lbl)
}



var currentTab = 0; // Current tab is set to be the first tab (0)
showTab(currentTab); // Display the current tab

function showTab(n) {
    var x = document.getElementsByClassName("formtab");
    x[n].style.display = "block";
    if (n == 0) {
        document.getElementById("prevBtn").style.display = "none";
    } else {
        document.getElementById("prevBtn").style.display = "inline";
    }
    if (n == (x.length - 1)) {
        document.getElementById("nextBtn").value = "Submit";
    } else {
        document.getElementById("nextBtn").value = "Next";
    }
    fixStepIndicator(n)
}

function nextPrev(n) {
    var x = document.getElementsByClassName("formtab");
    if (n == 1 && !validateForm()) return false;
    x[currentTab].style.display = "none";
    currentTab = currentTab + n;
    if (currentTab >= x.length) {
        document.getElementById("locationForm").submit();
        return false;
    }
    showTab(currentTab);
}

function validateForm() {
    var x, y, i, valid = true;
    x = document.getElementsByClassName("formtab");
    y = x[currentTab].getElementsByTagName("input");
    for (i = 0; i < y.length; i++) {
        if (y[i].value == "") {
            y[i].className += " invalid";
            valid = false;
        }
    }
    if (valid) {
        document.getElementsByClassName("step")[currentTab].className += " finish";
    }
    return valid;
}

function fixStepIndicator(n) {
    var i, x = document.getElementsByClassName("step");
    for (i = 0; i < x.length; i++) {
        x[i].className = x[i].className.replace(" active", "");
    }
    x[n].className += " active";
}



function displayOnChecked(eventID, targetID) {
    var check = document.getElementById(eventID);
    var trg = document.getElementById(targetID);
    if (check.checked) {
        check.firstElementChild.replaceWith()
        trg.style.display = "block";
        check.style.display = "none";
        setLabel(check, "Free party")
    } else {
        trg.style.display = "none";
        check.style.display = "block";
        setLabel(check, "Price in &euro;")

    }
}

