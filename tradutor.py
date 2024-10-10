import fitz  # PyMuPDF
from googletrans import Translator
from fpdf import FPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # Importação do ttk
import os
from tqdm import tqdm
import threading

# Inicializa o tradutor
translator = Translator()

# Função para extrair texto de um PDF
def extrair_texto_pdf(caminho_arquivo):
    doc = fitz.open(caminho_arquivo)
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()
    return texto

# Função para criar um novo PDF com o texto traduzido
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Tradução', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

def criar_pdf_traduzido(texto, caminho_saida):
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_body(texto)
    pdf.output(caminho_saida)

# Função para traduzir o texto com barra de progresso
def traduzir_com_progresso(texto, src_lang, dest_lang, progress_callback):
    # Determina o tamanho da barra de progresso
    linhas = texto.split('\n')
    total_linhas = len(linhas)
    texto_traduzido = ''

    for i, linha in enumerate(linhas):
        if linha.strip():
            traducao = translator.translate(linha, src=src_lang, dest=dest_lang).text
            texto_traduzido += traducao + '\n'
        else:
            texto_traduzido += '\n'
        
        # Atualiza a barra de progresso
        progress_callback((i + 1) / total_linhas * 100)

    return texto_traduzido

def selecionar_arquivo():
    caminho_arquivo_pdf = filedialog.askopenfilename(
        title="Selecione o arquivo PDF",
        filetypes=(("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*"))
    )
    if caminho_arquivo_pdf:
        texto_original = extrair_texto_pdf(caminho_arquivo_pdf)
        caminho_arquivo_pdf_traduzido = os.path.splitext(caminho_arquivo_pdf)[0] + '-traduzido.pdf'

        # Executa a tradução em uma thread separada para não bloquear a UI
        def traduzir_e_salvar():
            def progress_callback(porcentagem):
                progress_var.set(porcentagem)
                root.update_idletasks()

            src_lang, dest_lang = ('pt', 'en') if lang_var.get() == 'Português para Inglês' else ('en', 'pt')
            texto_traduzido = traduzir_com_progresso(texto_original, src_lang, dest_lang, progress_callback)
            criar_pdf_traduzido(texto_traduzido, caminho_arquivo_pdf_traduzido)
            messagebox.showinfo("Concluído", f'Tradução concluída! O arquivo traduzido foi salvo como {caminho_arquivo_pdf_traduzido}')

        threading.Thread(target=traduzir_e_salvar).start()

# Interface gráfica
root = tk.Tk()
root.title("Tradutor de PDF")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(padx=10, pady=10)

label = tk.Label(frame, text="Selecione um arquivo PDF para traduzir:", font=("Arial", 14))
label.pack(pady=10)

lang_var = tk.StringVar(value='Português para Inglês')
lang_options = ['Português para Inglês', 'Inglês para Português']
lang_menu = tk.OptionMenu(frame, lang_var, *lang_options)
lang_menu.pack(pady=10)

botao_selecionar = tk.Button(frame, text="Selecionar arquivo", command=selecionar_arquivo, font=("Arial", 12))
botao_selecionar.pack(pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100)
progress_bar.pack(pady=10)

root.mainloop()