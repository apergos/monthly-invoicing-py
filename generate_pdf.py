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
        self.margin = 8
        # A4 paper size. This must be adjusted if caller doesn't use A4.
        self.page_width = 210 - 16

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

    def draw_divider(self, ypos):
        '''draw a dividing line across the page 10 line breaks below our current pos'''
        self.ln(10)
        self.dark_draw_color()
        self.line(self.margin, ypos, self.page_width + self.margin, ypos)

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
        right_width = 20
        # "Date"
        self.set_xy(right_x, 40)
        self.dark_text()
        self.cell(right_width, 0, "Date:")
        self.light_text()
        self.cell(20, 0, self.get_invoice_date())
        # "Invoice Number"
        self.set_xy(right_x, 45)
        self.dark_text()
        self.cell(right_width, 0, "Invoice #:")
        self.light_text()
        self.cell(right_width, 0, self.get_invoice_number())

        # Left side
        self.dark_text()
        left_width = 40
        # Biller Name
        self.bold_serif(14)
        self.set_xy(self.margin, 40)
        self.cell(left_width, 0, self.config['business']['person'])
        # Biller Address
        self.serif(9)
        self.set_xy(self.margin, 45)
        self.cell(left_width, 0, self.config['business']['address'])

        self.draw_divider(50)

    def footer(self):
        '''
        Display at bottom of the invoice:
        divider line to separate footer from body of the invoice,
        company name, date invoice generated
        '''
        self.draw_divider(275)

        # Text
        self.bold_serif(10)

        # Left side
        # company name
        self.set_xy(self.margin, 280)
        self.dark_text()
        company_text = self.config['business']['name']
        self.cell(self.get_string_width(company_text), 0, company_text)

        # Right side
        # invoice generation date
        self.light_text()
        time_text = "Generated: " + time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        # add in left margin for correct placement
        self.set_x(self.page_width - self.get_string_width(time_text) + self.margin)
        self.cell(self.get_string_width(time_text), 0, time_text)


class InvoiceUtils():
    '''
    utils for manipulating invoice data
    '''
    @staticmethod
    def remove_off(work_days, week_start, week_end, off_days):
        '''given a list of days off for a month,
        see if any of them fall in the week_start/end range and
        if so, decrement work_days appropriately,
        then return the result'''
        for day in off_days:
            if week_start <= day <= week_end:
                work_days = work_days - 1
        return work_days

    @staticmethod
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
        work_days = InvoiceUtils.remove_off(work_days, week_start_date, week_end_date, off)

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
            work_days = InvoiceUtils.remove_off(work_days, week_start_date, week_end_date, off)
        return week_info

    @staticmethod
    def not_weekend(day, month, year):
        '''return True if the day is not a Sat/Sun, False otherwise'''
        weekday = datetime.date(year, month, day).weekday()
        if weekday in [5, 6]:
            return False
        return True

    @staticmethod
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
        cost = InvoiceUtils.convert_money(billable['rate']) * int(billable['hours'])
        billable['cost'] = currency_marker + ' ' + InvoiceUtils.format_money(cost)
        return billable

    @staticmethod
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
        off = [day for day in off if InvoiceUtils.not_weekend(day, month, year)]
        weeks = InvoiceUtils.get_week_info(year, month, off)
        billables = {'billables':
                     [InvoiceUtils.fillin_billable(
                         week, values[billdate]['rate'], month, currency_marker)
                      for week in weeks if week[3] > 0]}
        return billables

    @staticmethod
    def get_currency_marker(config):
        '''
        we may have an incompete config with values yet to be filled in
        but get the currency marker or its default and return it
        '''
        if 'currency_marker' not in config:
            return '$'
        return config['currency_marker']

    @staticmethod
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

        config['bill']['due_date'] = InvoiceUtils.get_n_months_later(
            config['billdate'], int(fields[1]))
        return config

    @staticmethod
    def get_n_months_later(date, count):
        '''given a date in YYYY-MM-DD format, return
        a date count months later in format YYYY/MM/DD'''
        year, month, day = date.split('-')
        old_date = datetime.date(int(year), int(month), int(day))
        new_date = old_date + datetime.timedelta(days=count)
        return new_date.strftime("%Y/%m/%d")

    @staticmethod
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

    @staticmethod
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


