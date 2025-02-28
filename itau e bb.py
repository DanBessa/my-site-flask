import tkinter as tk
from tkinter import messagebox

def escolher_banco():
    global banco_selecionado
    banco_selecionado = None

    def selecionar_bb():
        global banco_selecionado
        banco_selecionado = "bb"
        janela.destroy()

    def selecionar_itau():
        global banco_selecionado
        banco_selecionado = "itau"
        janela.destroy()

    # Criando a janela Tkinter
    janela = tk.Tk()
    janela.title("Selecione o Banco")
    janela.geometry("300x150")
    janela.resizable(False, False)

    tk.Label(janela, text="Escolha o banco:", font=("Arial", 12)).pack(pady=10)

    btn_bb = tk.Button(janela, text="Banco do Brasil", font=("Arial", 10), command=selecionar_bb)
    btn_bb.pack(pady=5)

    btn_itau = tk.Button(janela, text="Banco Itaú", font=("Arial", 10), command=selecionar_itau)
    btn_itau.pack(pady=5)

    janela.mainloop()

    return banco_selecionado

# 🔹 Importa o código correto após a seleção do banco
if __name__ == "__main__":
    banco = escolher_banco()
    
    if banco == "bb":
        import conversor_bb # Substitua pelo nome correto do arquivo Banco do Brasil
        conversor_bb.selecionar_pdfs()

    elif banco == "itau":
        import conversor_itau # Substitua pelo nome correto do arquivo Banco Itaú
        conversor_itau.processar_pdf_itau()

    else:
        messagebox.showwarning("Aviso", "Nenhuma opção foi selecionada. O programa será encerrado.")
