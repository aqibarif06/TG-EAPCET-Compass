import pdfplumber


class TableAnalyzer:

    def analyze(self, pdf_path):

        with pdfplumber.open(pdf_path) as pdf:

            print("=" * 80)
            print(pdf_path)
            print("=" * 80)

            print("Total Pages :", len(pdf.pages))

            page = pdf.pages[0]

            tables = page.extract_tables()

            print("Tables Found :", len(tables))

            if not tables:
                print("No tables detected.")
                return

            first_table = tables[0]

            print()

            print("Rows :", len(first_table))

            print("Columns :", len(first_table[0]))

            print()

            print("First Five Rows\n")

            for row in first_table[:5]:
                print(row)