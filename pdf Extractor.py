import pandas as pd
import pdfplumber
import io


def pdf_extractor(path):

    df1 = pd.DataFrame(
        columns=['Doc Type', 'Document.No', 'Posting Date', 'Bill.No', 'Bill.Date', 'Gross', 'Net.Amt Deductions',
                 'TDS'])
    k = 0
    with open(path, 'rb') as f:
        content = io.BytesIO(f.read())
    with pdfplumber.open(content) as pdf:
        page0 = pdf.pages[0]
    for i in range(0, len(pdf.pages)):
        with pdfplumber.open(content) as pdf:
            page = pdf.pages[i]
            text = page.extract_table()
            if i != len(pdf.pages) - 1:
                for j in range(0, len(text[-1][0].split('C\n'))):
                    lst = text[-1][0].split('C\n')[j].replace('\n', '').split(" ")
                    try:
                        while True:
                            lst.remove('')
                    except ValueError:
                        pass
                    if len(lst) == 8:
                        print(lst)
                        df1.loc[k] = lst
                        k = k + 1
                    elif len(lst) == 9:
                        print(lst[0:-1])
                        df1.loc[k] = lst[0:-1]
                        k = k + 1

            elif i == len(pdf.pages) - 1:
                for j in range(0, len(text[-4][0].split('C\n '))):
                    lst = text[-4][0].split('C\n ')[j].replace('\n', '').split(" ")
                    try:
                        while True:
                            lst.remove('')
                    except ValueError:
                        pass
                    if len(lst) == 8:
                        print(lst)
                        df1.loc[k] = lst
                        k = k + 1
                    elif len(lst) == 9:
                        print(lst[0:-1])
                        df1.loc[k] = lst[0:-1]
                        k = k + 1
    df1['D/C'] = 'C'
    return df1
