from flask import Flask, render_template, request, send_file, jsonify, url_for
import os
import tempfile
from werkzeug.utils import secure_filename
from conversor_itau import PDFTableExtractor
from conversor_bb import extract_data_from_pdf

app = Flask(__name__)
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def detect_bank(pdf_path):
    with open(pdf_path, 'rb') as file:
        content = file.read(1000).decode(errors='ignore').lower()
        if 'itau' in content:
            return 'itau'
        elif 'banco do brasil' in content:
            return 'bb'
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    files = request.files.getlist('files')
    selected_bank = request.form.get('bank')
    selected_pages = request.form.get('pages')

    if not selected_bank:
        return jsonify({'error': 'Nenhum banco selecionado'}), 400

    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'Nenhum arquivo válido'}), 400

    csv_files = []
    
    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        print(f"📂 Arquivo recebido: {filename} - Banco: {selected_bank} - Páginas: {selected_pages}")

        try:
            csv_path = process_pdf(file_path, selected_bank, selected_pages)
            csv_files.append(os.path.basename(csv_path))
            print(f"✅ Conversão concluída: {csv_path}")
        except Exception as e:
            print(f"❌ Erro ao processar {filename}: {e}")
            return jsonify({'error': f'Erro ao processar {filename}: {str(e)}'}), 500

    return jsonify({'files': csv_files})


@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return "Arquivo não encontrado", 404
    return send_file(file_path, as_attachment=True)

def process_pdf(file_path, bank, pages=None):
    csv_path = file_path.replace('.pdf', '.csv')

    if bank == 'itau':
        configs = {
            'flavor': 'stream',
            'page_1': {
                'table_areas': ['149,257, 552,21'],
                'columns': ['144,262, 204,262, 303,262, 351,262, 406,262, 418,262, 467,262, 506,262, 553,262']
            },
            'page_2_end': {
                'table_areas': ['151,760, 553,20'],
                'columns': ['157,757, 173,757, 269,757, 309,757, 363,757, 380,757, 470,757, 509,757, 545,757']
            }
        }
        
        extractor = PDFTableExtractor(file_path, configs)

        # Se o usuário especificou páginas, passamos no método `start()`
        try:
            if pages:
                pages_list = [int(p) if '-' not in p else list(range(int(p.split('-')[0]), int(p.split('-')[1]) + 1)) for p in pages.split(',')]
                pages_list = [p for sublist in pages_list for p in (sublist if isinstance(sublist, list) else [sublist])]
                print(f"🔍 Extraindo páginas específicas: {pages_list}")
                extractor.start(pages=pages_list)
            else:
                extractor.start()
            print("✅ Conversão concluída com sucesso")
        except Exception as e:
            print(f"❌ Erro ao processar PDF: {e}")
    
    elif bank == 'bb':
        extract_data_from_pdf(file_path, '6', '6')

    return csv_path



if __name__ == '__main__':
    app.run(host='192.168.15.129',port=5000, debug=True)
