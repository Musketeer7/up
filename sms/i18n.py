# -*- coding: utf-8 -*-
import csv
import datetime
import re

from django.conf import settings
from django.utils.encoding import force_text
from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from sms import timezone


EPOCH = 226895
PERSIAN_NUMBER = u"۰۱۲۳۴۵۶۷۸۹"
ARABIC_NUMBER = u"٠١٢٣٤٥٦٧٨٩"

PERSIAN_LITERALS = {
    0: u'صفر', 1: u'یک', 2: u'دو', 3: u'سه', 4: u'چهار', 5: u'پنج', 6: u'شش', 7: u'هفت',
    8: u'هشت', 9: u'نه', 10: u'ده', 11: u'یازده', 12: u'دوازده', 13: u'سیزده', 14: u'چهارده',
    15: u'پانزده', 16: u'شانزده', 17: u'هفده', 18: u'هجده', 19: u'نوزده', 20: u'بیست',
    30: u'سی', 40: u'چهل', 50: u'پنجاه', 60: u'شصت', 70: u'هفتاد', 80: u'هشتاد', 90: u'نود',
    100: u'صد', 200: u'دویست', 300: u'سیصد', 400: u'چهارصد', 500: u'پانصد', 600: u'ششصد',
    700: u'هفتصد', 800: u'هشتصد', 900: u'نهصد', 1000: u'هزار', 1000000: u'میلیون',
    1000000000: u'میلیارد'
}

ENGLISH_LITERALS = {
    0: u'Zero', 1: u'One', 2: u'Two', 3: u'Three', 4: u'Four', 5: u'Five', 6: u'Six', 7: u'Seven',
    8: u'Eight', 9: u'Nine', 10: u'Ten', 11: u'Eleven', 12: u'Twelve', 13: u'Thirteen', 14: u'Fourteen',
    15: u'Fifteen', 16: u'Sixteen', 17: u'Seventeen', 18: u'Eighteen', 19: u'Nineteen', 20: u'Twenty',
    30: u'Thirty', 40: u'Forty', 50: u'Fifty', 60: u'Sixty', 70: u'Seventy', 80: u'Eighty', 90: u'Ninety',
    100: u'One Hundred', 200: u'Two Hundred', 300: u'Three Hundred', 400: u'Four Hundred', 500: u'Five Hundred', 600: u'Six Hundred',
    700: u'Seven Hundred', 800: u'Eight Hundred', 900: u'Nine Hundred', 1000: u'Thousand', 1000000: u'Million',
    1000000000: u'billion'
}

PERSIAN_TIME_UNITS = (u'ثانیه', u'دقیقه', u'ساعت', u'روز', u'هفته', u'ماه', u'سال')
ENGLISH_TIME_UNITS = (u'second', u'minute', u'hour', u'day', u'week', u'month', u'year')

PERSIAN_LITERALS_BASES = sorted(PERSIAN_LITERALS.keys(), reverse=True)
ENGLISH_LITERALS_BASES = sorted(ENGLISH_LITERALS.keys(), reverse=True)

PERSIAN_MONTHS = (_("Farvardin") , _("Ordibehesht") , _("Khordad"), \
                _("Tir"), _("Mordad"), _("Shahrivar"), \
                _("Mehr"), _("Aban"), _("Azar"), \
                _("Dey"), _("Bahman"), _("Esfand"))

GREGORIAN_MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

def localize_digits(value, lang=None, symbols=True):
    """

    >>> localize_digits('123.45', lang='fa')
    u'\u06f1\u06f2\u06f3\u066b\u06f4\u06f5'

    >>> localize_digits('123.45', lang='fa', symbols=False)
    u'\u06f1\u06f2\u06f3.\u06f4\u06f5'

    """

    lang = lang or translation.get_language()
    lang = lang.lower()
    if lang[:2] == 'fa':
        return iranian_digits(value, symbols)

    return value

def iranian_digits(value, symbols=True):
    r = u""
    value = u"%s" % value
    for v in value:
        if v <= u"9" and v >= u"0":
            r += PERSIAN_NUMBER[int(v)]
        elif symbols:
            if v == ".":
                r += u"٫"
            elif v == ",":
                r += u"٬"
            elif v == u"%":
                r += u"٪"
            else:
                r += v
        else:
            r += v
    return force_text(r)

