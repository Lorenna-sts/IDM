import pandas as pd

def diagnosticar_problemas_idm():
    caminho_origem = r"Z:\GEDE\BDE - Banco de Dados\Banco de Informações\IDM\IDM 2024\idm_panel_com_dimensoes.xlsx"

    print(f"--- DIAGNÓSTICO DO ARQUIVO: {os.path.basename(caminho_origem)} ---\n")
    
    try:
        df_dados = pd.read_excel(caminho_origem, sheet_name='Dados')
        df_var_cod = pd.read_excel(caminho_origem, sheet_name='Var_Cod')
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return

    # Normalizar nomes para comparação (remover espaços extras)
    colunas_dados = set(df_dados.columns.str.strip())
    
    # 1. Verificar Variáveis sem Código Numérico (Causa Principal)
    print("1. VARIÁVEIS COM CÓDIGO VAZIO OU INVÁLIDO NA ABA 'Var_Cod':")
    print("(Estas variáveis existem na lista, mas não têm número identificador)")
    
    # Tenta converter para numérico, o que falhar vira NaN
    df_var_cod['var_cod_num'] = pd.to_numeric(df_var_cod['var_cod'], errors='coerce')
    
    # Filtra onde é nulo/vazio
    vars_sem_cod = df_var_cod[df_var_cod['var_cod_num'].isna()]
    
    if not vars_sem_cod.empty:
        for index, row in vars_sem_cod.iterrows():
            print(f"   - Variável: '{row['Des_var']}' | Valor atual em var_cod: '{row['var_cod']}'")
    else:
        print("   Nenhuma encontrada.")
    
    print("\n" + "-"*50 + "\n")

    # 2. Verificar Discrepância de Nomes (Dados vs Var_Cod)
    print("2. VARIÁVEIS QUE TÊM CÓDIGO, MAS O NOME NÃO BATE COM A ABA 'Dados':")
    print("(O código existe, mas o script não encontra a coluna correspondente)")
    
    # Pegar apenas as que TEM código válido
    df_com_cod = df_var_cod.dropna(subset=['var_cod_num'])
    vars_validas_nomes = set(df_com_cod['Des_var'].str.strip())
    
    # Ver quais dessas NÃO estão nas colunas da aba Dados
    nao_encontradas = vars_validas_nomes - colunas_dados
    
    if nao_encontradas:
        for var in nao_encontradas:
            print(f"   - '{var}' (Existe em Var_Cod com ID, mas não existe coluna na aba Dados)")
    else:
        print("   Todas as variáveis com código foram encontradas na aba Dados.")

    print("\n" + "-"*50 + "\n")
    print("CONCLUSÃO:")
    print("As variáveis listadas no item 1 precisam receber um número na coluna 'var_cod' do Excel.")
    print("As variáveis do item 2 precisam ter o nome corrigido para ficarem idênticas nas duas abas.")

if __name__ == "__main__":
    import os
    diagnosticar_problemas_idm()