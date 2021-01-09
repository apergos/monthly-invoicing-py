#monthly-invoicing-py

## Description
What is this? A lousy python script to generate invoices on a monthly basis with as little input data as possible.

The script is a loose port of https://github.com/relistan/billmonger to python, adapted to my personal needs.

## Dependencies
 * python3
 * https://github.com/alexanderankin/pyfpdf.git

## Testing
  * Get and install pyfpdf from link in the above section
  * From within the git repository, run
```
   python3 generate_pdf.py -v inputs/sample.yaml -t templates/example.tmpl
```
  * Check the pdf invoice in the "billed" subdirectory.
  * If you have font issues, check the paths of DejaVuSerif.ttf and DejaVuSerif-Bold.ttf and edit generate_pdf.py to update them

## Installation
 * Put the script somewhere within your path
 * Make a directory for your future billing
 * Within that, make four subdirectories:
   * dir for invoice inputs
   * dir for invoice templates
   * dir for created invoices
   * dir for logos
 * Create a logo in your logos subdirectory, if you need one
 * Create a yaml template in your templates subdirectory, adapting templates/example.tmpl to your needs

## Customization notes
 You can adust some settings in the template as follows:
 * If you need the tax to be called VAT or some other thing, change the "tax_name" setting
 * Change the table header fields background color by changing the values for "color_light"
 * Change the color of the "Invoices" and other dark but not black text but changing the values for "color_dark"
 * Change the Net terms by changing the value for "payment_terms"
 * Change the output directory by changing the value for "output_dir"
 * Change the currency marker ($, € etc) by changing the value for "currency_marker"
 * Change the currency name by changing the value for "currency"
 * Change the path to the logo by changing the value for "image_file"
 * Change the sans font by changing the value for "sans_font"
 * Change the serif font by changing the value for "serif_font" AND adding the corresponding entries for the font to __init__() in generate_pdf.py

## Assumptions made
 * Work days are Monday through Friday
 * The week starts on Sunday
 * No partial days are taken off

## Running
 * Create a yaml file of invoice inputs in your invoice inputs subdirectory. You may copy from inputs/blank.yaml and fill in the relevant bits.
   * Each work item you want listed on the invoice must have a text string.
   * The hourly rate must be in double quotes.
   * The list of days off can be empty. Days that fall on the weekend will silently be ignored, since weekend days are already skipped.
   * The billing date must be in yyyy-mm-dd format, in double quotes, at the top of the file, and it must be the last day of the month being billed.
   * Net terms can be one of: Net 30,60,90,120,180; default is Net 30.
 * Be in the directory just above all of the subdirectories for inputs, templates, and so on
 * Run the script: generate_pdf.py -v path-to-invoice-inputs-file -t path-to-template-file
 * Check the output subdirectory for your pdf invoice.
