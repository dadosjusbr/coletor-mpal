# coding: utf8
import pandas as pd
import sys
import os
from coleta import coleta_pb2 as Coleta

CONTRACHEQUE = "contracheque"
INDENIZACOES = "indenizações"


HEADERS = {
    CONTRACHEQUE: {
        "Remuneração do Cargo Efetivo": 4,
        "Outras Verbas Remuneratórias, Legais ou Judiciais": 5,
        "Função de Confiança ou Cargo em Comissão": 6,
        "Gratificação Natalina": 7,
        "Férias (1/3 constitucional)": 8,
        "Abono de Permanência": 9,
        "Contribuição Previdenciária": 11,
        "Imposto de Renda": 12,
        "Retenção por Teto Constitucional": 13,
    },
    INDENIZACOES: {
        "Auxílio Saúde": 4,
        "Auxílio Alimentação": 5,
        "Auxílio Transporte": 6,
        "Auxílio Moradia": 7,
        "Férias Indenizadas": 8,
        "Férias Indenizadas de Estágio": 9,
        "Insalubridade": 10,
        "Remuneração Lei 6773": 11,
        "Remuneração Lei 6818": 12,
        "Diferença de Entrância": 13,
        "Remuneração Lei 6773 / Ato 09/2012": 14,
        "Remuneração Ato 11/2018": 15,
        "Coordenação de Grupos de Trabalho": 16,
        "Participação em Comissões e Projetos": 17,
        "Remuneração de Chefia / Direção / Assessoria": 18,
    },
}


def parse_employees(fn, chave_coleta):
    employees = {}
    counter = 1
    for row in fn:
        matricula = row[0]
        name = str(row[1]).strip()
        if (
            not is_nan(name)
            and not is_nan(matricula)
            and matricula != "0"
            and matricula != "Matrícula"
            and name != "Nome"
        ):
            membro = Coleta.ContraCheque()
            membro.id_contra_cheque = chave_coleta + "/" + str(counter)
            membro.chave_coleta = chave_coleta
            membro.nome = name
            membro.matricula = str(matricula).strip()
            membro.funcao = str(row[3]).strip()
            membro.tipo = Coleta.ContraCheque.Tipo.Value("MEMBRO")
            membro.ativo = True
            membro.remuneracoes.CopyFrom(cria_remuneracao(row, CONTRACHEQUE))
            employees[name] = membro
            counter += 1
    return employees


def cria_remuneracao(row, categoria):
    remu_array = Coleta.Remuneracoes()
    items = list(HEADERS[categoria].items())
    for i in range(len(items)):
        key, value = items[i][0], items[i][1]
        # evitando títulos das colunas
        if key != row[value]:
            remuneracao = Coleta.Remuneracao()
            remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("R")
            remuneracao.categoria = categoria
            remuneracao.item = key
            remuneracao.valor = format_value(row[value])
            remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("O")
            if categoria == CONTRACHEQUE and value in [4, 5]:
                remuneracao.tipo_receita = Coleta.Remuneracao.TipoReceita.Value("B")
            if categoria == CONTRACHEQUE and value in [11, 12, 13]:
                remuneracao.valor = remuneracao.valor * (-1)
                remuneracao.natureza = Coleta.Remuneracao.Natureza.Value("D")

            remu_array.remuneracao.append(remuneracao)
    return remu_array


def update_employees(fn, employees, categoria):
    for row in fn:
        matricula = str(row[0]).strip()
        name = str(row[1]).strip()
        if (
            not is_nan(name)
            and not is_nan(matricula)
            and matricula != "0"
            and matricula != "Matrícula"
            and name != "Nome"
        ):
            if name in employees.keys():
                emp = employees[name]
                emp.matricula = matricula
                remu = cria_remuneracao(row, categoria)
                emp.remuneracoes.MergeFrom(remu)
                employees[name] = emp
    return employees


def parse(data, chave_coleta):
    employees = {}
    folha = Coleta.FolhaDePagamento()
    try:
        employees.update(parse_employees(data.contracheque, chave_coleta))
        update_employees(data.indenizatorias, employees, INDENIZACOES)

    except KeyError as e:
        sys.stderr.write(
            "Registro inválido ao processar contracheque ou indenizações: {}".format(e)
        )
        os._exit(1)
    for i in employees.values():
        folha.contra_cheque.append(i)
    return folha


def is_nan(string):
    return string != string


def format_value(element):
    # A value was found with incorrect formatting. (3,045.99 instead of 3045.99)
    if is_nan(element):
        return 0.0
    if type(element) == str:
        if "." in element and "," in element:
            element = element.replace(".", "").replace(",", ".")
        elif "," in element:
            element = element.replace(",", ".")
        elif "-" in element:
            element = 0.0

    return float(element)
