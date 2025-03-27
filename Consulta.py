import mysql.connector
import csv
import tkinter as tk
from tkinter import ttk, messagebox

# Configuração do Banco de Dados
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "combustiveis"
}

# Função para conectar ao MySQL e executar uma procedure
def executar_procedure(nome_procedure, params=()):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.callproc(nome_procedure, params)
        
        resultados = []
        for result in cursor.stored_results():
            resultados.extend(result.fetchall())
        
        cursor.close()
        conn.close()
        return resultados
    except mysql.connector.Error as err:
        messagebox.showerror("Erro no Banco de Dados", f"Erro: {err}")
        return []

# Função para exibir os resultados na interface
def mostrar_resultados(resultados, colunas):
    for widget in frame_resultados.winfo_children():
        widget.destroy()
    
    if not resultados:
        messagebox.showinfo("Resultado", "Nenhum dado encontrado.")
        return

    tree = ttk.Treeview(frame_resultados, columns=colunas, show="headings")
    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    for row in resultados:
        tree.insert("", tk.END, values=row)
    
    tree.pack(fill=tk.BOTH, expand=True)

# Chamadas para as procedures
def menor_preco():
    bairro = entry_bairro.get() or None
    combustivel = entry_combustivel.get() or None
    resultados = executar_procedure("menor_preco_combustivel", (bairro, combustivel))
    colunas = ["Nome Posto", "Endereço", "Bairro", "Combustível", "Preço", "Data"]
    mostrar_resultados(resultados, colunas)

def preco_medio():
    bairro = entry_bairro.get() or None
    data_inicial = entry_data_inicial.get() or None
    data_final = entry_data_final.get() or None
    resultados = executar_procedure("preco_medio_combustivel", (bairro, data_inicial, data_final))
    colunas = ["Combustível", "Preço Médio"]
    mostrar_resultados(resultados, colunas)

def resumo_posto():
    data_inicial = entry_data_inicial.get() or None
    data_final = entry_data_final.get() or None
    resultados = executar_procedure("resumo_posto_combustivel", (data_inicial, data_final))
    colunas = ["Posto", "Bairro", "Total Coletas", "Combustível", "Preço Médio"]
    mostrar_resultados(resultados, colunas)

# Criando a interface gráfica
root = tk.Tk()
root.title("Consulta de Preços de Combustíveis")
root.geometry("800x500")

frame_inputs = tk.Frame(root)
frame_inputs.pack(pady=10)

tk.Label(frame_inputs, text="Bairro:").grid(row=0, column=0)
entry_bairro = tk.Entry(frame_inputs)
entry_bairro.grid(row=0, column=1)

tk.Label(frame_inputs, text="Combustível:").grid(row=0, column=2)
entry_combustivel = tk.Entry(frame_inputs)
entry_combustivel.grid(row=0, column=3)

tk.Label(frame_inputs, text="Data Inicial:").grid(row=1, column=0)
entry_data_inicial = tk.Entry(frame_inputs)
entry_data_inicial.grid(row=1, column=1)

tk.Label(frame_inputs, text="Data Final:").grid(row=1, column=2)
entry_data_final = tk.Entry(frame_inputs)
entry_data_final.grid(row=1, column=3)

frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

tk.Button(frame_buttons, text="Menor Preço", command=menor_preco).pack(side=tk.LEFT, padx=5)
tk.Button(frame_buttons, text="Preço Médio", command=preco_medio).pack(side=tk.LEFT, padx=5)
tk.Button(frame_buttons, text="Resumo Posto", command=resumo_posto).pack(side=tk.LEFT, padx=5)

frame_resultados = tk.Frame(root)
frame_resultados.pack(fill=tk.BOTH, expand=True)

root.mainloop()


# Grafico
import pymysql
import pandas as pd
import matplotlib.pyplot as plt

conn = pymysql.connect(
    host='localhost',  
    user='root',  
    password='',  
    database='combustiveis',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
# Criar um cursor para executar a consulta
with conn.cursor() as cursor:
    query = """
    SELECT c.data, cb.tipo, AVG(c.preco) AS preco_medio
    FROM Coleta c
    JOIN Combustivel cb ON c.id_combustivel = cb.id_combustivel
    GROUP BY c.data, cb.tipo
    ORDER BY c.data;
    """
    cursor.execute(query)
    dados = cursor.fetchall()

# Criar um DataFrame com os dados
df = pd.DataFrame(dados)

# Converter a coluna de data para formato datetime
df['data'] = pd.to_datetime(df['data'])

# Criar o gráfico
plt.figure(figsize=(10, 5))

# Gerar uma linha para cada tipo de combustível
for combustivel in df['tipo'].unique():
    df_filtrado = df[df['tipo'] == combustivel]
    plt.plot(df_filtrado['data'], df_filtrado['preco_medio'], marker='o', linestyle='-', label=combustivel)

# Configuração do gráfico
plt.xlabel('Data')
plt.ylabel('Preço Médio (R$)')
plt.title('Variação do Preço dos Combustíveis')
plt.legend()
plt.xticks(rotation=45)
plt.grid()

# Exibir o gráfico
plt.show()