class InvoiceDraw():
    '''
    methods to draw all the bits
    '''
    def __init__(self, pdf):
        self.pdf = pdf

    def draw_unframed_list(self, header, values, left_cols, rect=False):
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
        xpos = self.pdf.margin + 2
        ypos = None

        # header if any
        if header:
            self.pdf.bold_serif(12)
            # point size stuff is to add some space below top of rectangle
            ypos = self.pdf.get_y() - int(self.pdf.font_size_pt * 0.7)
            self.pdf.black_text()
            self.pdf.cell(40, 0, " " + header)
            self.pdf.ln(7)

        # list
        self.pdf.serif(10)
        self.pdf.black_text()

        # no header was printed so we must get ypos now
        if ypos is None:
            # point size stuff is to add some space below top of rectangle
            ypos = self.pdf.get_y() - int(self.pdf.font_size_pt * 0.7)

        max_width = 0
        for value in values:
            # give a bit of space between rectangle and text
            value = " " + value + " "
            if left_cols:
                self.pdf.set_x(left_cols)
            new_width = (left_cols + self.pdf.get_string_width(value) +
                         int(self.pdf.font_size_pt * 0.4))
            if new_width > max_width:
                max_width = new_width
            self.pdf.cell(0, 0, value)
            self.pdf.ln(5)

        # point size stuff is to add some space before bottom of rectangle
        ypos_new = self.pdf.get_y() + int(self.pdf.font_size_pt * 0.4)

        if rect:
            self.pdf.rect(xpos, ypos, max_width, ypos_new - ypos)
            self.pdf.ln(5)

    def draw_bill_to(self):
        '''
        display email, company name and address of entity being billed
        in that order, but skip any fields not in the config file
        so that e.g. 'country' need not be displayed if the biller is
        in the same country
        '''
        self.pdf.ln(20)

        # one column
        ypos = self.pdf.get_y()
        values = ['To:']
        self.draw_unframed_list(None, values, 0, False)
        self.pdf.set_y(ypos)

        # the next column, plus border around both
        fields = ['email', 'name', 'street', 'city_state_zip', 'country']
        values = [self.pdf.config['bill_to'][field] for field in fields
                  if field in self.pdf.config['bill_to']]
        self.draw_unframed_list(None, values, 20, True)

    def draw_work_table(self):
        '''
        itemized description of work done during the month
        '''
        self.pdf.ln(20)

        values = [item['work'] for item in self.pdf.config['work_done']]
        self.draw_unframed_list("Work Details", values, 0, False)

    def set_table_header_colors_font(self):
        '''
        set font and colors used for bordered table headers
        '''
        self.pdf.white_text()
        self.pdf.set_draw_color(64, 64, 64)
        self.pdf.light_fill_color()
        self.pdf.set_line_width(0.3)
        self.pdf.bold_serif(10)

    def set_table_content_colors_font(self):
        '''
        set font and colors used for bordered table content
        '''
        self.pdf.black_text()
        self.pdf.set_draw_color(64, 64, 64)
        self.pdf.set_fill_color(255, 255, 255)
        self.pdf.set_line_width(0.3)
        self.pdf.serif(8)

    def get_widths(self, headers):
        '''
        given a bunch of headers for a bordered table that will fill
        the whole page, get and return the cell widths for the table
        '''
        self.set_table_header_colors_font()
        string_widths = [self.pdf.get_string_width(header) for header in headers]
        spare_per_header = (self.pdf.page_width - sum(string_widths)) / len(headers)
        header_widths = []
        for idx, _ in enumerate(headers):
            header_widths.append(string_widths[idx] + spare_per_header)
        return header_widths

    def draw_filled_table(self, table_content, table_info, align="R"):
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
            align: right align the text (default) or some other alignment (e.g. "L")
        '''
        self.set_table_header_colors_font()

        base_y = self.pdf.get_y() + 10
        self.pdf.set_y(base_y)

        # get column widths
        widths = self.get_widths(table_info['headers'])

        # put the headers
        for idx, header in enumerate(table_info['headers']):
            self.pdf.header_cell(widths[idx], int(self.pdf.font_size_pt / 2), header)

        self.pdf.ln(5)
        self.set_table_content_colors_font()

        # put the content
        for row in table_content:
            for idx, name in enumerate(table_info['content_keys']):
                value = row[name]
                if align == "L":
                    self.pdf.content_cell_left(widths[idx], int(self.pdf.font_size_pt / 2), value)
                else:
                    self.pdf.content_cell(widths[idx], int(self.pdf.font_size_pt / 2), value)
            self.pdf.ln(4)

    def draw_bill_table(self):
        '''
        display two line table with department, currency, terms
        and due date
        '''
        headers = ["Department", "Currency", "Payment Terms", "Due Date"]
        content_keys = ['department', 'currency', 'payment_terms', 'due_date']
        table_info = {'headers': headers, 'content_keys': content_keys}
        table_content = [self.pdf.config['bill']]
        self.draw_filled_table(table_content, table_info, align="L")

    def draw_blanks(self, widths):
        '''
        fill in the empty cells on the left in the list of
        sub-total, tax, and total for billable items
        '''
        # choose the first billable item, this tells us how many cells
        # we had, the rightmost two will be filled, blank the rest
        empty = len(self.pdf.config['billables'][0]) - 2
        for i in range(0, empty):
            self.pdf.blank_cell(widths[i], int(self.pdf.font_size_pt / 2))

    def get_tax(self, subtotal):
        '''return tax based on default percentage in config'''
        tax = 0
        if self.pdf.config['tax_details'] is not None:
            tax = int(subtotal * self.pdf.config['tax_details']['default_percentage'] / 100)
        return tax

    def get_subtotal(self):
        '''compute and return the subtotal'''
        subtotal = 0
        for billable in self.pdf.config['billables']:
            subtotal = subtotal + InvoiceUtils.convert_money(billable['cost'])
        return subtotal

    def draw_subtotal(self, subtotal, widths, xpos):
        '''display the subtotal line'''
        # display accumulated subtotal
        self.pdf.ln(2)
        self.pdf.set_draw_color(255, 255, 255)
        self.pdf.serif(8)
        self.pdf.set_x(xpos)

        subtotal_text = (self.pdf.config['currency_marker'] + ' ' +
                         InvoiceUtils.format_money(subtotal))
        self.pdf.content_cell(widths[0], int(self.pdf.font_size_pt / 2), "Subtotal")
        self.pdf.content_cell(widths[1], int(self.pdf.font_size_pt / 2), subtotal_text)

    def draw_tax(self, tax, widths, xpos):
        '''display tax (or whatever it might be called in the config)'''
        self.pdf.ln(4)
        self.pdf.set_draw_color(255, 255, 255)
        self.pdf.serif(8)
        self.pdf.set_x(xpos)

        tax_name = "Tax"
        if ('tax_details' in self.pdf.config and 'tax_name' in self.pdf.config['tax_details'] and
                self.pdf.config['tax_details']['tax_name']):
            tax_name = self.pdf.config['tax_details']['tax_name']

        tax_text = self.pdf.config['currency_marker'] + " " + InvoiceUtils.format_money(tax)

        self.pdf.content_cell(widths[0], int(self.pdf.font_size_pt / 2), tax_name)
        self.pdf.content_cell(widths[1], int(self.pdf.font_size_pt / 2), tax_text)

    def set_total_colors_font(self):
        '''set colors and font for the Totals line'''
        self.pdf.set_draw_color(255, 255, 255)
        self.pdf.bold_serif(10)

    def draw_total(self, total, widths, xpos):
        '''
        write the total, with the proper currency marker
        '''
        self.set_total_colors_font()
        self.pdf.ln(4)
        self.pdf.set_x(xpos)

        y_pos = self.pdf.get_y()

        # write the currency marker plus total
        total_text = self.pdf.config['currency_marker'] + ' ' + InvoiceUtils.format_money(total)
        self.pdf.content_cell(widths[0], int(self.pdf.font_size_pt / 2), "Total")
        self.pdf.content_cell(widths[1], int(self.pdf.font_size_pt / 2), total_text)

        # place a dividing line just above the total entry
        x_line_end = self.pdf.get_x()
        self.pdf.set_draw_color(64, 64, 64)
        self.pdf.line(xpos, y_pos, x_line_end, y_pos)

    def draw_billables_table(self):
        '''
        display the billable items
        '''
        headers = ["Week of:", "Hours/Week", "Rate", "Line Total"]
        content_keys = ["description", "hours", "rate", "cost"]
        table_info = {'headers': headers, 'content_keys': content_keys}
        table_content = self.pdf.config['billables']
        self.draw_filled_table(table_content, table_info, None)

    def get_totals_taxes_widths(self):
        '''
        calculate and return the widths of the two columns in the
        subtotal/taxes/total table. these will be fixed based on them
        font size and the text. yeah now we have "Total" defined as
        the string in two places, ugh.
        '''
        self.set_total_colors_font()
        # make more than this in a week? get yer own invoice generator!
        total_name = "Total"
        max_total_text = self.pdf.config['currency_marker'] + ' ' + "999999.99"
        widths = [self.pdf.get_string_width(total_name), self.pdf.get_string_width(max_total_text)]
        # add a little padding
        widths = [width + 2 for width in widths]
        return widths

    def draw_totals_taxes_table(self):
        '''
        display the subtotal, the tax, and the final total
        '''
        widths = self.get_totals_taxes_widths()
        # must add in the left margin to properly place x
        xpos = self.pdf.page_width - sum(widths) + self.pdf.margin + 2

        subtotal = self.get_subtotal()
        self.draw_subtotal(subtotal, widths, xpos)

        tax = self.get_tax(subtotal)
        self.draw_tax(tax, widths, xpos)

        total = subtotal + tax
        self.draw_total(total, widths, xpos)


class InvoiceConfig():
    '''manage invoice settings'''
    @staticmethod
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
        currency_marker = InvoiceUtils.get_currency_marker(yaml.safe_load(fake_completed_text))

        for billdate in values:
            work = {'work_done': values[billdate]['work_done']}

            billables = InvoiceUtils.get_billables(values, billdate, currency_marker)

            completed_text = text % {
                "BILLDATE": billdate,
                "WORK": yaml.dump(work),
                "BILLABLES": yaml.dump(billables)
            }
            config.append(yaml.safe_load(completed_text))

        return config

    @staticmethod
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

        if ('image_file' in config['business'] and
                not os.path.exists(config['business']['image_file'])):
            sys.stderr.write("No such image file " + config['business']['image_file'] + "\n")
            return False
        return True

    @staticmethod
    def add_config_defaults(config):
        '''add some defaults where we can'''
        config['currency_marker'] = InvoiceUtils.get_currency_marker(config)
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
            config['app_config']['serif_font'] = "DejaVu"

        if 'colors' not in config:
            config['colors'] = {}
        if 'color_light' not in config['colors']:
            config['colors']['color_light'] = {'r': 117, 'g': 180, 'b': 209}
        if 'color_light' not in config['colors']:
            config['colors']['color_dark'] = {'r': 16, 'g': 46, 'b': 95}

        return config


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

    draw = InvoiceDraw(pdf)

    # entity being billed
    draw.draw_bill_to()

    # currency, payment terms and such
    draw.draw_bill_table()

    # itemized work done
    draw.draw_work_table()

    draw.draw_billables_table()
    draw.draw_totals_taxes_table()

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
    pdf_config = InvoiceConfig.get_yaml_config(template, valuesfile)
    for entry in pdf_config:
        entry = InvoiceConfig.add_config_defaults(entry)
        entry = InvoiceUtils.set_due_date(entry)
        if not InvoiceConfig.validate_config(entry):
            usage("Bad yaml configuration, exiting")
        render_pdf(entry)


if __name__ == '__main__':
    do_main()
