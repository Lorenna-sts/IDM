import pandas as pd
import os
import unicodedata
import sys

# Configuração para evitar erros de print no terminal
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def normalizar_texto(texto):
    """Limpa acentos e espaços para garantir que nomes de cidades batam 100%"""
    if pd.isna(texto) or texto == "":
        return ""
    texto = str(texto).replace('\ufeff', '').replace('ï»¿', '')
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').lower().strip()

def converter_para_float(valor):
    """Converte qualquer bagunça (texto com vírgula, ponto, etc) para número real"""
    if pd.isna(valor):
        return None
    if isinstance(valor, (float, int)):
        return float(valor)
    
    # Tratamento de string
    s = str(valor).strip()
    if not s:
        return None
    
    # Se tiver vírgula e ponto (ex: 1.234,56), remove ponto e troca vírgula
    if ',' in s and '.' in s:
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.')
        
    try:
        return float(s)
    except:
        return None

def transferir_dados_idm_final():
    caminho_origem = r"CAMINHO DO ARQUIVO"
    caminho_destino = r"CAMINHO DO ARQUIVO"

    print("--- INICIANDO IMPORTAÇÃO COM 2 CASAS DECIMAIS ---")
    
    # 1. Carregar Excel de Origem
    print("1. Lendo arquivo de Origem...")
    try:
        df_dados = pd.read_excel(caminho_origem, sheet_name='Dados')
        df_var_cod = pd.read_excel(caminho_origem, sheet_name='Var_Cod')
    except Exception as e:
        print(f"ERRO: Não foi possível ler o Excel. {e}")
        return

    # 2. Carregar CSV de Destino
    print("2. Lendo arquivo de Destino...")
    df_destino = None
    try:
        # Tenta ler como UTF-8-SIG (o correto)
        df_destino = pd.read_csv(caminho_destino, sep=';', decimal=',', encoding='utf-8-sig')
    except:
        try:
            # Fallback para Latin-1
            df_destino = pd.read_csv(caminho_destino, sep=';', decimal=',', encoding='latin-1')
        except Exception as e:
            print(f"ERRO CRÍTICO: Não consegui abrir o arquivo CSV. {e}")
            return

    # --- LIMPEZA E PADRONIZAÇÃO DO ARQUIVO EXISTENTE ---
    print("3. Saneando dados antigos...")
    
    # Identificar colunas corretas
    col_map = {}
    for col in df_destino.columns:
        norm = normalizar_texto(col)
        if 'municipio' in norm: col_map[col] = 'Município'
        if 'loc_cod' in norm: col_map[col] = 'loc_cod'
        if 'var_cod' in norm: col_map[col] = 'var_cod'
        if 'd_2024' in norm or 'valor' in norm: col_map[col] = 'd_2024'
    
    df_destino = df_destino.rename(columns=col_map)
    
    # Converter valores antigos para float puro para poder formatar depois
    if 'd_2024' in df_destino.columns:
        df_destino['d_2024'] = df_destino['d_2024'].apply(converter_para_float)

    # Criar Mapa de Municípios
    df_destino['munic_key'] = df_destino['Município'].apply(normalizar_texto)
    mapa_loc = df_destino.dropna(subset=['loc_cod']).set_index('munic_key')['loc_cod'].to_dict()

    # --- PREPARAR NOVOS DADOS ---
    print("4. Processando novos dados do Excel...")
    
    # Preparar mapeamento de variáveis
    df_dados.columns = df_dados.columns.str.strip()
    df_var_cod['Des_var'] = df_var_cod['Des_var'].astype(str).str.strip()
    
    # Converter códigos para número
    df_var_cod['var_cod_clean'] = pd.to_numeric(df_var_cod['var_cod'], errors='coerce')
    df_vars_validas = df_var_cod.dropna(subset=['var_cod_clean']).copy()
    df_vars_validas['var_cod_final'] = df_vars_validas['var_cod_clean'].astype(int)
    
    mapa_vars = dict(zip(df_vars_validas['Des_var'], df_vars_validas['var_cod_final']))

    # Transformar colunas em linhas (Melt)
    cols_presentes = [c for c in df_dados.columns if c in mapa_vars]
    df_melt = df_dados.melt(id_vars=['munic'], value_vars=cols_presentes, var_name='variavel', value_name='d_2024')

    # Aplicar os códigos
    df_melt['var_cod'] = df_melt['variavel'].map(mapa_vars)
    df_melt['munic_key'] = df_melt['munic'].apply(normalizar_texto)
    df_melt['loc_cod'] = df_melt['munic_key'].map(mapa_loc)

    # Filtrar dados válidos
    df_novos = df_melt.dropna(subset=['loc_cod', 'var_cod', 'd_2024']).copy()
    
    # Padronizar colunas dos novos dados
    df_novos = df_novos.rename(columns={'munic': 'Município'})
    df_novos = df_novos[['Município', 'loc_cod', 'var_cod', 'd_2024']]
    
    # Garantir tipagem
    df_novos['loc_cod'] = df_novos['loc_cod'].astype(int)
    df_novos['var_cod'] = df_novos['var_cod'].astype(int)
    df_novos['d_2024'] = df_novos['d_2024'].astype(float)

    print(f"   > {len(df_novos)} novos registros preparados.")

    # --- CONSOLIDAÇÃO ---
    print("5. Consolidando e Salvando...")
    
    # Remover colunas auxiliares do destino antes de juntar
    cols_finais = ['Município', 'loc_cod', 'var_cod', 'd_2024']
    df_destino_limpo = df_destino[cols_finais].copy()
    
    # Concatenar (Antigos + Novos)
    df_final = pd.concat([df_destino_limpo, df_novos], ignore_index=True)
    
    # REMOVER DUPLICADOS (Prioridade para o dado NOVO)
    df_final = df_final.drop_duplicates(subset=['loc_cod', 'var_cod'], keep='last')

    # Ordenar
    df_final = df_final.sort_values(by=['Município', 'var_cod'])

    # --- SALVAMENTO COM 2 CASAS DECIMAIS ---
    try:
        # float_format='%.2f' -> Força exatas 2 casas decimais (ex: 2,70)
        df_final.to_csv(caminho_destino, 
                        sep=';', 
                        decimal=',', 
                        index=False, 
                        encoding='utf-8-sig',
                        float_format='%.2f') 
                        
        print(f"SUCESSO! Arquivo salvo em: {caminho_destino}")
        print("NOTA: Todos os valores foram formatados com 2 casas decimais após a vírgula.")
        
    except PermissionError:
        print("ERRO: O arquivo está aberto no Excel. Feche-o e tente novamente.")

if __name__ == "__main__":

    transferir_dados_idm_final()
