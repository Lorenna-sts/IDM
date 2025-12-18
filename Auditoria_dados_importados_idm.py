import pandas as pd
import unicodedata
import sys

# Ajuste de encoding para o terminal
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def normalizar(texto):
    if not isinstance(texto, str): return str(texto)
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').lower().strip()

def auditar_dados():
    caminho_origem = r"CAMINHO DO ARQUIVO"
    caminho_destino = r"CAMINHO DO ARQUIVO"

    print("--- AUDITORIA DE DADOS (TIRA-TEIMA) ---")
    
    # 1. Carregar Origem
    print("Lendo Excel de Origem...")
    df_dados = pd.read_excel(caminho_origem, sheet_name='Dados')
    # Limpar colunas
    df_dados.columns = df_dados.columns.str.strip()
    
    # Criar coluna normalizada para busca
    df_dados['munic_norm'] = df_dados['munic'].apply(normalizar)

    # 2. Carregar Destino
    print("Lendo CSV de Destino...")
    try:
        df_destino = pd.read_csv(caminho_destino, sep=';', decimal=',', encoding='utf-8-sig')
    except:
        df_destino = pd.read_csv(caminho_destino, sep=';', decimal=',', encoding='latin-1')

    # Identificar colunas no destino
    col_munic_dest = next((c for c in df_destino.columns if 'municipio' in normalizar(c)), None)
    
    if not col_munic_dest:
        print("Erro: Não achei a coluna Município no CSV.")
        return

    df_destino['munic_norm'] = df_destino[col_munic_dest].apply(normalizar)

    # --- PERGUNTA INTERATIVA ---
    cidade_alvo = "Abadia de Goiás" # Padrão, mas vamos tentar achar o que o usuário quer
    print(f"\nExemplo de cidade no banco: {df_dados['munic'].iloc[0]}")
    busca = input("Digite o nome de um município para conferir (ou Enter para 'Abadia de Goiás'): ").strip()
    if not busca:
        busca = "Abadia de Goiás"
    
    busca_norm = normalizar(busca)

    # Buscar na Origem
    row_origem = df_dados[df_dados['munic_norm'] == busca_norm]
    if row_origem.empty:
        print(f"❌ Município '{busca}' não encontrado na aba Dados do Excel!")
        return
    
    # Buscar no Destino
    rows_destino = df_destino[df_destino['munic_norm'] == busca_norm]
    if rows_destino.empty:
        print(f"❌ Município '{busca}' não encontrado no CSV de destino!")
        return

    print(f"\n--- RELATÓRIO PARA: {row_origem['munic'].values[0]} ---")
    
    # Pegar algumas variáveis chave para comparar
    # Vamos pegar pib_pc_10 (cod 696) e IDM_economia (cod 692) como exemplo, ou o que tiver
    vars_teste = {
        'IDM_economia': 692,
        'pib_pc_10': 696,
        'IDM_infra': 707
    }

    print(f"{'VARIÁVEL':<20} | {'VALOR EXCEL (Origem)':<25} | {'VALOR CSV (Destino)':<25} | {'STATUS'}")
    print("-" * 85)

    for nome_var, cod_var in vars_teste.items():
        # Valor Origem
        if nome_var in row_origem.columns:
            val_orig = row_origem[nome_var].values[0]
        else:
            val_orig = "N/A (Col não existe)"

        # Valor Destino (procurar na linha onde var_cod == cod_var)
        row_dest_var = rows_destino[rows_destino['var_cod'] == cod_var]
        
        if not row_dest_var.empty:
            val_dest = row_dest_var['d_2024'].values[0]
        else:
            val_dest = "N/A (Não gravou)"

        # Comparação (Arredondando para evitar erro de float 0.0000001)
        match = "✅ IGUAL"
        try:
            if abs(float(val_orig) - float(str(val_dest).replace(',', '.'))) > 0.001:
                match = "⚠️ DIVERGENTE"
        except:
            match = "?"

        print(f"{nome_var:<20} | {str(val_orig):<25} | {str(val_dest):<25} | {match}")

    print("-" * 85)
    print("\nOBSERVAÇÃO:")
    print("Se o STATUS for '✅ IGUAL', mas no Excel você vê diferente, é porque o Excel")
    print("está abrindo o CSV interpretando o ponto/vírgula de forma errada.")
    print("DICA: Abra o CSV clicando com botão direito -> Abrir com -> Bloco de Notas para ver o real.")

if __name__ == "__main__":

    auditar_dados()
