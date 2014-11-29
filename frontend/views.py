from flask import g, render_template, flash, redirect, request, url_for, session
from flask.ext.babel import gettext, ngettext, format_date
from frontend import app, logger, babel, ApiException
import requests
from requests import ConnectionError
import operator
import dateutil.parser
import forms
import json
import urllib
from operator import itemgetter
from markupsafe import Markup

API_HOST = app.config['API_HOST']


# handling static files (only relevant during development)
app.static_folder = 'static'
app.add_url_rule('/static/<path:filename>',
                 endpoint='static',
                 view_func=app.send_static_file,
                 subdomain='med-db')


@babel.localeselector
def get_locale():
    # set locale to session if present in get variables
    if request.args.get('locale'):
        if app.config['LANGUAGES'].get(request.args['locale']):
            session['locale'] = request.args['locale']

    # get locale from session cookie
    if session.get('locale'):
        return session['locale']

    # # if a user is logged in, use the locale from the user settings
    # user = getattr(g, 'user', None)
    # if user is not None:
    #     return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits. The best match wins.
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())


@app.template_filter('format_date')
def jinja2_filter_format_date(date_str, format='long'):
    if date_str:
        date = dateutil.parser.parse(date_str)
        native = date.replace(tzinfo=None)
    else:
        return ""
    return format_date(native, format=format)


@app.template_filter('add_commas')
def jinja2_filter_add_commas(quantity):
    out = ""
    quantity_str = str(quantity)
    while len(quantity_str) > 3:
        tmp = quantity_str[-3::]
        out = "," + tmp + out
        quantity_str = quantity_str[0:-3]
    return quantity_str + out


