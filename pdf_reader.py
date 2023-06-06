import PyPDF2 as pdf

class Pdf_Reader:
    def read_pdf(self, file_dir):
        try:
            # ABRE ARQUIVO EM BINÁRIO
            pdf_file = open(file_dir, 'rb')

            # DADOS DO PDF
            data = pdf.PdfReader(pdf_file)

            # SEPARA O TEXTO EM LINHAS
            converted_text = ""

            for page in data.pages:
                page_text = page.extract_text()
                for line in page_text.splitlines():
                    if line != "\n" and line != "" and line != " ":
                        line = self.__convert_text(line) # REMOVE CARACTERES
                        converted_text += line + '\n'
            
            return converted_text
        except:
            print("erro pdf reader")
            return ""
    
    # REMOVE E SUBSTITUI CARACTERES INDESEJADOS, COM INTUITO DE ECONOMIZAR TOKENS
    def __convert_text(self, text):
        text = text.replace('•','')
        text = text.replace('ê','e')
        text = text.replace('ã','a')
        text = text.replace('í','i')
        text = text.replace('â','a')
        text = text.replace('ç','c')
        text = text.replace('õ','o')

        return text