def convert_iranian_digits_to_latin(input):
    result = u""
    input = u"%s" % input
    for c in input:
        if c >= PERSIAN_NUMBER[0] and c <= PERSIAN_NUMBER[-1]:
            result += str(int(c) - int(PERSIAN_NUMBER[0])) 
        elif c >= ARABIC_NUMBER[0] and c <= ARABIC_NUMBER[-1]:
            result += str(int(c) - int(ARABIC_NUMBER[0])) 
        elif c == u"٫":
            result += "."
        elif c == u"٬":
            result += ","
        else:
            result += c
    return force_text(result)


def persiandate(year, month, day):
    """Returns a date object corresponding to a specified Persian date."""
    k = EPOCH - 1

    k += 365 * (year - 1)
    k += (8 * year + 21) / 33
    if month <= 7:
        k += 31 * (month - 1)
    else:
        k += 30 * (month - 1) + 6
    k += day
    
    return datetime.date.fromordinal(k)


def topersiandate(date):
    """Returns a tuple of year, month, and day for a specified
    datetime object."""
    if isinstance(date, datetime.datetime):
        date = date.date()
    year = (33 * (date.toordinal() - EPOCH) + 3) / 12053 + 1
    day = (date - persiandate(year, 1, 1)).days
    if day < 216:
        month = day // 31 + 1
        day = day % 31 + 1
    else:
        month = (day-6) // 30 + 1
        day = (day-6) % 30 + 1
    
    return (year, month, day)


def get_start_of_persian_month(year, month, include_time=False, tz_aware=False):
    """
    Returns datetime.date if datetime=False, datetime.datetime with time set
    to 00:00 if include_time=True, and local 00:00 if tz_aware=True.

    >>> get_start_of_persian_month(1393, 3)
    datetime.date(2014, 5, 22)

    >>> get_start_of_persian_month(1393, 3, include_time=True)
    datetime.datetime(2014, 5, 22, 0, 0)

    >>> d = get_start_of_persian_month(1393, 3, include_time=True, tz_aware=True)
    >>> d.date()
    datetime.date(2014, 5, 22)
    >>> d.tzinfo == None
    False

    """
    res = persiandate(year, month, 1)
    if include_time or tz_aware:
        res = datetime.datetime.combine(res, datetime.datetime.min.time())
    if tz_aware:
        res = timezone.make_aware(res, timezone.get_current_timezone())
    return res

def to_literal(value, lang=None, base=False):
    lang = lang or translation.get_language()
    literals = PERSIAN_LITERALS if lang == 'fa' else ENGLISH_LITERALS
    bases = PERSIAN_LITERALS_BASES if lang == 'fa' else ENGLISH_LITERALS_BASES
    if value in literals and value < 1000 or base:
        return literals[value]
    if value > 1000000000000:
        return u'خیلی' if lang == 'fa' else u'Too Large!'

    for base in bases:
        if base <= value:
            break
    s = u''
    if lang == 'fa':
        if (value / base) > 1 or base > 1000:
            s += to_literal(value / base, 'fa')
        s += u' ' + to_literal(base, 'fa', True)
        reminder = value % base
        if reminder > 0:
            s += u' ﻭ '
            s += to_literal(value % base, 'fa')
    else:
        if (value / base) > 1 or base >= 1000:
            s += to_literal(value / base, lang) + ' '
        s += to_literal(base, lang, True)
        reminder = value % base
        if reminder > 0:
            s += (' ' if base >= 1000 and reminder >= 10 else ' and ' if base >= 100 else '-' if base >= 20 else ' ')
            s += to_literal(reminder, lang)

    return s

def detect_language(text):
    """
        >>> detect_language(u'My name is Mehdi (مهدی)')
        'en'
        >>> detect_language(u'\u0621\u0622\u0624')
        'fa'

        # TODO: problem using persian characters directly in doctests
    """
    if not text:
        return "fa"
    fa = 0
    en = 0
    for char in text:
        if char >= u'\u0621' and char < u'\u0700': # persian char
            fa += 1
        elif char >= u'\u0041' and char < u'\u007B': # english char
            en +=1
        if fa + en > 256:
            break;
    return "fa" if fa > en else "en"

