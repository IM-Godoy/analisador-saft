def processar_documento_universal(file_bytes, filename):
    filename_lower = filename.lower()
    
    # 1. Validação de Ficheiros Inválidos Óbvios (Ex: Currículos, Imagens puras, etc.)
    if any(k in filename_lower for k in ['curriculo', 'cv', 'bio', 'foto', 'imagem']):
        raise ValueError("O documento carregado parece ser um currículo ou ficheiro pessoal e não um registo comercial de vendas.")

    # 2. Se for SAF-T XML
    if filename_lower.endswith('.xml'):
        try:
            return processar_saft_xml(file_bytes)
        except Exception as e:
            raise ValueError(f"O ficheiro XML SAF-T não é válido ou está corrompido: {e}")

    # 3. Se for Excel ou CSV
    if filename_lower.endswith(('.xlsx', '.xls', '.csv')):
        try:
            if filename_lower.endswith('.xlsx'):
                df_raw = pd.read_excel(io.BytesIO(file_bytes))
            elif filename_lower.endswith('.xls'):
                df_raw = pd.read_excel(io.BytesIO(file_bytes), engine='xlrd')
            else:
                try:
                    df_raw = pd.read_csv(io.BytesIO(file_bytes), encoding='utf-8', sep=None, engine='python')
                except Exception:
                    df_raw = pd.read_csv(io.BytesIO(file_bytes), encoding='latin1', sep=None, engine='python')

            # Verificar se tem colunas minimamente comerciais
            colunas_texto = " ".join([str(c).lower() for c in df_raw.columns])
            if not any(k in colunas_texto for k in ['cliente', 'fatura', 'data', 'valor', 'total', 'net', 'iva', 'preco']):
                raise ValueError("A tabela carregada não possui colunas reconhecíveis de faturação (ex: Cliente, Fatura, Valor).")

            col_map = {}
            for col in df_raw.columns:
                col_lower = str(col).lower().strip()
                if any(k in col_lower for k in ['cliente', 'nome', 'customer', 'entidade', 'empresa']):
                    col_map[col] = 'Cliente'
                elif any(k in col_lower for k in ['fatura', 'doc', 'documento', 'invoice', 'numero', 'nº']):
                    col_map[col] = 'Documento'
                elif any(k in col_lower for k in ['data', 'date', 'emissao', 'dia']):
                    col_map[col] = 'Data'
                elif any(k in col_lower for k in ['bruto', 'total', 'gross', 'valor total']):
                    col_map[col] = 'ValorBruto'
                elif any(k in col_lower for k in ['liquido', 'net', 'base', 'valor sem iva']):
                    col_map[col] = 'ValorLiquido'
                elif any(k in col_lower for k in ['iva', 'imposto', 'tax']):
                    col_map[col] = 'Imposto'
                elif any(k in col_lower for k in ['tipo', 'type', 'documenttype']):
                    col_map[col] = 'Tipo'

            df_raw = df_raw.rename(columns=col_map)

            if 'ValorBruto' not in df_raw.columns:
                raise ValueError("O documento não contém uma coluna de valores válidos para análise.")

            for col in ['ValorBruto', 'ValorLiquido', 'Imposto']:
                if col in df_raw.columns:
                    df_raw[col] = pd.to_numeric(df_raw[col].astype(str).str.replace('€', '').str.replace(' ', '').str.replace(',', '.'), errors='coerce').fillna(0.0)

            dados_faturas = []
            for _, row in df_raw.iterrows():
                doc_type = str(row.get('Tipo', 'FT')).upper()
                if 'NC' in doc_type or ('NOTA' in doc_type and 'CREDITO' in doc_type):
                    doc_type = 'NC'
                else:
                    doc_type = 'FT'

                vb = float(row.get('ValorBruto', 0))
                if vb <= 0:
                    continue # Ignorar linhas inválidas ou zeradas

                vl = float(row.get('ValorLiquido', vb / 1.23))
                imp = float(row.get('Imposto', vb - vl))

                if doc_type == 'NC':
                    vb = -abs(vb)
                    vl = -abs(vl)
                    imp = -abs(imp)

                dados_faturas.append({
                    'Documento': str(row.get('Documento', 'DOC-01')),
                    'Tipo': doc_type,
                    'Data': str(row.get('Data', '2026-01-01'))[:10],
                    'Cliente': str(row.get('Cliente', 'Cliente Desconhecido')),
                    'ValorBruto': vb,
                    'ValorLiquido': vl,
                    'Imposto': imp
                })

            if not dados_faturas:
                raise ValueError("Nenhum registo de venda válido foi encontrado no documento.")

            df_final = pd.DataFrame(dados_faturas)
            df_tax_final = pd.DataFrame([{
                'TaxCode': 'NOR',
                'TaxRate': 23.0,
                'Base': abs(df_final['ValorLiquido'].sum()),
                'ValorIVA': abs(df_final['Imposto'].sum())
            }])
            return df_final, df_tax_final
        except Exception as e:
            raise ValueError(f"Erro ao processar tabela: {e}")

    # 4. Bloquear ficheiros de texto/PDF soltos que não sejam relatórios estruturados
    raise format_error if False else ValueError("Formato não suportado. Por favor utilize um ficheiro SAF-T (.xml), Excel (.xlsx) ou CSV de vendas.")
