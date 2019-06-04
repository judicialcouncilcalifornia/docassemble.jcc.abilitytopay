##############################################################################
#
# A simple example of some of the features of the XlsxWriter Python module.
#
# Copyright 2013-2019, John McNamara, jmcnamara@cpan.org
#
import xlsxwriter
import translations


langs=["es","zh-t","zh-s"]
for abbrev in langs:
    # Create an new Excel file and add a worksheet.
    workbook = xlsxwriter.Workbook('translations-'+abbrev+'.xlsx')
    worksheet = workbook.add_worksheet()

    # Widen the columns
    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:B', 19)
    worksheet.set_column('C:C', 120)
    worksheet.set_column('D:D', 120)


    # Write some simple text.
    worksheet.write('A1', 'Internal Identifier')
    worksheet.write('B1', 'Changes needed(y/n)')
    worksheet.write('C1', 'English')
    worksheet.write('D1', 'Translation')

    counter = 1

    for internal_identifier in translations.translations:
        en = translations.translations[internal_identifier]["en"]
        translation = translations.translations[internal_identifier][abbrev]
        counter = counter + 1
        cell_format = workbook.add_format({'text_wrap': True})
        worksheet.write('A'+str(counter), internal_identifier,cell_format)
        worksheet.write('B'+str(counter), "?",cell_format)
        worksheet.write('C'+str(counter), en,cell_format)
        worksheet.write('D'+str(counter), translation,cell_format)


    workbook.close()
