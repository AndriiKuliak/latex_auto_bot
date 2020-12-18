import os
import subprocess

import fitz

import config

class LatexUtilties:
    def __init__(self):
        pass

    def _create_latex_file(self, user_id, raw_latex):
        document_name = '{}user_document_{}.tex'.format(config.WORKDIR_PATH, user_id)

        with(open(document_name, 'w')) as doc:
            doc.write(raw_latex)
        
        return document_name

    def generate_pdf(self, user_id, document_name):
        document_name_base = document_name[:document_name.rindex('.')]
        document_name_pdf = document_name_base + '.pdf'

        gen_command = ['pdflatex', '-interaction', 'nonstopmode', '-output-directory', config.WORKDIR_PATH, document_name]
        process = subprocess.Popen(gen_command)
        process.communicate()

        os.unlink(document_name_base + '.log')
        os.unlink(document_name_base + '.aux')
        os.unlink(document_name)

        return_code = process.returncode
        if not return_code == 0:
            os.unlink(document_name_pdf)

            raise ValueError('Failed to generate PDF!')

        return document_name_pdf


    def generate_png(self, user_id, document_name):
        png_file_name = 'converted_png_{}.png'.format(user_id)

        pdf_file_name = self.generate_pdf(user_id, document_name)

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


    def generate_pdf_raw(self, user_id, raw_latex):
        return self.generate_pdf(user_id, self._create_latex_file(user_id, raw_latex))


    def generate_png_raw(self, user_id, raw_latex):
        return self.generate_png(user_id, self._create_latex_file(user_id, raw_latex))