@app.template_filter('urlencode')
def jinja2_filter_urlencode(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.quote_plus(s)
    return Markup(s)


def sort_list(unsorted_list, key):
    """
    Sort a list of dicts by the value found with the key provided.
    """

    return sorted(unsorted_list, key=operator.itemgetter(key))


def load_from_api(resource_name, resource_id=None):

    query_str = resource_name + "/"
    if resource_id:
        query_str += str(resource_id) + "/"

    headers = {}
    if session and session.get('api_key'):
        headers = {'Authorization': 'ApiKey:' + session.get('api_key')}

    try:
        response = requests.get(API_HOST + query_str, headers=headers)
        out = response.json()
        if response.status_code != 200:
            raise ApiException(response.status_code, response.json().get('message', gettext(u"An unspecified error has occurred.")))
        i = 0
        while i < 10:
            i += 1
            if response.json().get('next'):
                response = requests.get(response.json()['next'], headers=headers)
                if response.status_code != 200:
                    raise ApiException(response.status_code, response.json().get('message', gettext(u"An unspecified error has occurred.")))
                out['results'] += response.json()['results']
            else:
                break
        return out

    except ConnectionError:
        flash(gettext(u'Error connecting to backend service.'), 'danger')
        pass
    return


@app.route('/', subdomain='med-db')
def landing():

    recent_updates = load_from_api('recent_updates')
    if recent_updates:
        recent_updates = recent_updates.get('results')

    overview = load_from_api('overview')

    return render_template(
        'index.html',
        API_HOST=API_HOST,
        active_nav_button="home",
        overview=overview,
        recent_updates=recent_updates
    )


@app.route('/medicine-list/', subdomain='med-db')
def medicine_list():

    tmp = load_from_api('active_medicines')
    medicine_list = tmp["result"]
    medicine_list = sorted(medicine_list, key=itemgetter('name'))
    return render_template(
        'medicine_list.html',
        API_HOST=API_HOST,
        medicine_list=medicine_list,
        active_nav_button="medicines"
    )


@app.route('/medicine/<int:medicine_id>/', subdomain='med-db')
def medicine(medicine_id):

    medicine = load_from_api('medicine', medicine_id)

    # find the maximum price, for making comparisons
    max_price = medicine['procurements'][-1]['unit_price_usd']
    if medicine.get('benchmarks'):
        for benchmark in medicine['benchmarks']:
            if benchmark['price'] > max_price:
                max_price = benchmark['price']

    # add procurements and benchmarks to the same list, and sort
    tmp = list(medicine['procurements'])
    if medicine.get('benchmarks'):
        for benchmark in medicine['benchmarks']:
            benchmark['unit_price_usd'] = benchmark['price']
            tmp.append(benchmark)
    procurements_and_benchmarks = sort_list(tmp, 'unit_price_usd')

    # find the best procurements
    best_procurements = medicine['procurements']
    if len(best_procurements) > 5:
        best_procurements = best_procurements[0:5]

    # calculate potential cost difference
    form_args = []
    if request.args.get("compare-quantity") and request.args.get("compare-pack-size") and request.args.get("compare-price"):
        form_args = request.args
        try:
            compare_quantity = int(form_args['compare-quantity'])
            compare_pack_size = int(form_args['compare-pack-size'])
            compare_price = float(form_args['compare-price'])
            compare_unit_price = float(compare_price/compare_pack_size)

            for procurement in best_procurements:
                unit_price = float(procurement['unit_price_usd'])
                procurement['cost_difference'] = (unit_price - compare_unit_price) * compare_quantity * compare_pack_size
        except Exception as e:
            flash(gettext(u"There was a problem with your input."), "warning")
            logger.debug(e)
            pass

    return render_template(
        'medicine.html',
        API_HOST=API_HOST,
        medicine=medicine,
        active_nav_button="medicines",
        max_price = max_price,
        best_procurements = best_procurements,
        procurements_and_benchmarks = procurements_and_benchmarks,
        form_args = form_args,
    )

@app.route('/procurement/<int:procurement_id>/', subdomain='med-db')
def procurement(procurement_id):

    procurement = load_from_api('procurement', procurement_id)
    return render_template(
        'procurement.html',
        API_HOST=API_HOST,
        procurement=procurement,
        active_nav_button="procurement"
    )


@app.route('/country-ranking/', subdomain='med-db')
def country_ranking():

    country_ranking = load_from_api('country_ranking')
    return render_template(
        'country_ranking.html',
        API_HOST=API_HOST,
        country_ranking=country_ranking,
        active_nav_button="reports"
    )


@app.route('/country-report/<string:country_code>/', subdomain='med-db')
def country_report(country_code):

    report = load_from_api('country_report', country_code)
    return render_template(
        'country_report.html',
        API_HOST=API_HOST,
        report=report,
        active_nav_button="reports"
    )


@app.route('/login/', subdomain='med-db', methods=['GET', 'POST'])
def login():

    next = request.args.get('next', None)
    login_form = forms.LoginForm(request.form)
    if request.method == 'POST' and login_form.validate():
        data = json.dumps(request.form)
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(API_HOST + 'login/', data=data, headers=headers)
            if response.status_code == 200:
                user_dict = response.json()
                api_key = user_dict.get('api_key')
                email = user_dict.get('email')
                session['api_key'] = api_key
                session['email'] = email
                if next:
                    return redirect(next)
                return redirect(url_for('landing'))
            elif response.status_code != 400:
                raise ApiException(response.status_code, response.json().get('message', gettext(u"An unspecified error has occurred.")))
            else:
                # incorrect login / password
                flash(response.json()["message"], "danger")
        except ConnectionError:
            flash(gettext(u'Error connecting to backend service.'), 'danger')
            pass
    return render_template(
        'login.html',
        API_HOST=API_HOST,
        form=login_form
    )

@app.route('/logout/', subdomain='med-db', methods=['GET', 'POST'])
def logout():

    session.clear()
    flash(gettext(u"You have been logged out successfully."), "success")
    return redirect(url_for('landing'))

@app.route('/register/', subdomain='med-db', methods=['GET', 'POST'])
def register():

    register_form = forms.RegistrationForm(request.form)
    if request.method == 'POST' and register_form.validate():
        data = json.dumps(request.form)
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(API_HOST + 'register/', data=data, headers=headers)
            if response.status_code != 200:
                raise ApiException(response.status_code, response.json().get('message', gettext(u"An unspecified error has occurred.")))
            user_dict = response.json()
            api_key = user_dict.get('api_key')
            email = user_dict.get('email')
            session['api_key'] = api_key
            session['email'] = email
            flash(gettext(u"Thank you. You have been registered successfully."), "success")
            return redirect(url_for('landing'))
        except ConnectionError:
            flash(gettext(u'Error connecting to backend service.'), 'danger')
            pass

    return render_template(
        'register.html',
        API_HOST=API_HOST,
        form=register_form
    )


@app.route('/change-login/', subdomain='med-db', methods=['GET', 'POST'])
def change_login():

    change_login_form = forms.ChangeLoginForm(request.form)
    if not change_login_form.email.data:
        change_login_form.email.data = session['email']
    if request.method == 'POST' and change_login_form.validate():
        data = json.dumps(request.form)
        headers = {}
        headers['Authorization'] = 'ApiKey:' + session.get('api_key')
        headers["Content-Type"] = "application/json"
        try:
            response = requests.post(API_HOST + 'change-login/', data=data, headers=headers)
            if response.status_code != 200:
                raise ApiException(response.status_code, response.json().get('message', gettext(u"An unspecified error has occurred.")))
            user_dict = response.json()
            api_key = user_dict.get('api_key')
            email = user_dict.get('email')
            session['api_key'] = api_key
            session['email'] = email
            flash(gettext(u"Your details have been updated successfully."), "success")
            return redirect(url_for('landing'))
        except ConnectionError:
            flash(gettext(u'Error connecting to backend service.'), 'danger')
            pass

    return render_template(
        'change_login.html',
        API_HOST=API_HOST,
        form=change_login_form
    )


@app.route('/admin/', subdomain='med-db')
def admin_redirect():
    return redirect(API_HOST + "admin/")


@app.route('/meddb/', subdomain='med-db')
def legacy_redirect():
    return redirect("/", 301)


@app.route('/links/', subdomain='med-db')
def links():

    link_list = [
        ("http://apps.who.int/prequal/", "WHO | Prequalification of Medicines Programme", "WHO webpage for the UN Prequalification Programme for prequalification of product-manufacturing site combinations"),
        ("http://www.who.int/medicines/areas/access/ecofin/en/", "WHO | Medicines Price Information", ""),
        ("http://erc.msh.org/mainpage.cfm?file=1.0.htm&module=DMP&language=English", "MSH | International Drug Price Indicator Guide (IDPIG)", ""),
        ("http://www.haiweb.org/medicineprices/international-medicine-prices-sources.php", "haiweb.org | medicine prices", "HAI Multi Country Price Sources"),
        ("http://www.clintonhealthaccess.org/files/ARV%20Price%20Reduction%20Overview%20%2808.06.09%29.pdf", "CHAI ARV Price List", "The Clinton Foundation HIV/AIDS Initiative (CHAI) - ANTIRETROVIRAL (ARV) PRICE LIST"),
    ]
    return render_template(
        'links.html',
        API_HOST=API_HOST,
        link_list=link_list,
        active_nav_button="links"
    )

@app.route('/tenders/', subdomain='med-db')
def tenders():
    tenders = [
        {
            "country" : "Namibia",
            "organisation" : "Central Medical Stores",
            "type" : "International Tender for Essential Medicines",
            "start_date" : "August 2014",
            "duration" : "2 Year framework",
        },
        {
            "country" : "Madagascar",
            "organisation" : "SALAMA",
            "type" : "International Tender for Essential Medicines and Medical Supplies",
            "start_date" : "November 2014",
            "duration" : "1 Year",
        },
        {
            "country" : "Tanzania",
            "organisation" : "Medical Stores Department (MSD)",
            "type" : "International Tender for Essential Medicines and Medical Supplies",
            "start_date" : "March 2015",
            "duration" : "2 Year framework",
        },
        {
            "country" : "Democratic Republic of Congo (DRC)",
            "organisation" : "FEDECAME",
            "type" : "Limited International Tender for Essential Medicines and Medical Supplies",
            "start_date" : "March 2015",
            "duration" : "1 Year",
        },
        {
            "country" : "Namibia",
            "organisation" : "Central Medical Stores",
            "type" : "International Tender for Anti-Retroviral Medicines",
            "start_date" : "June 2015",
            "duration" : "1 Year (renewable)",
        },
        {
            "country" : "Namibia",
            "organisation" : "Central Medical Stores",
            "type" : "International Tender for Anti-Retroviral Medicines",
            "start_date" : "June 2016",
            "duration" : "2 Year framework",
        },
    ]
        

    return render_template(
        'tenders.html',
        API_HOST=API_HOST,
        tender_schedule=tenders,
        active_nav_button="tenders"
    )

@app.route('/registers/', subdomain='med-db')
def registers():
    registers = [
        ("Angola", "N/A", "#"),
        ("Botswana", "Register", "#"),
        ("DRC", "N/A", ""),
        ("Lesotho", "N/A", "#"),
        ("Madagascar", "N/A", "#"),
        ("Malawi", "N/A", "#"),
        ("Mauritius", "N/A", "#"),
        ("Mozambique", "N/A", "#"),
        ("Namibia", "Register", "http://www.nmrc.com.na/LinkClick424c.pdf?fileticket=ir5cbbaayg8%3d&tabid=677&language=en-US"),
        ("Seychelles", "N/A", "#"),
        ("South Africa", "Regulatory Authority", "http://www.mccza.com/dynamism/default_dynamic.asp?grpID=30&doc=dynamic_generated_page.asp&categID=165&groupID=30"),
        ("Swaziland", "N/A", "#"),
        ("Tanzania", "Register", "http://tfda.or.tz/index.php?option=com_phocadownload&view=category&id=65&Itemid=351"),
        ("Zambia", "Registration Information", "http://www.zamra.co.zm/info"),
        ("Zimbabwe", "Register", "http://www.mcaz.co.zw/index.php/downloads/category/17-registers"),
    ]
        
    return render_template(
        'registers.html',
        API_HOST=API_HOST,
        registers=registers,
        active_nav_button="registers"
    )
