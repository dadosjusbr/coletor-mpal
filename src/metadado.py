from coleta import coleta_pb2 as Coleta


def captura():
    metadado = Coleta.Metadados()
    metadado.acesso = Coleta.Metadados.FormaDeAcesso.ACESSO_DIRETO
    metadado.extensao = Coleta.Metadados.Extensao.ODS
    # Planilhas não seguem o padrão tabular (linha sendo variável e coluna sendo valor), apresentam títulos e comentários
    metadado.estritamente_tabular = False
    metadado.formato_consistente = True
    metadado.tem_matricula = True
    metadado.tem_lotacao = True
    metadado.tem_cargo = True
    metadado.receita_base = Coleta.Metadados.OpcoesDetalhamento.DETALHADO
    metadado.despesas = Coleta.Metadados.OpcoesDetalhamento.DETALHADO
    metadado.outras_receitas = Coleta.Metadados.OpcoesDetalhamento.DETALHADO

    return metadado
