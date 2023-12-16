# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 09:38:47 2023

@author: BRUNO
"""

import streamlit as st
import pandas as pd
import os
import numpy as np
import time
import matplotlib.pyplot as plt


st.set_page_config(page_title="Avaliação de consumo de nutrientes", page_icon="hospital", layout="wide")

sub_dir = './parcial' # Diretório onde estão os arquivos de dieta
#sub_dir = '\dietas2' # Diretório onde estão os arquivos de dieta
#diretorio = os.getcwd() + sub_dir
#diretorio = os.getcwd()
#os.listdir(diretorio)
#k = os.listdir(diretorio)
k = os.listdir(sub_dir)


st.title("Avaliação de consumo de nutrientes  :hospital:")
st.header(f"BASE DE DADOS UTILIZADA: {sub_dir}")

col11, col22, col33 = st.columns(3)
#PESO DO PACIENTE
peso_paciente = col11.number_input("Peso do paciente, em kg", 30.0)
#QUANTIDADE DE CALORIAS POR KG:
qtde_calorias = col22.number_input("Calorias por kg", 20.0)
#QUANTIDADE DE PROTEINA POR KG:
qtde_proteina = col33.number_input("Proteína por kg", 0.80)    



#NECESSIDADE CALORICA
nec_calorica = peso_paciente * qtde_calorias
col11.write(f"Necessidade calórica: {nec_calorica}")

#NECESSIDADE PROTEICA
nec_proteica = peso_paciente * qtde_proteina
col22.write(f"Necessidade proteica: {nec_proteica}")



# Carregar arquivo Excel com as correções
correcoes = pd.read_excel('dicionario.xlsx', header=None, usecols='A:B', names=["INCORRETO", "CORRETO"], index_col="INCORRETO")

# Criar um dicionário com todas as dietas
todas_dietas = {}
for arquivo in k:
    # Ignorar arquivos que não são do tipo xlsx
    if not arquivo.endswith(".xlsx"):
        continue
    
    # Ler o arquivo como um dataframe do Pandas
    #df = pd.read_excel(os.path.join(diretorio, arquivo), header=None, names=["REFEIÇÃO", "CARDÁPIO","DETALHAMENTO", "PER_CAPITA" ])
    df = pd.read_excel(os.path.join(sub_dir, arquivo), header=None, names=["REFEIÇÃO", "CARDÁPIO","DETALHAMENTO", "PER_CAPITA" ])
    
    # Fazer as correções nas descrições incorretas
    df['DETALHAMENTO'] = df['DETALHAMENTO'].replace(correcoes['CORRETO'])      
            
    # criar um dicionário vazio para armazenar os dados
    refeicoes = {}
    
    # iterar sobre as linhas do dataframe e adicionar cada refeição ao dicionário
    for i, row in df.iterrows():
        refeicao = row['REFEIÇÃO']
        cardapio = row['CARDÁPIO']
        detalhamento = row['DETALHAMENTO']
        per_capita = row['PER_CAPITA']
        
        if refeicao not in refeicoes:
            refeicoes[refeicao] = {}
            
        if cardapio not in refeicoes[refeicao]:
            refeicoes[refeicao][cardapio] = {}
        
        refeicoes[refeicao][cardapio][detalhamento] = per_capita
        
        # Adicionar o dicionário das refeições da dieta ao dicionário de todas as dietas        
        todas_dietas[arquivo.split('.')[0]] = refeicoes

# Selecionar o tipo de dieta
dieta = st.selectbox("Selecione a dieta", list(todas_dietas.keys()), index=1)

with st.container(): #são sempre 6, mas alguma pode ficar vazia
    #quantidade de refeicoes, de acordo com a dieta selecionada
    num_refeicoes = len(list(todas_dietas[dieta].keys()))
    
    st.write("This is inside the container")
    col1, col2 = st.columns(2)    
    count = 0
    
    # Filtrar os dados para exibir apenas os itens selecionados
    dados_selecionados = {}
    # Cria um dicionário para armazenar a quantidade de cada comida selecionada
    quantidades2 = {}
    
    for i in range(1, num_refeicoes):         
        # Selecionar o tipo de refeição (condicionado à dieta selecionada)
        #refeicao = col1.selectbox("Selecione a refeição", list(todas_dietas[dieta].keys()),  key="ref" + str(count), index=i, disabled=1)        
        refeicao = list(todas_dietas[dieta].keys())[i]
        count += 1 
        # Selecionar múltiplos itens no cardápio (condicionado ao tipo de refeição selecionado)
        itens = col1.multiselect(f"Selecione os itens do {refeicao}", list(todas_dietas[dieta][refeicao].keys()), max_selections=6,  key= count)       
        #default = list(todas_dietas[dieta][refeicao].keys())[0] pega o 1º item da lista pra vir já preenchido
        count += 1 
        
        # Adicionar os itens selecionados no dicionário dados_selecionados
        for item in itens:
            dados_selecionados[item] = todas_dietas[dieta][refeicao][item]
            
            #calcular o peso da porção, que é a soma dos pesos dos alimentos
            peso_total = 0.0
            for nome, peso in dados_selecionados[item].items():
                peso_total = peso_total + peso
            
            # Adicionar o valor de peso_total ao dicionário dados_selecionados[item]
            dados_selecionados[item]["peso_total"] = peso_total
    
            # qtd = st.number_input(f"Quantidade de {item} do {refeicao} (em gramas):", min_value=peso_total, value=peso_total, key= count, step=1.0)               
            # quantidades2[item] = {"quantidade": qtd, "peso_total": peso_total}
            # count += 1
            
    for comida in dados_selecionados:
        quantidade_minima = dados_selecionados[comida]["peso_total"]                
        quantidade = st.number_input(f"Digite a quantidade desejada para {comida}: (mínimo de {quantidade_minima} gramas)",min_value=0.0, value=quantidade_minima, key= count, step=1.0)
        quantidades2[comida] = quantidade
        count += 1 

    


# # Exibir os detalhes e o per_capita dos itens selecionados
st.write("Detalhes dos itens selecionados:")
with st.expander("Detalhes dos itens selecionados"): 
     for comida, detalhes in dados_selecionados.items():
         st.write("- **{}:** {}".format(comida, detalhes))

# # Lê o arquivo Excel com a Tabela TACO 2011
taco = pd.read_excel("taco_2011.xls", header=0, usecols='B:S', skiprows=2, nrows=597)

# Define as colunas a serem tratadas
#colunas_numericas = ["Proteína (g)", "Energia, kcal", "Potássio (mg)", "Fibra", "Sódio (mg)"]

# Loop para percorrer as colunas e aplicar as transformações necessárias
#for coluna in colunas_numericas:
    # Substitui "Tr" por vazio e "NA" por NaN na coluna
    #taco[coluna] = taco[coluna].replace({"Tr": "", "NA": np.nan})
    
    # Converte os valores da coluna para numéricos e substitui valores não numéricos por NaN
    #taco[coluna] = pd.to_numeric(taco[coluna], errors="coerce")
    
    # Substitui NaN por zero na coluna
    #taco[coluna] = taco[coluna].fillna(value=0)

# # Cria um dicionário com os dados da tabela para cada comida
comidas_taco = {}
for index, row in taco.iterrows():
     comidas_taco[row["Alimento"]] = {"proteína": row["Proteína (g)"], 
                                      "energia": row["Energia, kcal"], 
                                      "potássio": row["Potássio (mg)"],
                                      "fibra": row["Fibra"],
                                      "sódio": row["Sódio (mg)"]
                                      }

total_proteina_refeicoes = {}

for refeicao, ingredientes in dados_selecionados.items(): #key é o cardápio; value é o dict alimento:per_capita
  total_proteina_refeicao = 0
  for ingrediente, quantidade in ingredientes.items(): #key é o alimento; value é o per_capita
    #st.write(ingrediente)
    if ingrediente != "peso_total": #porque em ingredientes.keys tem os alimentos mas tem 'peso_total' tambem
        #st.write("quantidade de proteína em 100g de ", ingrediente, ": ", comidas_taco[ingrediente]["proteína"]) 
        #print(quantidades2[refeicao]) #quantidade digitada para a refeicao
        #print(dados_selecionados[refeicao]["peso_total"]) #peso total da porção da refeicao
        #st.write("considerando a quantidade per capita de", quantidade) #variável quantidade tá fixa nesse loop
        #st.write("a quantidade de proteína do alimento", ingrediente, "é:")
        #st.write(quantidades2[refeicao], "/", dados_selecionados[refeicao]["peso_total"], "X", comidas_taco[ingrediente]["proteína"], "/100g x", quantidade)
        #st.write("= ", quantidades2[refeicao] / dados_selecionados[refeicao]["peso_total"] * comidas_taco[ingrediente]["proteína"] /100 * quantidade)       
        total_proteina_refeicao += quantidades2[refeicao] / dados_selecionados[refeicao]["peso_total"] * comidas_taco[ingrediente]["proteína"] /100 * quantidade
        total_proteina_refeicoes[refeicao] = total_proteina_refeicao

#st.write(total_proteina_refeicoes) #separado por refeição!
#AGOOOORRA TÁ CERTO

total_energia_refeicoes = {}
for refeicao, ingredientes in dados_selecionados.items(): #key é o cardápio; value é o dict alimento:per_capita
  total_energia_refeicao = 0
  for ingrediente, quantidade in ingredientes.items(): #key é o alimento; value é o per_capita    
    if ingrediente != "peso_total": #porque em ingredientes.keys tem os alimentos mas tem 'peso_total' tambem        
        total_energia_refeicao += quantidades2[refeicao] / dados_selecionados[refeicao]["peso_total"] * comidas_taco[ingrediente]["energia"] /100 * quantidade
        total_energia_refeicoes[refeicao] = total_energia_refeicao

total_potassio_refeicoes = {}
for refeicao, ingredientes in dados_selecionados.items(): #key é o cardápio; value é o dict alimento:per_capita
  total_potassio_refeicao = 0
  for ingrediente, quantidade in ingredientes.items(): #key é o alimento; value é o per_capita    
    if ingrediente != "peso_total": #porque em ingredientes.keys tem os alimentos mas tem 'peso_total' tambem        
        total_potassio_refeicao += quantidades2[refeicao] / dados_selecionados[refeicao]["peso_total"] * comidas_taco[ingrediente]["potássio"] /100 * quantidade
        total_potassio_refeicoes[refeicao] = total_potassio_refeicao

total_fibra_refeicoes = {}
for refeicao, ingredientes in dados_selecionados.items(): #key é o cardápio; value é o dict alimento:per_capita
  total_fibra_refeicao = 0
  for ingrediente, quantidade in ingredientes.items(): #key é o alimento; value é o per_capita    
    if ingrediente != "peso_total": #porque em ingredientes.keys tem os alimentos mas tem 'peso_total' tambem        
        total_fibra_refeicao += quantidades2[refeicao] / dados_selecionados[refeicao]["peso_total"] * comidas_taco[ingrediente]["fibra"] /100 * quantidade
        total_fibra_refeicoes[refeicao] = total_fibra_refeicao

total_sodio_refeicoes = {}
for refeicao, ingredientes in dados_selecionados.items(): #key é o cardápio; value é o dict alimento:per_capita
  total_sodio_refeicao = 0
  for ingrediente, quantidade in ingredientes.items(): #key é o alimento; value é o per_capita    
    if ingrediente != "peso_total": #porque em ingredientes.keys tem os alimentos mas tem 'peso_total' tambem        
        total_sodio_refeicao += quantidades2[refeicao] / dados_selecionados[refeicao]["peso_total"] * comidas_taco[ingrediente]["sódio"] /100 * quantidade
        total_sodio_refeicoes[refeicao] = total_sodio_refeicao
        



#Para somar os valores de proteína de todas as refeições, é só usar o sum
soma_proteina = sum(total_proteina_refeicoes.values())
#st.write(f"Total Proteína: {soma_proteina:.2f}g")

#Para somar os valores de energia de todas as refeições, é só usar o sum
soma_energia = sum(total_energia_refeicoes.values())
#st.write(f"Total Calorias: {soma_energia:.2f}g")

#Para somar os valores de potássio de todas as refeições, é só usar o sum
soma_potassio = sum(total_potassio_refeicoes.values())
#st.write(f"Total Potássio: {soma_potassio:.2f}g")

#Para somar os valores de fibra de todas as refeições, é só usar o sum
soma_fibra = sum(total_fibra_refeicoes.values())
#st.write(f"Total Fibras: {soma_fibra:.2f}g")

#Para somar os valores de sódio de todas as refeições, é só usar o sum
soma_sodio = sum(total_sodio_refeicoes.values())
#st.write(f"Total Sódio: {soma_sodio:.2f}g")


recebido_calorias = soma_energia / nec_calorica
recebido_proteina = soma_proteina / nec_proteica
recebido_fibra = soma_fibra / 25.0
recebido_sodio = soma_sodio / 2000.0

st.header("TOTAIS")

col111, col222 = st.columns(2)
col111.write(f"- Proteína: {soma_proteina:.2f} g, que é {recebido_proteina:.2%} da necessidade proteica")
col111.write(f"- Energia: {soma_energia:.2f} kcal, que é {recebido_calorias:.2%} da necessidade calorica")
col111.write(f"- Potássio: {soma_potassio:.2f} mg")
col111.write(f"- Fibra: {soma_fibra:.2f} g, que é {recebido_fibra:.2%} da necessidade diária")
col111.write(f"- Sódio: {soma_sodio:.2f} g, que é {recebido_sodio:.2%} da necessidade diária")

#quantidades reais em cada dicionário
total_nutrientes_percent = pd.DataFrame(
    [recebido_calorias, recebido_proteina, recebido_fibra, recebido_sodio], 
    index=['Calorias', 'proteínas', 'Fibras', 'Sódio'])



# cria o gráfico de barras
col222.bar_chart(total_nutrientes_percent * 100)

cola1, cola2 = st.columns(2)
# Pergunta o nome do alimento
alimento_busca = cola1.text_input("Digite o nome do alimento: ")

# Cria uma lista para armazenar as refeições que contêm o alimento
refeicoes_com_alimento = []

# Itera sobre cada item do dicionário
for x, alimentos in todas_dietas.items():
    #st.write(x)
    #st.write(alimentos)
    for z, p in alimentos.items():
        #st.write(z)
        for a, b in p.items():
            #st.write(b)
            for vv, vz in b.items():
                #st.write(vv)
                # Verifica se o alimento está presente na lista de alimentos da refeição
                if alimento_busca in vv:
                    # Se estiver, adiciona o nome da refeição à lista de refeições com o alimento
                    refeicoes_com_alimento.append(a) #é uma lista


def procura():    
    #st.write(refeicoes_com_alimento)
    #st.write(type((refeicoes_com_alimento)))
    for cardapio in refeicoes_com_alimento:
        #st.write("- **{}**".format(cardapio))
        st.write(f"- {cardapio}")

cola2.write(" ")
cola2.write(" ")
if cola2.button('Busca'):
    st.write("Relação de refeições com o alimento selecionado:")
    result = procura()
