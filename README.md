
# 📊 Automação de Carga de Dados - IDM (Índice de Desempenho Municipal)

Este repositório contém um conjunto de scripts em Python desenvolvidos para automatizar o processo de Extração, Transformação e Carga (ETL) dos dados do **IDM 2024** para o **Banco de Dados Estatístico (BDE)**.

O fluxo garante a padronização de codificações, formatação decimal e integridade referencial entre a planilha de origem (Excel) e a base histórica (CSV).

---

## 📂 Estrutura dos Arquivos

O projeto é composto por três scripts principais, que devem ser utilizados em uma ordem lógica de verificação e execução:

### 1. `diagnostico_problemas_idm.py` 🩺
**O "Check-up" dos dados.**
Antes de tentar importar, execute este script. Ele varre o Excel de origem para identificar inconsistências comuns que quebram a importação.
* **Verifica:** Variáveis na aba `Var_Cod` que estão sem número identificador (`var_cod`).
* **Verifica:** Discrepâncias de nomes entre as colunas da aba `Dados` e os nomes registrados na aba `Var_Cod`.

### 2. `ImportbaseIDM_BDE.py` 🚀
**O Motor de Carga.**
Este é o script principal que realiza a transferência dos dados.
* **Leitura:** Carrega o Excel de origem e o CSV de destino (suporta UTF-8 e Latin-1).
* **Transformação (Melt):** Transforma os dados de formato "Largo" (colunas por variável) para formato "Longo" (linhas por variável), padrão do BDE.
* **Limpeza:** Normaliza nomes de municípios (remove acentos e espaços) para garantir o "match".
* **Consolidação:** Mescla dados novos com antigos, atualizando registros existentes e preservando o histórico.
* **Saída:** Salva o arquivo final com formatação estrita (separador `;`, decimal `,`, 2 casas decimais).

### 3. `Auditoria_dados_importados_idm.py` 🔍
**O Tira-Teima.**
Ferramenta para conferência amostral pós-importação.
* Permite buscar um município específico (interativo).
* Compara lado a lado o valor original no Excel vs. o valor gravado no CSV.
* Calcula diferenças de arredondamento para validar a precisão dos dados.

---

## ⚙️ Pré-requisitos

* **Python 3.x** instalado.
* Biblioteca **Pandas** e **OpenPyXL**.

Para instalar as dependências:
```bash
pip install pandas openpyxl
