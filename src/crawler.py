import requests
import pathlib
import sys
import os
import urllib3

base_url = "https://sistemas.mpal.mp.br/transparencia/contracheque/index/"


def links_remuneration(month, year):
    links_type = {}
    link = (
        base_url
        + "65?tipo=membrosativos&mes="
        + month
        + "&ano="
        + year
        + "&busca=&download=ods"
    )

    links_type["Membros ativos"] = link
    return links_type


def links_perks_temporary_funds(month, year):
    links_type = {}
    link = (
        base_url
        + "102?tipo=verbasindenizatorias&mes="
        + month
        + "&ano="
        + year
        + "&busca=&download=ods"
    )

    links_type["Verbas Indenizatorias"] = link
    return links_type


def download(url, file_path):
    # Silence InsecureRequestWarning
    requests.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        response = requests.get(url, allow_redirects=True, verify=False)
        with open(file_path, "wb") as file:
            file.write(response.content)
        file.close()
    except Exception as excep:
        sys.stderr.write(
            "Não foi possível fazer o download do arquivo: "
            + file_path
            + ". O seguinte erro foi gerado: "
            + excep
        )
        os._exit(1)


# Crawl retrieves payment files from MPAL.
def crawl(year, month, output_path):
    urls_remuneration = links_remuneration(month, year)
    files = []

    for element in urls_remuneration:
        pathlib.Path(output_path).mkdir(exist_ok=True)
        file_name = "membros-ativos-contracheque-" + month + "-" + year + ".ods"
        file_path = output_path + "/" + file_name
        download(urls_remuneration[element], file_path)
        files.append(file_path)

    urls_perks = links_perks_temporary_funds(month, year)
    for element in urls_perks:
        pathlib.Path(output_path).mkdir(exist_ok=True)
        file_name_indemnity = (
            "membros-ativos-verbas-indenizatorias-" + month + "-" + year + ".ods"
        )

        file_path_indemnity = output_path + "/" + file_name_indemnity
        download(urls_perks[element], file_path_indemnity)
        files.append(file_path_indemnity)

    return files
