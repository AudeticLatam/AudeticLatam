# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 10:11:18 2021

@author: Andrés Amparo
@Email: aamparo@audetic.ec
"""

import re #Libreria de manejo de expresiones regulares
#Manejo de procesammiento de lenguaje natural (PLN)
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import nltk
import spacy_udpipe as udpipe
#Manejo de codigo html para proceso de scrapping
import requests
from scrapy import Selector
#Manejo de data frames y arreglos numpy
import pandas as pd
import numpy as np

#nltk.download('punkt')
nltk.download('stopwords') #Descargas de stopwords en español
udpipe.download('es') #Descarga modelo de PLN
nlp_model_es = udpipe.load('es') #Carga de modelo PLN

#Carga de archivo de texto a analizar
with open('meeting_saved_chat.txt', encoding='utf-8') as f:
    contents = f.read()
    
#Funcion para validacion de digito verificador cedula de Ecuador
def ValidaCedula(cedula):
    
    suma = 0
    
    longitud = len(cedula)
    
    if longitud != 10:
        return False
    else:
        for i in range(longitud-1):
            digito = int(cedula[i])
            if (i+1) % 2 == 0:
                mul = digito*1
            else:
                mul = digito*2
            
            if mul >= 10:
                mul = mul - 9
                
            suma = suma + mul
            
        verificacion = 10 - (suma%10)
        
        if verificacion == int(cedula[9]):
            return True
        else:
            return False
        
#Funcion que permite localizar en un texto cadenas con formato de correo electronico
def EncuentraEmail(texto):
    match = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', texto)
    return match

#Funcion que permite localicar en un texto cadenas con formato de cedula ecuatoriana 
#(Esta funcion busca grupos de numeros de 10 digitos) el resultado se pasa a la funcion de validacion de cedula para verificar
#que sea una cedula valida.
def EncuentraCedula(texto):
    match = re.findall(r"\b\d{10}\b", texto)
    return match

#Aca entramos al proceso de PLN. Esta funcion se encarga de extraer las raices morfologicas de cada palabra en el texto
def lematiza(palabra):
    base_url = 'https://www.lenguaje.com/cgi-bin/lema.exe?edition_field='+palabra+"&B1=Lematizar"
    selector_lemma = Selector(text = requests.get(base_url).content)
    lemma = selector_lemma.css('div div div div div li').css('::text').extract()[0]
    if lemma=='Raíz del sustantivo "suma". ':
        lemma = ''
    return lemma  

#Esta funcion permite separar en tokens o palabras el texto, tomando en consideracion que convierte todo el texto en minusculas,
#Elimina caracteres especiales, elimina numeros, elimina las stopwords (el, la, con, etc.)
def word_tokenize_clean(sentence, xtra_words, to_lower=True, remove_special_chars=True, remove_numbers=True, remove_stopwords=True, remove_emails=True):
    if remove_emails:
        sentence = re.sub(r'[\w.+-]+@[\w-]+\.[\w.-]+', '', sentence)
    token_clean = word_tokenize(sentence)
    if to_lower:
        token_clean = [i.lower() for i in token_clean]
    if remove_special_chars:
        token_clean = [re.sub(r'\W+', '', i) for i in token_clean]
    if remove_numbers:
        token_clean = [re.sub(r'[0-9]+', '', i) for i in token_clean] 
    if remove_stopwords:
        token_clean = [i for i in token_clean if i.lower() not in stopwords.words('spanish')]
        token_clean = [i for i in token_clean if i.lower() not in stopwords.words('english')]
    if len(xtra_words) > 0:
        token_clean = [i for i in token_clean if i.lower() not in xtra_words]
    token_clean = [i for i in token_clean if i!='']
    return token_clean

#Reemplaza vocales tildadas y las ñ/Ñ
def normalize(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("ñ", "n"),
        ("Ñ", "N"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s

nombres_apellidos = []
tokens = []
lista = []

for t in word_tokenize_clean(normalize(contents), ['everyone', 'from']):
    valor = lematiza(t)
    if valor != '':
        tokens.append(valor)

for token in nlp_model_es(np.unique(np.array(tokens)).tolist()):
    if token.pos_ in ['NOUN', 'PROPN']:
        nombres_apellidos.append(token.text)