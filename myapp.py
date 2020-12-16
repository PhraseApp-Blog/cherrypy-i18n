import cherrypy
import os
import glob
import json
import datetime
from jinja2 import Environment, FileSystemLoader
from babel.dates import format_date, format_datetime, get_timezone
from babel.numbers import format_number
from babel.plural import PluralRule

# initialization
env = Environment(loader=FileSystemLoader('templates'))

app_language = 'en_US'
languages = {}
tz = get_timezone('Asia/Singapore')
plural_rule = PluralRule({'one': 'n in 0..1'})

# dynamic loading of language files using glob
language_list = glob.glob("languages/*.json")
for lang in language_list:
    filename = lang.split('\\')
    lang_code = filename[1].split('.')[0]

    with open(lang, 'r', encoding='utf8') as file:
        languages[lang_code] = json.load(file)


# functions for custom filters
def plural_formatting(key_value, input, lang):
    key = ''
    for i in languages[lang]:
        if(key_value == languages[lang][i]):
            key = i
            break

    if not key:
        return key_value

    plural_key = f"{key}_plural"

    if(plural_rule(input) != 'one' and plural_key in languages[lang]):
        key = plural_key

    return languages[lang][key]


def number_formatting(input, lang):
    return format_number(input, locale=lang)


def date_formatting(input, lang):
    # format_datetime(datetime.datetime.now(), tzinfo=tz, format='full', locale=lang)
    return format_date(input, format='full', locale=lang)


# assigning the corresponding function to Jinja2 filters
env.filters['plural_formatting'] = plural_formatting
env.filters['number_formatting'] = number_formatting
env.filters['date_formatting'] = date_formatting


# main class
class FoodBlog(object):
    @cherrypy.expose
    def index(self):
        return "Hello world!"

    @cherrypy.expose(['über_uns', '关于我们'])  # set aliases
    def about_us(self, lang=app_language):
        if(lang not in languages):
            lang = app_language

        template = env.get_template('index.html')
        return template.render(**languages[lang], locale=lang, last_updated_value=datetime.datetime.now(), customer_value=25)


if __name__ == '__main__':
    # configurations
    conf = {
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
        }
    }
    cherrypy.quickstart(FoodBlog(), '/', conf)