ENGLISH_TIME_UNITS = (u'second', u'minute', u'hour', u'day', u'week', u'month', u'year')

def convert_timedelta_to_literal(timedelta, lang=None, include_week=True, include_seconds=True):
    lang = lang or translation.get_language()
    units = PERSIAN_TIME_UNITS if lang == 'fa' else ENGLISH_TIME_UNITS
    and_ = u' و ' if lang == 'fa' else ' and '
    summation = '' if lang == 'fa' else 's'
    result = ''
    d = abs(timedelta).days
    if include_week and d >= 7:
        result = and_ + to_literal(d // 7) + ' ' + units[4] + (summation if d >= 14 else '')
        d = d % 7
    if d > 0:
        result += and_ + to_literal(d) + ' ' + units[3] + (summation if d >= 2 else '')
    s = abs(timedelta).seconds
    if s >= 3600:
        result += and_ + to_literal(s // 3600) + ' ' + units[2] + (summation if s >= 7200 else '')
        s = s % 3600
    if s >= 60:
        result += and_ + to_literal(s // 60) + ' ' + units[1] + (summation if s >= 120 else '')
        s = s % 60
    if s > 0 and include_seconds:
        result += and_ + to_literal(s) + ' ' + units[0] + (summation if s >= 2 else '')
    result = result[len(and_):].lower().capitalize()
    return result

# TODO: move it to middleware.py
class MultiLangMiddleware(object):
    """
    This is a very simple middleware that parses a request
    and decides what translation object to install in the current
    thread context. This allows pages to be dynamically
    translated to the language the user desires (if the language
    is available, of course).
    """

    SUPPORTED = dict(settings.LANGUAGES)

    def process_request(self, request):
        language = None

        if 'lang' in request.POST:
            language = request.POST['lang']
        elif 'l' in request.GET:
            language = request.GET['l'][:2].lower()
        elif 'preferences_lang' in request.COOKIES:
            language = request.COOKIES['settings_lang']

        if (not language) or (language not in MultiLangMiddleware.SUPPORTED):
            language = settings.LANGUAGE_CODE[:2].lower()

        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response


class UnicodeCsvReader(object):
    def __init__(self, f, encoding="utf-8", **kwargs):
        self.csv_reader = csv.reader(f, **kwargs)
        self.encoding = encoding

    def __iter__(self):
        return self

    def next(self):
        # read and split the csv row into fields
        row = self.csv_reader.next()
        # now decode
        return [unicode(cell, self.encoding) for cell in row]

    @property
    def line_num(self):
        return self.csv_reader.line_num


# Replace arabic characters with standard persian characters.

# statistics that are shown in front of every character in comments, are taken in 18 March 2015 from Reviews
kaafs = [u'\u0643', # Arabic kaaf - about 4% usage
          #u'\u063B', # Arabic letter keheh with two dots above - 0% usage
          #u'\u063C', # Arabic letter keheh with three dots below - 0% usage
          u'\u06AA', # Kaf in sindhi - less than 1% usage
          #u'\u06AB', # Pashto - Only one person used this character, does it worth? :))
          #u'\u06AC', # Old malay :D - 0% usage
          #u'\u06AD', # early persian - 0% usage
          #u'\u06AE', # Berber! early persian - 0% usage
          #u'\u0762', # Old malay - Only one person used this character, does it worth? :))
          #u'\u0763', # Moroccan arabic - 0% usage
          #u'\u0764', # Arabic letter keheh with three dots pointing upwards bellow - Only one person used this character, does it worth? :))
          #u'\u077F', # Arabic letter kaf with two dots above - 0% usage
          u'\uFB8E', # Arabic letter keheh isolated form. - less than 1% usage
          u'\uFB8F', # Arabic letter keheh final form - less than 1% usage
          u'\uFB90', # Arabic letter keheh initial form - about 1% usage
          u'\uFB91', # Arabic letter keheh medial form - about 1% usage
          u'\uFED9', # Arabic letter kaf isolated form - less than 1% usage
          u'\uFEDA', # Arabic letter kaf final form - less than 1% usage
          u'\uFEDB', # Arabic letter kaf initial form - about 1% usage
          u'\uFEDC', # Arabic letter kaf medial form - about 1% usage
          ]

# Standard persian keh is: \u06A9
unstandard_kaafs_pattern = '|'.join(kaafs)
unstandard_kaafs_regex = re.compile(unstandard_kaafs_pattern)

yehs = [
        u'\u064A', # Arabic letter yeh - about 8% usage
        #u'\u0620', # Arabic letter kashmiri yeh - 0% usage
        u'\u0626', # Arabic letter yeh with hamza above - about 1% usage
        #u'\u063D', # Arabic letter farsi yeh with inverted v - 0% usage
        #u'\u063E', # Arabic letter farsi yeh with two dots above - 0% usage
        #u'\u063F', # Arabic letter farsi yeh with three dots above - 0% usage
        #u'\u0678', # Arabic letter high hamza yeh - only 6 person used this, does it worth? :-/
        #u'\u06CD', # Arabic letter yeh with tail - only 29 person used this, does it worth? :-/
        #u'\u06CE', # Arabic letter yeh with small V - only 109 person used this, does it worth? :-/
        #u'\u06D0', # Arabic letter E - only 5 person used this, does it worth? :-/
        #u'\u06D1', # Old malay - 0% usage
        u'\u06D2', # Arabic letter yeh barree - less than 1% usage
        #u'\u06D3', # Arabic letter yeh barree with hamza above - only 1 person used this, does it worth? :-/
        #u'\u0775', # Arabic letter farsi yeh with extended arabic-indic digit two above - 0% usage
        #u'\u0776', # Arabic letter farsi yeh with extended arabic-indic digit three above - 0% usage
        #u'\u0777', # Arabic letter farsi yeh with extended arabic-indic digit four below - 0% usage
        #u'\u077A', # Arabic letter yeh barree with extended arabic-indic digit two above - 0% usage
        #u'\u077B', # Arabic letter yeh barree with extended arabic-indic digit three above - 0% usage
        #u'\u08A8', # Arabic letter yeh with two dots below and hamza above - 0% usage
        #u'\u08A9', # Arabic letter yeh with two dots below and dot above - 0% usage
        #u'\uFBAE', # Arabic letter yeh barree isolated form - only 4 person used this, does it worth? :-/
        #u'\uFBAF', # Arabic letter yeh barree final form - only 19 person used this, does it worth? :-/
        #u'\uFBB0', # Arabic letter yeh barree with hamza above isolated form - 0% usage
        #u'\uFBB1', # Arabic letter yeh barree with hamze above final form - only one person used this, does it worth?
        #u'\uFBE4', # Arabic letter E isolated form - 0% usage
        #u'\uFBE5', # Arabic letter E final form - 0% usage
        #u'\uFBE6', # Arabic letter E initial form - 0% usage
        #u'\uFBE7', # Arabic letter E medial form - 0% usage
        u'\uFBFC', # Arabic letter farsi yeh isolated form - less than 1%
        u'\uFBFD', # Arabic letter farsi yeh final form - less than 1%
        u'\uFBFE', # Arabic letter farsi yeh initial form - less than 1%
        u'\uFBFF', # Arabic letter farsi yeh medial form - less than 1%
        u'\uFEF1', # Arabic letter yeh isolated form - less than 1%
        u'\uFEF2', # Arabic letter yeh final form - less than 1%
        u'\uFEF3', # Arabic letter yeh initial form - less than 1%
        u'\uFEF4', # Arabic letter yeh medial form - about 1% usage
        ]
# Standard persian yeh is: \u06CC
unstandard_yehs_pattern = '|'.join(yehs)
unstandard_yehs_regex = re.compile(unstandard_yehs_pattern)

# For better performance re.compile of patterns is outside of method.

def normalize_word(word):
    """
    Convert all kinds of kaaf and yee to standard form.

    Test:
    >>> normalize_word(u'\u064A\u0643\u0628\u0643\u0648')
    u'\u06cc\u06a9\u0628\u06a9\u0648'
    >>> normalize_word(u'\u06cc\u06a9\u0628\u06a9\u0648')
    u'\u06cc\u06a9\u0628\u06a9\u0648'

    """

    word = unstandard_kaafs_regex.sub(u'\u06A9', word)
    word = unstandard_yehs_regex.sub(u'\u06CC', word)

    return word