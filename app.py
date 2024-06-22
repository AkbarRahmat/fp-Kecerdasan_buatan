from flask import Flask, request, render_template
import pandas as pd
import re

app = Flask(__name__)

# Load data
data = pd.read_csv('data/updated_preprocessed_data.csv')

# Membersihkan data dari koma di kolom "Metode Pengendalian Lain"
def clean_methods(methods):
    # Menghapus koma dan karakter lainnya seperti tanda kutip dan kurung siku
    methods = re.sub(r"[,'[\]]", "", methods)
    return methods.strip()

# Membersihkan seluruh kolom "Metode Pengendalian Lain"
data['Metode Pengendalian Lain'] = data['Metode Pengendalian Lain'].apply(clean_methods)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    nama_hama = request.form.get('nama_hama')
    gejala_serangan = request.form.get('gejala_serangan')

    # Pisahkan kata kunci menggunakan regex
    keywords = re.split(r'\s+', gejala_serangan.strip())

    # Filter data berdasarkan nama hama dan gejala serangan
    result = data[
        ((data['Nama Hama (Latin)'].str.contains(nama_hama, case=False, na=False, regex=False)) |
         (data['Nama Hama (Indonesia)'].str.contains(nama_hama, case=False, na=False, regex=False))) &
        (data['Gejala Serangan'].apply(lambda x: all(keyword.lower() in x.lower() for keyword in keywords)))
    ]

    # Mengambil kolom yang relevan untuk output
    if not result.empty:
        output = result[['Fase Pertumbuhan Diserang', 'Pestisida Kimia Efektif', 'Pestisida Hayati Efektif', 'Metode Pengendalian Lain']]
    else:
        output = pd.DataFrame(columns=['Fase Pertumbuhan Diserang', 'Pestisida Kimia Efektif', 'Pestisida Hayati Efektif', 'Metode Pengendalian Lain'])

    # Mengatur ulang index dan menambahkan nomor urut
    output.reset_index(drop=True, inplace=True)
    output.index = output.index + 1

    # Convert DataFrame to HTML with numbered rows
    output_html = output.to_html(classes='data', header="true", index=True)
    output_html = output_html.replace('<th>', '<th scope="col">')


    return render_template('index.html', tables=[output_html], titles=output.columns.values)

if __name__ == '__main__':
    app.run(debug=True)
