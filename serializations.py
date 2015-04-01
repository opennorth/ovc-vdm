# -*- coding: utf-8 -*-
import ho.pisa as pisa 
from StringIO import *
import csv
import xlsxwriter
from flask import render_template, request, abort
from flask.ext.restful import Api


class CustomApi(Api):


    FORMAT_MIMETYPE_MAP = {
        "csv": "text/csv",
        "json": "application/json",
        "pdf": "application/pdf",
        "ocds": "application/json",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        # Add other mimetypes as desired here
    }


    def mediatypes(self):
        """Allow all resources to have their representation
        overriden by the `format` URL argument"""

        preferred_response_type = []
        format = request.args.get("format")
        if format:
            mimetype = self.FORMAT_MIMETYPE_MAP.get(format)
            preferred_response_type.append(mimetype)
            if not mimetype:
                #TODO: THIS DOES NOT WORK...
                abort(404)
        return preferred_response_type + super(CustomApi, self).mediatypes()



def generate_pdf(data):

    html = render_template('pdf_generator.html', data=data, url=request.url)

    output_pdf = StringIO()
    pisa.CreatePDF(html.encode('utf-8'), output_pdf)

    return output_pdf.getvalue()

def generate_csv(data):
    output_csv = StringIO()
    csv_writer = csv.writer(output_csv)

    header = ["identifiant", "date", "montant", "type", "acheteur", "activité", "description", "fournisseur", "autorisation", "décision", "dossier" ]
    csv_writer.writerow(header)

    for release in data["releases"]:
        laliste = []
        laliste.append(release["ocid"])
        laliste.append(release["date"][0:9])
        laliste.append(release["awards"][0]["value"]["amount"])
        laliste.append(release["tender"]["procurementMethodRationale"])
        laliste.append(release["buyer"]["name"])
        laliste.append(", ".join(release["subject"]))
        laliste.append(release["awards"][0]["items"][0]["description"])
        laliste.append(release["awards"][0]["suppliers"][0]["name"])
        laliste.append(release["tender"]["procuringEntity"]["name"])
        laliste.append(release["awards"][0]["items"][0]["id"])
        laliste.append(release["awards"][0]["id"])
                
        csv_writer.writerow(laliste)

    return output_csv.getvalue()


def generate_xlsx(data):
    output_xlsx = StringIO()
    workbook = xlsxwriter.Workbook(output_xlsx)
    worksheet = workbook.add_worksheet()

    header = ["identifiant", "date", "montant", "type", "acheteur", "activité", "description", "fournisseur", "autorisation", "décision", "dossier" ]
    [worksheet.write(0, col, val) for (col, val) in enumerate(header) ]

    col = 0
    row = 1

    for release in data["releases"]:

        worksheet.write(row, col, release["ocid"])
        worksheet.write(row, col+1, release["date"][0:9])
        worksheet.write(row, col+2, release["awards"][0]["value"]["amount"])
        worksheet.write(row, col+3, release["tender"]["procurementMethodRationale"])
        worksheet.write(row, col+4, release["buyer"]["name"])
        worksheet.write(row, col+5, ", ".join(release["subject"]))
        worksheet.write(row, col+6, release["awards"][0]["items"][0]["description"])
        worksheet.write(row, col+7, release["awards"][0]["suppliers"][0]["name"])
        worksheet.write(row, col+8, release["tender"]["procuringEntity"]["name"])
        worksheet.write(row, col+9, release["awards"][0]["items"][0]["id"])
        worksheet.write(row, col+10, release["awards"][0]["id"])
                
             
        row += 1

    workbook.close()
    return output_xlsx.getvalue()


