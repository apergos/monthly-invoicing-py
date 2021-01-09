#!/usr/bin/python3
'''
write an invoice based on config to
pdf, with optional logo
'''
import getopt
import os
import sys
import time
import calendar
import datetime
import yaml
from fpdf import FPDF


class PDF(FPDF):
    '''
    subclass with invoice header, footer
    and some methods to set text, draw and
    fill colors based on config
    '''
    def __init__(self, config):
        self.config = config
        super().__init__()
        self.add_font('DejaVu', '', '/usr/share/fonts/dejavu/DejaVuSerif.ttf', uni=True)
        self.add_font('DejaVu', 'B', '/usr/share/fonts/dejavu/DejaVuSerif-Bold.ttf', uni=True)
        self.add_fonts_from_config()
        self.left_margin = 8

    def add_fonts_from_config(self):
        '''
        we are doing unicode fonts now. explicitly add them if specified
        in the template
        '''
        if 'sans_font' in self.config['app_config']:
            if 'sans_font_path' in self.config['app_config']:
                self.add_font(self.config['app_config']['sans_font'], '',
                              self.config['app_config']['sans_font_path'], uni=True)
            if 'sans_font_bold_path' in self.config['app_config']:
                self.add_font(self.config['app_config']['sans_font'], 'B',
                              self.config['app_config']['sans_font_bold_path'], uni=True)
            if 'sans_font_bolditalic_path' in self.config['app_config']:
                self.add_font(self.config['app_config']['sans_font'], 'BI',
                              self.config['app_config']['sans_fontitalic_bold_path'], uni=True)
        if 'serif_font' in self.config['app_config']:
            if 'serif_font_path' in self.config['app_config']:
                self.add_font(self.config['app_config']['serif_font'], '',
                              self.config['app_config']['serif_font_path'], uni=True)
            if 'serif_font_bold_path' in self.config['app_config']:
                self.add_font(self.config['app_config']['serif_font'], 'B',
                              self.config['app_config']['serif_font_bold_path'], uni=True)

    def dark_text(self):
        '''
        set the text color to the dark color per config
        '''
        self.set_text_color(
            self.config['colors']['color_dark']['r'],
            self.config['colors']['color_dark']['g'],
            self.config['colors']['color_dark']['b'])

    def light_text(self):
        '''
        set the text color to the light color per config
        '''
        self.set_text_color(
            self.config['colors']['color_light']['r'],
            self.config['colors']['color_light']['g'],
            self.config['colors']['color_light']['b'])

    def dark_draw_color(self):
        '''
        set the draw color to the dark color per config
        '''
        self.set_draw_color(
            self.config['colors']['color_dark']['r'],
            self.config['colors']['color_dark']['g'],
            self.config['colors']['color_dark']['b'])

    def light_fill_color(self):
        '''
        set the fill color to the light color per config
        '''
        self.set_fill_color(
            self.config['colors']['color_light']['r'],
            self.config['colors']['color_light']['g'],
            self.config['colors']['color_light']['b'])

    def black_text(self):
        '''
        set the text color to black
        '''
        self.set_text_color(0, 0, 0)

    def white_text(self):
        '''
        set the text color to white
        '''
        self.set_text_color(255, 255, 255)

    def serif(self, fontsize):
        '''
        set the font to plain serif of the specified size
        '''
        self.set_font(self.config['app_config']['serif_font'], "", fontsize)

    def bold_serif(self, fontsize):
        '''
        set the font to bold serif of the specified size
        '''
        self.set_font(self.config['app_config']['serif_font'], "B", fontsize)

    def content_cell(self, width, height, text):
        '''
        write a filled framed cell with right aligned text
        which is what we want for most content cells in the
        invoice tables
        '''
        self.cell(width, height, text, border=1, align="R", fill=True)

    def content_cell_left(self, width, height, text):
        '''
        write a filled framed cell with left aligned text
        which a few content cells need
        '''
        self.cell(width, height, text, border=1, fill=True)

    def header_cell(self, width, height, text):
        '''
        write a filled framed cell with centered text
        which is what we want for most header cells in the
        invoice tables
        '''
        self.cell(width, height, text, border=1, align="C", fill=True)

    def blank_cell(self, width, height):
        '''
        write a transparent borderless cell with no text, which is the
        default for all the args except of course for the empty
        text string
        '''
        # self.cell(width, height, "", align="C", fill=True)
        self.cell(width, height, "")

    def get_invoice_date(self):
        '''
        from the bill date, figure out the invoice date, which is
        in the format "Monthname daynum, Year"
        '''
        year, month, last_day = self.config['billdate'].split('-')
        month = int(month)
        month_name = calendar.month_name[month]
        last_day = int(last_day)
        return "{name} {day}, {year}".format(name=month_name, day=last_day, year=year)

    def get_invoice_number(self):
        '''
        from the bill date, figure out the invoice number, which is
        in the format "MonthabbrevDaynumYear"
        '''
        year, month, last_day = self.config['billdate'].split('-')
        month = int(month)
        month_name = calendar.month_name[month]
        last_day = int(last_day)
        return "{name}{day}{year}".format(name=month_name[0:3], day=last_day, year=year)

    def header(self):
        '''
        Display at top of the invoice:
        logo if any, biller name and address, invoice number and date,
        divider line to separate the header from the body of the invoice
        '''
        # logo
        self.image(self.config['business']['image_file'], 0, 10, 100, 0, '', '')

        # Right side
        # "Invoice"
        right_x = 140
        self.set_font(self.config['app_config']['sans_font'], "BI", 28)
        self.set_xy(right_x, 30)
        self.dark_text()
        self.cell(40, 0, "Invoice")

        # Rest of right side
        self.serif(10)
        # "Date"
        self.set_xy(right_x, 40)
        self.dark_text()
        self.cell(20, 0, "Date:")
        self.light_text()
        self.cell(20, 0, self.get_invoice_date())
        # "Invoice Number"
        self.set_xy(right_x, 45)
        self.dark_text()
        self.cell(20, 0, "Invoice #:")
        self.light_text()
        self.cell(20, 0, self.get_invoice_number())

        # Left side
        self.dark_text()
        # Biller Name
        self.bold_serif(14)
        self.set_xy(self.left_margin, 40)
        self.cell(40, 0, self.config['business']['person'])
        # Biller Address
        self.serif(9)
        self.set_xy(self.left_margin, 45)
        self.cell(40, 0, self.config['business']['address'])

        # Divider line
        self.ln(10)
        self.dark_draw_color()
        self.line(self.left_margin, 50, 200, 50)

    def footer(self):
        '''
        Display at bottom of the invoice:
        divider line to separate footer from body of the invoice,
        company name, date invoice generated
        '''
        # Divider line
        self.ln(10)
        self.dark_draw_color()
        self.line(self.left_margin, 275, 200, 275)

        # Text
        self.bold_serif(10)

        # Left side
        # company name
        self.set_xy(self.left_margin, 280)
        self.dark_text()
        self.cell(127, 0, self.config['business']['name'])

        # Right side
        # invoice generation date
        self.light_text()
        self.cell(40, 0, "Generated: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))


def usage(message=None):
    '''
    display a helpful usage message with
    an optional introductory message first
    '''
    if message is not None:
        sys.stderr.write(message)
        sys.stderr.write("\n")
    usage_message = """
Usage: python3 generate_pdf.py --values <path> --template <path>

This script generates an invoice in pdf format based on the values
and template specified.

bill:payment_terms should be set to one of Net 30|60|90|120|180;
default value if omitted is Net 30

--values     (-v):  path to yaml file with the values to shove into the template
--template   (-t):  path to template file
--help       (-h):  display this help message
"""
    sys.stderr.write(usage_message)
    sys.exit(1)


def remove_off(work_days, week_start, week_end, off_days):
    '''given a list of days off for a month,
    see if any of them fall in the week_start/end range and
    if so, decrement work_days appropriately,
    then return the result'''
    for day in off_days:
        if week_start <= day <= week_end:
            work_days = work_days - 1
    return work_days


def get_week_info(year, month, off):
    '''return a list of start and end days for each week, plus
    the number of workdays (filtered for the off days list supplied)'''
    week_info = []
    week_start_date = 1
    # find the day of the week of the 1st of the month and
    # the number of days in the month
    week_start_day, month_end = calendar.monthrange(year, month)
    # week starts monday = 0, ends Sunday = 6
    # we want sunday = 1 and saturday = 7
    week_start_day = (week_start_day + 1) % 7 + 1

    week_difference = 7 - week_start_day
    week_end_date = week_start_date + week_difference
    if week_difference == 6:
        work_days = 5
    else:
        work_days = week_difference
    work_days = remove_off(work_days, week_start_date, week_end_date, off)

    while True:
        work_hours = work_days * 8
        week_info.append((week_start_date, week_end_date, work_days, work_hours))
        week_start_date = week_end_date + 1
        if week_start_date > month_end:
            break
        if month_end - week_start_date >= 6:
            week_end_date = week_start_date + 6
            work_days = 5
        else:
            week_end_date = month_end
            work_days = month_end - week_start_date
        work_days = remove_off(work_days, week_start_date, week_end_date, off)
    return week_info


def not_weekend(day, month, year):
    '''return True if the day is not a Sat/Sun, False otherwise'''
    weekday = datetime.date(year, month, day).weekday()
    if weekday in [5, 6]:
        return False
    return True


def fillin_billable(week_info, rate, month, currency_marker):
    '''
    given week start and end and hours, the billing rate and the month,
    put together a basic billable item and return it
    '''
    billable = {}
    billable['description'] = 'Week of {month} {start} - {end}'.format(
        month=calendar.month_name[month], start=week_info[0], end=week_info[1])
    billable['rate'] = str(rate)
    billable['hours'] = str(week_info[3])
    # printable format for the rate
    billable['rate'] = currency_marker + ' ' + billable['rate']
    # add the line item cost
    cost = convert_money(billable['rate']) * int(billable['hours'])
    billable['cost'] = currency_marker + ' ' + format_money(cost)
    return billable


def get_billables(values, billdate, currency_marker):
    '''
    given a set of values for an invoice, and a billdate,
    generate a dict of billables from these values
    and return it
    '''
    if 'off_days' in values[billdate]:
        off = values[billdate]['off_days']
    else:
        off = []
    year, month, _unused = billdate.split('-')
    year = int(year)
    month = int(month)
    off = [day for day in off if not_weekend(day, month, year)]
    weeks = get_week_info(year, month, off)
    billables = {'billables':
                 [fillin_billable(week, values[billdate]['rate'], month, currency_marker)
                  for week in weeks if week[3] > 0]}
    return billables


def get_currency_marker(config):
    '''
    we may have an incompete config with values yet to be filled in
    but get the currency marker or its default and return it
    '''
    if 'currency_marker' not in config:
        return '$'
    return config['currency_marker']


def get_yaml_config(template, valuesfile):
    '''
    given template and a tiny set of values for one or
    more invoices,
    generate a yaml config with settings for each invoice
    and return it
    '''
    with open(template, "r") as fhandle:
        text = fhandle.read()
    with open(valuesfile, "r") as fhandle:
        contents = fhandle.read()
        values = yaml.safe_load(contents)

    config = []

    # fake fill in the template so we can get the currency marker
    # from the template; we need it to format the rates and costs
    # in each billable item
    fake_completed_text = text % {
        "BILLDATE": "JUNK",
        "WORK": "",
        "BILLABLES": ""
        }
    currency_marker = get_currency_marker(yaml.safe_load(fake_completed_text))

    for billdate in values:
        work = {'work_done': values[billdate]['work_done']}

        billables = get_billables(values, billdate, currency_marker)

        completed_text = text % {
            "BILLDATE": billdate,
            "WORK": yaml.dump(work),
            "BILLABLES": yaml.dump(billables)
        }
        config.append(yaml.safe_load(completed_text))

    return config


def is_date(maybedate):
    '''check that the arg passed in is in the form YYYY-MM-DD'''
    fields = maybedate.split('-')
    if len(fields) != 3:
        return False
    for field in fields:
        if not field.isdigit():
            return False
    if len(fields[0]) != 4 or len(fields[1]) != 2 or len(fields[2]) != 2:
        return False
    if fields[1] < 1 or fields[1] > 12 or fields[2] < 1 or fields[1] > 31:
        return False
    return True


def get_args():
    '''get and validate command-line args'''
    template = None
    valuesfile = None
    try:
        (options, remainder) = getopt.gnu_getopt(
            sys.argv[1:], "t:v:h",
            ["template=", "values=", "help"])
    except getopt.GetoptError as err:
        usage("Unknown option specified: " + str(err))

    for (opt, val) in options:
        if opt in ["-t", "--template"]:
            template = val
        elif opt in ["-v", "--values"]:
            valuesfile = val
        elif opt in ["-h", "--help"]:
            usage("Help for this script")

    if not template or not valuesfile:
        usage("One of the mandatory arguments 'template' or 'values' was not specified")

    if remainder:
        usage("Unknown option(s) specified: %s" % remainder[0])

    if not os.path.exists(template):
        usage("No such file: " + template)
    if not os.path.exists(valuesfile):
        usage("No such file: " + valuesfile)

    return template, valuesfile


def set_due_date(config):
    '''
    Determine the due date based on the Net 30|60|90|120|180 terms
    with default Net 30, and all other payment term strings causing
    an error
    Return the new updated config
    '''
    if 'payment_terms' not in config['bill']:
        # default. FIXME document this.
        config['bill']['payment_terms'] = 'Net 30'
    fields = config['bill']['payment_terms'].split()
    if (fields[0] not in ['net', 'Net'] or not fields[1].isdigit() or
            fields[1] not in ["30", "60", "90", "120", "180"]):
        sys.stderr.write("Bad payment terms: " + config['bill']['payment_terms'] + "\n")
        sys.exit(1)

    config['bill']['due_date'] = get_n_months_later(config['billdate'], int(fields[1]))
    return config


def get_n_months_later(date, count):
    '''given a date in YYYY-MM-DD format, return
    a date count months later in format YYYY/MM/DD'''
    year, month, day = date.split('-')
    old_date = datetime.date(int(year), int(month), int(day))
    new_date = old_date + datetime.timedelta(days=count)
    return new_date.strftime("%Y/%m/%d")


def check_missing_settings(stanza, settings, config):
    '''whine if any of the settings is missing from the stanza'''
    if stanza:
        for setting in settings:
            if setting not in config[stanza]:
                sys.stderr.write("Config ' + stanza + 'stanza is missing mandatory setting "
                                 + setting + "\n")
                return False
        return True

    for setting in settings:
        if setting not in config:
            sys.stderr.write("Config entry is missing mandatory setting "
                             + setting + "\n")
            return False
    return True


def validate_config(config):
    '''check some fields in the yaml config'''
    required_sections = ['business', 'bill_to', 'bill', 'work_done', 'billables']
    for section in required_sections:
        if section not in config:
            sys.stderr.write("Config is missing mandatory stanza " + section + "\n")
            return False

    settings = ['name', 'person', 'address']
    okay = check_missing_settings('business', settings, config)
    settings = ['email', 'name', 'street', 'city_state_zip', 'country']
    result = check_missing_settings('bill_to', settings, config)
    okay = okay and result
    settings = ['department', 'currency', 'payment_terms', 'due_date']
    result = check_missing_settings('bill', settings, config)
    okay = okay and result
    if not okay:
        return False
    settings = ['description', 'hours', 'rate']
    for item in config['billables']:
        result = check_missing_settings(None, settings, item)
        okay = okay and result

    if 'image_file' in config['business'] and not os.path.exists(config['business']['image_file']):
        sys.stderr.write("No such image file " + config['business']['image_file'] + "\n")
        return False
    return True


def add_config_defaults(config):
    '''add some defaults where we can'''
    config['currency_marker'] = get_currency_marker(config)
    if 'currency_marker' not in config:
        config['currency_marker'] = '$'

    if 'tax_details' not in config:
        config['tax_details'] = {}
    if 'tax_name' not in config['tax_details']:
        config['tax_details']['tax_name'] = 'Tax'
    if 'default_percentage' not in config['tax_details']:
        config['tax_details']['default_percentage'] = 0

    if 'app_config' not in config:
        config['app_config'] = {}
    if 'output_dir' not in config['app_config']:
        config['app_config']['output_dir'] = './billed'
    if 'sans_font' not in config['app_config']:
        config['app_config']['sans_font'] = "Helvetica"
    if 'serif_font' not in config['app_config']:
        # config['app_config']['serif_font'] = "Times"
        config['app_config']['serif_font'] = "DejaVu"

    if 'colors' not in config:
        config['colors'] = {}
    if 'color_light' not in config['colors']:
        config['colors']['color_light'] = {'r': 117, 'g': 180, 'b': 209}
    if 'color_light' not in config['colors']:
        config['colors']['color_dark'] = {'r': 16, 'g': 46, 'b': 95}

    return config


def convert_money(value):
    '''
    skip leading non-digits if any (might be currency marker and
    following spaces), take the resultant decimal string,
    convert it to the corresponding integer multiplied by 100,
    and return that

    this lets us work with monetary values as ints; they can be
    formatted back to money for printing
    '''
    while not value[0].isdigit():
        value = value[1:]
    if not value:
        return 0

    if '.' in value:
        base, decimal = value.split('.')
        return int(base) * 100 + int(decimal[0]) * 10 + int(decimal[1])
    return int(base) * 100


def format_money(value):
    '''
    convert a number of cents (int) to a string with a decimal point
    suitable for printing
    '''
    base = int(value / 100)
    decimal = value % 100
    if decimal == 0:
        padding = "0"
    else:
        padding = ""
    return "{base}.{dec}{pad}".format(base=base, dec=decimal, pad=padding)


def draw_unframed_list(pdf, header, values, left_cols, rect=False):
    '''
    given a list of values, write them one after another,
    optionally shifted right by "left_cols" amount of mm

    a header will be drawn above the list if specified

    a rectangle will be drawn around optional header and list,
    if specified; if left_cols is specified then the rectangle will
    include that blank area to the left; this can be used to
    draw multiple such columns with multiple calls to this method,
    drawing a final rectangle around them all
    '''
    xpos = pdf.left_margin + 2
    ypos = None

    # header if any
    if header:
        pdf.bold_serif(12)
        # point size stuff is to add some space below top of rectangle
        ypos = pdf.get_y() - int(pdf.font_size_pt * 0.7)
        pdf.black_text()
        pdf.cell(40, 0, " " + header)
        pdf.ln(7)

    # list
    pdf.serif(10)
    pdf.black_text()

    # no header was printed so we must get ypos now
    if ypos is None:
        # point size stuff is to add some space below top of rectangle
        ypos = pdf.get_y() - int(pdf.font_size_pt * 0.7)

    max_width = 0
    for value in values:
        # give a bit of space between rectangle and text
        value = " " + value + " "
        if left_cols:
            pdf.set_x(left_cols)
        new_width = left_cols + pdf.get_string_width(value) + int(pdf.font_size_pt * 0.4)
        if new_width > max_width:
            max_width = new_width
        pdf.cell(0, 0, value)
        pdf.ln(5)

    # point size stuff is to add some space before bottom of rectangle
    ypos_new = pdf.get_y() + int(pdf.font_size_pt * 0.4)

    if rect:
        pdf.rect(xpos, ypos, max_width, ypos_new - ypos)
        pdf.ln(5)


def draw_bill_to(pdf):
    '''
    display email, company name and address of entity being billed
    in that order, but skip any fields not in the config file
    so that e.g. 'country' need not be displayed if the biller is
    in the same country
    '''
    pdf.ln(20)

    # one column
    ypos = pdf.get_y()
    values = ['To:']
    draw_unframed_list(pdf, None, values, 0, False)
    pdf.set_y(ypos)

    # the next column, plus border around both
    fields = ['email', 'name', 'street', 'city_state_zip', 'country']
    values = [pdf.config['bill_to'][field] for field in fields
              if field in pdf.config['bill_to']]
    draw_unframed_list(pdf, None, values, 20, True)


def draw_work_table(pdf):
    '''
    itemized description of work done during the month
    '''
    pdf.ln(20)

    values = [item['work'] for item in pdf.config['work_done']]
    draw_unframed_list(pdf, "Work Details", values, 0, False)


def draw_filled_table(pdf, table_content, table_info, widths=None, align="R"):
    '''
    draw a standard bordered table with headers centered and a different cell
    color than the content

    the table will be the width of the page (minus margins)

    args:
      pfd: PDF object
      table_content: list of dicts with content field names and content
      table_info: dict with two entries:
          headers: list of headers to go in the header row of the table
          content_keys: list of keys from the table_content dicts, one key per
              header, so we know which elements in table content correspond
              to which headers and in which order
      widths: list of widths of the cells in a row; if not supplied, the
              width of the header field plus a multiplier will be used
      align: right align the text (default) or some other alignment (e.g. "L")
    '''
    pdf.white_text()
    pdf.set_draw_color(64, 64, 64)
    pdf.light_fill_color()
    pdf.set_line_width(0.3)
    pdf.bold_serif(10)

    base_y = pdf.get_y() + 10
    pdf.set_y(base_y)

    # put the headers
    for idx, header in enumerate(table_info['headers']):
        if widths:
            width = widths[idx]
        else:
            width = len(header) * 4.9
        pdf.header_cell(width, 5, header)

    pdf.ln(5)
    pdf.set_fill_color(255, 255, 255)
    pdf.black_text()
    pdf.serif(8)

    # put the content
    for row in table_content:
        for idx, name in enumerate(table_info['content_keys']):
            value = row[name]
            if widths:
                width = widths[idx]
            else:
                width = len(table_info['headers'][idx]) * 4.9
            if align == "L":
                pdf.content_cell_left(width, 4, value)
            else:
                pdf.content_cell(width, 4, value)
        pdf.ln(4)


def draw_bill_table(pdf):
    '''
    display two line table with department, currency, terms
    and due date
    '''
    headers = ["Department", "Currency", "Payment Terms", "Due Date"]
    content_keys = ['department', 'currency', 'payment_terms', 'due_date']
    table_info = {'headers': headers, 'content_keys': content_keys}
    table_content = [pdf.config['bill']]
    draw_filled_table(pdf, table_content, table_info, align="L")


def draw_blanks(pdf, widths):
    '''
    fill in the empty cells on the left in the list of
    sub-total, tax, and total for billable items
    '''
    # choose the first billable item, this tells us how many cells
    # we had, the rightmost two will be filled, blank the rest
    empty = len(pdf.config['billables'][0]) - 2
    for i in range(0, empty):
        pdf.blank_cell(widths[i], 4)


def get_tax(pdf, subtotal):
    '''return tax based on default percentage in config'''
    tax = 0
    if pdf.config['tax_details'] is not None:
        tax = int(subtotal * pdf.config['tax_details']['default_percentage'] / 100)
    return tax


def draw_tax(pdf, tax, widths):
    '''display tax (or whatever it might be called in the config)'''
    pdf.ln(4)
    draw_blanks(pdf, widths)

    tax_name = "Tax"
    if ('tax_details' in pdf.config and 'tax_name' in pdf.config['tax_details'] and
            pdf.config['tax_details']['tax_name']):
        tax_name = pdf.config['tax_details']['tax_name']

    tax_text = pdf.config['currency_marker'] + " " + format_money(tax)

    pdf.content_cell(widths[len(widths)-2], 4, tax_name)
    pdf.content_cell(widths[len(widths)-1], 4, tax_text)


def draw_total(pdf, total, widths):
    '''
    write the total, with the proper currency marker
    '''
    pdf.ln(4)
    draw_blanks(pdf, widths)

    pdf.bold_serif(10)
    y_pos = pdf.get_y()
    x_line_start = pdf.get_x()

    # write the currency marker plus total
    total_text = pdf.config['currency_marker'] + ' ' + format_money(total)
    pdf.content_cell(widths[len(widths)-2], 6, "Total")
    pdf.content_cell(widths[len(widths)-1], 6, total_text)

    # place a dividing line just above the total entry
    x_line_end = pdf.get_x()
    pdf.set_draw_color(64, 64, 64)
    pdf.line(x_line_start, y_pos, x_line_end, y_pos)


def draw_billables_table(pdf):
    '''
    display the billable items
    '''
    headers = ["Week of:", "Hours/Week", "Rate", "Line Total"]
    content_keys = ["description", "hours", "rate", "cost"]
    table_info = {'headers': headers, 'content_keys': content_keys}
    widths = [116.5, 25, 25, 25]
    table_content = pdf.config['billables']
    draw_filled_table(pdf, table_content, table_info, widths)


def draw_totals_taxes_table(pdf):
    '''
    display the subtotal, the tax, and the final total
    '''
    widths = [116.5, 25, 25, 25]
    subtotal = 0
    for billable in pdf.config['billables']:
        subtotal = subtotal + convert_money(billable['cost'])
    # display accumulated subtotal
    pdf.set_draw_color(255, 255, 255)
    pdf.serif(8)
    pdf.ln(2)
    draw_blanks(pdf, widths)

    subtotal_text = pdf.config['currency_marker'] + ' ' + format_money(subtotal)
    pdf.content_cell(widths[len(widths)-2], 4, "Subtotal")
    pdf.content_cell(widths[len(widths)-1], 4, subtotal_text)

    tax = get_tax(pdf, subtotal)
    draw_tax(pdf, tax, widths)

    total = subtotal + tax
    draw_total(pdf, total, widths)


def render_pdf(config):
    '''
    given a yaml config with all information for them
    invoice, draw all the tables and other entries and
    write out the pdf
    '''

    # default: A4, portrait, all units are in milimeters except for
    # font sizes, which are in points
    pdf = PDF(config)
    # one page invoice, we hope. this will automatically write the
    # header and footer as well.
    pdf.add_page()

    # entity being billed
    draw_bill_to(pdf)

    # currency, payment terms and such
    draw_bill_table(pdf)

    # itemized work done
    draw_work_table(pdf)

    draw_billables_table(pdf)
    draw_totals_taxes_table(pdf)

    outfile_name = os.path.join(
        pdf.config['app_config']['output_dir'],
        "invoice_" + pdf.get_invoice_number() + ".pdf")

    err = pdf.output(outfile_name, 'F')
    if err:
        return err
    return None


def do_main():
    '''entry point'''
    template, valuesfile = get_args()
    pdf_config = get_yaml_config(template, valuesfile)
    for entry in pdf_config:
        entry = add_config_defaults(entry)
        entry = set_due_date(entry)
        if not validate_config(entry):
            usage("Bad yaml configuration, exiting")
        render_pdf(entry)


if __name__ == '__main__':
    do_main()
