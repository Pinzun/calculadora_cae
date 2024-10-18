# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 10:11:10 2024

@author: Ivan
"""


#!streamlit run "maqueta_web_calculadora_cae.py"
import streamlit as st
from unidecode import unidecode

# Constantes
VALOR_UF = 37944.50
VALOR_UTM = 66561
CONTRIBUCION = {
    500000: 0, 600000: 0.021, 700000: 0.037, 800000: 0.05,
    900000: 0.061, 1000000: 0.07, 1250000: 0.07, 1500000: 0.07,
    1750000: 0.07, 2000000: 0.07, 2250000: 0.07, 2500000: 0.07,
    2750000: 0.07, 3000000: 0.08
}

def pago_tramos(ingreso,utm):
    if ingreso>utm*11.2:
        T1=utm*(11.2-7.5)*0.13
    elif ingreso>utm*7.5:
        T1=(ingreso-utm*7.5)*0.13
    else:
        T1=0
    if ingreso>99999999:
        T2=(99999999-utm*11.2)*0.15
    elif ingreso>utm*11.2:
        T2=(ingreso-utm*11.2)*0.15
    else:
        T2=0
    return T1+T2
    
    

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
        ("No", "Sí"): 60,
        ("No", "No"): 30,
        ("Sí", "Sí"): 40,
        ("Sí", "No"): 20
    }
    return factor.get((condicion, situacion), 0) * VALOR_UF * ((cuotas_pagadas / cuotas_totales) + 1)

# Título de la aplicación
st.title("Calculadora CAE")
st.write("Bienvenido a la calculadora CAE. Esta aplicación simula la condonación y el pago de la cuota a la que puedes optar bajo el sistema FES.", key="welcome_message")

# Entrada de variables
condicion_academica = st.radio("¿Egresó de su carrera?", ('Sí', 'No'), key="condicion_academica_input")
situacion_pago = st.radio("¿Está al día en el pago de sus cuotas?", ('Sí', 'No'), key="situacion_pago_input")
cuotas_pagadas = st.number_input("Indique la cantidad de cuotas que ha pagado", min_value=0, value=0, step=1, key="cuotas_pagadas_input")
cuotas_totales = st.number_input("Indique la cantidad de cuotas totales de su crédito CAE", min_value=0, value=0, step=1, key="cuotas_totales_input")
deuda_pendiente = st.number_input("Indique el monto pendiente por pagar", min_value=0, value=0, step=1000, key="deuda_pendiente_input")
ingreso_bruto = st.number_input("Indique su ingreso bruto mensual", min_value=0, value=0, step=1000, key="ingreso_bruto_input")

try:
    monto_condonacion = calcular_monto_condonacion(condicion_academica, situacion_pago, cuotas_pagadas, cuotas_totales)
    saldo_deuda =int( deuda_pendiente - monto_condonacion)
    st.write(f"Luego de la condonación inicial su monto adeudado es ${saldo_deuda}.", key="saldo_deuda_output")
except ZeroDivisionError:
    st.error("Error: La cantidad total de cuotas no puede ser cero. Por favor, ingresa un valor mayor a cero.")
    
pago_anticipado = st.radio("¿Desea realizar el pago anticipado?", ('Sí', 'No'), key="pago_anticipado_radio")
if st.button("Calcular", key="calcular_button"):   
    if pago_anticipado == 'Sí':
        deuda_75 =int( 0.75 * saldo_deuda)
        st.write(f"Usted debe pagar {deuda_75:.2f}", key="deuda_75_output")
    elif pago_anticipado == 'No':
        if ingreso_bruto>45*VALOR_UTM:
            valor_A = saldo_deuda / (cuotas_totales - cuotas_pagadas)
            contribucion = buscar_contribucion(ingreso_bruto)
            valor_B = contribucion * ingreso_bruto
            if valor_B == 0:
                st.write("Usted no paga cuota mensual", key="no_paga_cuota_output")
            else:
                monto_cuota = min(valor_A, valor_B)
                tiempo = (cuotas_totales - cuotas_pagadas) / 12
                st.write(f"Usted debe pagar ${monto_cuota:.2f} mensualmente por {tiempo:.2f} años", key="monto_cuota_output")
        else:               
            valor_A = saldo_deuda / (cuotas_totales - cuotas_pagadas)
            valor_B = pago_tramos(ingreso_bruto, VALOR_UTM)
            contribucion = buscar_contribucion(ingreso_bruto)
            valor_C =contribucion * ingreso_bruto 
            tiempo = (cuotas_totales - cuotas_pagadas) / 12
            monto_cuota = min(valor_A, valor_B, valor_C)
            st.write(f"Usted debe pagar ${monto_cuota:.2f} mensualmente por {tiempo:.2f} años", key="monto_cuota_output")
