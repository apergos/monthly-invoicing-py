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
        self.set_font(self.config['app_config']['sans_font'], "BI", 28)
        # logo
        self.image(self.config['business']['image_file'], 0, 10, 100, 0, '', '')

        # Right side
        # "Invoice"
        self.set_xy(140, 30)
        self.dark_text()
        self.cell(40, 0, "Invoice")
        # "Date"
        self.set_xy(140, 40)
        self.dark_text()
        self.set_font(self.config['app_config']['serif_font'], "", 12)
        self.cell(20, 0, "Date:")
        self.light_text()
        self.cell(20, 0, self.get_invoice_date())
        # "Invoice Number"
        self.set_xy(140, 45)
        self.dark_text()
        self.cell(20, 0, "Invoice #:")
        self.light_text()
        self.cell(20, 0, self.get_invoice_number())

        # Left side
        # Biller Name
        self.set_xy(8, 40)
        self.dark_text()
        self.set_font(self.config['app_config']['serif_font'], "B", 14)
        self.cell(40, 0, self.config['business']['person'])
        # Biller Address
        self.set_font(self.config['app_config']['serif_font'], "", 10)
        self.set_xy(8, 45)
        self.cell(40, 0, self.config['business']['address'])

        # Divider line
        self.ln(10)
        self.dark_draw_color()
        self.line(8, 50, 200, 50)

    def footer(self):
        '''
        Display at bottom of the invoice:
        divider line to separate footer from body of the invoice,
        company name, date invoice generated
        '''
        # divider line
        self.ln(10)
        self.dark_draw_color()
        self.line(8, 275, 200, 275)

        # Left side
        # company name
        self.set_xy(8.0, 280)
        self.dark_text()
        self.cell(143, 0, self.config['business']['name'])

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
    # print(weekday, month, day, year)
    if weekday in [5, 6]:
        return False
    return True


def fillin_billable(week_info, rate, month):
    '''
    given week start and end and hours, the billing rate and the month,
    put together a basic billable item and return it
    '''
    billable = {}
    billable['rate'] = str(rate)
    billable['hours'] = str(week_info[3])
    billable['description'] = 'Week of {month} {start} - {end}'.format(
        month=calendar.month_name[month], start=week_info[0], end=week_info[1])
    return billable


def get_billables(values, billdate):
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
                 [fillin_billable(week, values[billdate]['rate'], month)
                  for week in weeks if week[3] > 0]}
    return billables


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

    for billdate in values:
        work = {'work_done': values[billdate]['work_done']}

        billables = get_billables(values, billdate)

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
        config['app_config']['serif_font'] = "Times"

    if 'colors' not in config:
        config['colors'] = {}
    if 'color_light' not in config['colors']:
        config['colors']['color_light'] = {'r': 117, 'g': 180, 'b': 209}
    if 'color_light' not in config['colors']:
        config['colors']['color_dark'] = {'r': 16, 'g': 46, 'b': 95}

    return config


