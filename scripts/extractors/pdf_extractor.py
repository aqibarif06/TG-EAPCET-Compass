import pdfplumber


class PDFExtractor:

    def extract_rows(self, pdf_path):

        rows = []

        with pdfplumber.open(pdf_path) as pdf:

            for page_number, page in enumerate(pdf.pages, start=1):

                tables = page.extract_tables()

                if not tables:
                    continue

                table = tables[0]

                # Skip title row and header row
                data_rows = table[2:]

                for row in data_rows:

                    if row:
                        rows.append(row)

        return rows