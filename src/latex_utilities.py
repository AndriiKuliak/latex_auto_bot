import os
import subprocess

import fitz

import config

class LatexUtilties:
    def __init__(self):
        pass

    def generate_pdf(self, user_id, raw_latex):
        document_name = config.WORKDIR_PATH + 'user_document_{}'.format(user_id)
        document_name_tex = document_name + '.tex'
        document_name_pdf = document_name + '.pdf'

        with(open(document_name_tex, 'w')) as doc:
            doc.write(raw_latex)
        
        gen_command = ['pdflatex', '-interaction', 'nonstopmode', '-output-directory', config.WORKDIR_PATH, document_name_tex]
        process = subprocess.Popen(gen_command)
        process.communicate()

        return_code = process.returncode
        if not return_code == 0:
            os.unlink(document_name_pdf)

            raise ValueError('Failed to generate PDF!')
        
        os.unlink(document_name + '.log')
        os.unlink(document_name + '.aux')
        os.unlink(document_name_tex)

        return document_name_pdf


    def generate_png(self, user_id, raw_latex):
        png_file_name = 'converted_png_{}.png'.format(user_id)

        pdf_file_name = self.generate_pdf(user_id, raw_latex)

        converted_files = []

        doc = fitz.open(pdf_file_name)
        for i in range(doc.pageCount):
            doc_page = doc.loadPage(i)
            raw_png = doc_page.getPixmap()

            page_file_name = "{}{}_{}".format(config.WORKDIR_PATH, i, png_file_name)
            raw_png.writePNG(page_file_name)

            converted_files.append(page_file_name)

        os.unlink(pdf_file_name)

        return converted_files