def convert_money(value):
    '''
    skip leading non-digit if any

    take a decimal string, convert it to the corresponding int
    multiplied by 100, and return that

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


def draw_bill_to(pdf):
    '''
    display email, company name and address of entity being billed
    in that order, but skip any fields not in the config file
    so that e.g. 'country' need not be displayed if the biller is
    in the same country
    '''
    pdf.black_text()
    pdf.ln(10)
    pdf.ln(10)

    pdf.cell(0, 0, "To: ")

    fields = ['email', 'name', 'street', 'city_state_zip', 'country']
    last_field = fields[-1]
    for field in fields:
        if field in pdf.config['bill_to']:
            pdf.set_x(20)
            pdf.cell(0, 0, pdf.config['bill_to'][field])
            if field != last_field:
                pdf.ln(5)


def draw_bill_table(pdf):
    '''
    display two line table with department, currency, terms
    and due date
    '''
    pdf.white_text()
    pdf.set_draw_color(64, 64, 64)
    pdf.light_fill_color()
    pdf.set_line_width(0.3)
    pdf.set_font(pdf.config['app_config']['serif_font'], "B", 10)

    base_y = pdf.get_y() + 10
    pdf.set_y(base_y)

    fields = ["Department", "Currency", "Payment Terms", "Due Date"]
    for field in fields:
        width = len(field) * 4.9
        pdf.header_cell(width, 5, field)

    pdf.ln(5)
    pdf.set_fill_color(255, 255, 255)
    pdf.black_text()
    pdf.set_font(pdf.config['app_config']['serif_font'], "", 8)

    for idx, name in enumerate(pdf.config['bill']):
        value = pdf.config['bill'][name]
        width = len(fields[idx]) * 4.9
        pdf.content_cell_left(width, 4, value)


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
    tax_name = "Tax"
    if ('tax_details' in pdf.config and 'tax_name' in pdf.config['tax_details'] and
            pdf.config['tax_details']['tax_name']):
        tax_name = pdf.config['tax_details']['tax_name']

    pdf.ln(4)
    draw_blanks(pdf, widths)
    tax_text = pdf.config['currency_marker'] + " " + format_money(tax)
    pdf.content_cell(widths[len(widths)-2], 4, tax_name)
    pdf.content_cell(widths[len(widths)-1], 4, tax_text)


def draw_total(pdf, total, widths):
    '''
    write the total, with the proper currency marker
    '''
    pdf.ln(4)
    draw_blanks(pdf, widths)
    pdf.set_font(pdf.config['app_config']['serif_font'], "B", 10)
    y_pos = pdf.get_y()
    x_pos = pdf.get_x()

    # write the currency marker plus total
    total_text = pdf.config['currency_marker'] + ' ' + format_money(total)
    pdf.content_cell(widths[len(widths)-2], 6, "Total")
    pdf.content_cell(widths[len(widths)-1], 6, total_text)

    # place a dividing line just above the total entry
    x2_pos = pdf.get_x()
    pdf.set_draw_color(64, 64, 64)
    pdf.line(x_pos, y_pos, x2_pos, y_pos)


def draw_billables_table(pdf):
    '''
    display the billable items, subtotal, tax and grand total
    '''
    pdf.set_fill_color(255, 0, 0)
    pdf.white_text()
    pdf.set_draw_color(64, 64, 64)
    pdf.light_fill_color()
    pdf.set_line_width(0.3)
    pdf.set_font(pdf.config['app_config']['serif_font'], "B", 10)
    base_y = pdf.get_y() + 10
    pdf.set_y(base_y)

    fields = ["Week of:", "Hours/Week", "Rate", "Line Total"]
    widths = [116.5, 25, 25, 25]
    # display field names (week, hours, rate, line total))
    for idx, field in enumerate(fields):
        pdf.header_cell(widths[idx], 5, field)

    pdf.ln(5)
    pdf.set_fill_color(255, 255, 255)
    pdf.black_text()
    pdf.set_font(pdf.config['app_config']['serif_font'], "", 8)

    subtotal = 0

    # display the values for each field for each billed item
    # and also accumulate the running total of all billed items
    names = ["description", "hours", "rate", "cost"]

    for billable in pdf.config['billables']:
        # printable format for the rate
        billable['rate'] = pdf.config['currency_marker'] + ' ' + billable['rate']
        # add the line item cost
        cost = convert_money(billable['rate']) * int(billable['hours'])
        billable['cost'] = pdf.config['currency_marker'] + ' ' + format_money(cost)

        for idx, name in enumerate(names):
            pdf.content_cell(widths[idx], 4, billable[name])

        subtotal = subtotal + cost
        pdf.ln(4)

    # display accumulated subtotal
    pdf.set_draw_color(255, 255, 255)
    pdf.set_font(pdf.config['app_config']['serif_font'], "", 8)
    pdf.ln(2)
    draw_blanks(pdf, widths)

    subtotal_text = pdf.config['currency_marker'] + ' ' + format_money(subtotal)
    pdf.content_cell(widths[len(widths)-2], 4, "Subtotal")
    pdf.content_cell(widths[len(widths)-1], 4, subtotal_text)

    tax = get_tax(pdf, subtotal)
    draw_tax(pdf, tax, widths)

    total = subtotal + tax
    draw_total(pdf, total, widths)


def draw_work_table(pdf):
    '''
    itemized description of work done during the month
    '''
    pdf.ln(20)
    pdf.set_font(pdf.config['app_config']['serif_font'], "B", 12)
    pdf.black_text()

    pdf.cell(40, 0, "Work Details")

    pdf.ln(5)
    pdf.set_font(pdf.config['app_config']['serif_font'], "", 10)

    for item in pdf.config['work_done']:
        pdf.cell(125, 5, item['work'])
        pdf.ln(5)


def render_pdf(config):
    '''actually render the pdf, heh'''
    pdf = PDF(config)
    pdf.add_page()

    # entity being billed
    draw_bill_to(pdf)

    # currency, payment terms and such
    draw_bill_table(pdf)

    # itemized work done
    draw_work_table(pdf)

    draw_billables_table(pdf)

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
