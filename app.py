import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
import pdfplumber
import io

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/downloads/'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

app = Flask(__name__, static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 8mb
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            process_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('index.html')


def process_file(path, filename):
    pdf_parser(path, filename)
    # with open(path, 'a') as f:
    #    f.write("\nAdded processed content")


def pdf_parser(path, filename):
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
    output_stream = open(app.config['DOWNLOAD_FOLDER'] + filename[:-4]+'.csv', 'wb')
    print(output_stream)
    df1.to_csv(output_stream,index=False)



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename[:-4]+'.csv', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)