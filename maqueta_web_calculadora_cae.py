# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 01:21:34 2024

@author: pablo
"""
#!streamlit run "maqueta_web_calculadora_cae.py"
import streamlit as st
from unidecode import unidecode

# Constantes
VALOR_UF = 37944.50
CONTRIBUCION = {
    500000: 0, 600000: 0.021, 700000: 0.037, 800000: 0.05,
    900000: 0.061, 1000000: 0.07, 1250000: 0.07, 1500000: 0.07,
    1750000: 0.07, 2000000: 0.07, 2250000: 0.07, 2500000: 0.07,
    2750000: 0.07, 3000000: 0.08
}

def transformar_texto(texto):
    return unidecode(texto).upper()

def buscar_contribucion(monto):
    limites = sorted(CONTRIBUCION.keys())
    for i in range(len(limites) - 1):
        if limites[i] <= monto < limites[i + 1]:
            return CONTRIBUCION[limites[i+1]]
    return CONTRIBUCION[3000000] if monto >= limites[-1] else 0

def calcular_monto_condonacion(condicion, situacion, cuotas_pagadas, cuotas_totales):
    factor = {
        ("NO", "SI"): 60,
        ("NO", "NO"): 30,
        ("SI", "SI"): 40,
        ("SI", "NO"): 20
    }
    return factor.get((condicion, situacion), 0) * VALOR_UF * ((cuotas_pagadas / cuotas_totales) + 1)

# Título de la aplicación
st.title("Calculadora CAE")
st.write("Bienvenido a la calculadora CAE. Esta aplicación simula la condonación y el pago de la cuota a la que puedes optar bajo el sistema FES.", key="welcome_message")

# Entrada de variables
condicion_academica = transformar_texto(st.text_input("¿Egresó de su carrera?", key="condicion_academica_input"))
situacion_pago = transformar_texto(st.text_input("¿Está al día en el pago de sus cuotas?", key="situacion_pago_input"))
cuotas_pagadas = st.number_input("Indique la cantidad de cuotas que ha pagado", min_value=0, value=15, step=1, key="cuotas_pagadas_input")
cuotas_totales = st.number_input("Indique la cantidad de cuotas totales de su crédito CAE", min_value=0, value=30, step=1, key="cuotas_totales_input")
deuda_pendiente = st.number_input("Indique el monto pendiente por pagar", min_value=0, value=5000000, step=1000, key="deuda_pendiente_input")
ingreso_bruto = st.number_input("Indique su ingreso bruto mensual", min_value=0, value=0, step=1000, key="ingreso_bruto_input")

monto_condonacion = calcular_monto_condonacion(condicion_academica, situacion_pago, cuotas_pagadas, cuotas_totales)
saldo_deuda =int( deuda_pendiente - monto_condonacion)
   
st.write(f"Luego de la condonación inicial su monto adeudado es {saldo_deuda:.2f}.", key="saldo_deuda_output")
    
pago_anticipado = st.radio("¿Desea realizar el pago anticipado?", ('Sí', 'No'), key="pago_anticipado_radio")
if st.button("Calcular", key="calcular_button"):   
    if pago_anticipado == 'Sí':
        deuda_75 =int( 0.75 * saldo_deuda)
        st.write(f"Usted debe pagar {deuda_75:.2f}", key="deuda_75_output")
    elif pago_anticipado == 'No':
             
        contribucion = buscar_contribucion(ingreso_bruto)
        valor_B = contribucion * ingreso_bruto
        if valor_B == 0:
            st.write("Usted no paga cuota mensual", key="no_paga_cuota_output")
        else:
            valor_A = saldo_deuda / (cuotas_totales - cuotas_pagadas)
            tiempo = (cuotas_totales - cuotas_pagadas) / 12
            monto_cuota = min(valor_A, valor_B)
            st.write(f"Usted debe pagar ${monto_cuota:.2f} mensualmente por {tiempo:.2f} años", key="monto_cuota_output")