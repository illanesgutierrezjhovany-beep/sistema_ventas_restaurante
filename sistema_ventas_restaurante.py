import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
def conectar():
    conn = sqlite3.connect("restaurante.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ventas 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       fecha TIMESTAMP, 
                       producto TEXT, 
                       cantidad INTEGER, 
                       total REAL)''')
    conn.commit()
    return conn

# --- INTERFAZ ---
st.set_page_config(page_title="Sistema de Ventas", page_icon="🍔")
st.title("🍔 Sistema de Ventas - Pollería & Alitas")

# Menú (Basado en las fotos que compartiste)
menu = {
    "Pollo a la Canasta": 35.0,
    "Alitas Barbacoa": 30.0,
    "Alitas Miel Mostaza": 30.0,
    "Alitas Picantes": 30.0,
    "Pollo al Spiedo": 40.0,
    "Refresco Personal": 8.0,
    "Cerveza": 15.0
}

# Formulario de venta
st.subheader("Registrar Nueva Venta")
producto = st.selectbox("Seleccione el producto:", list(menu.keys()))
cantidad = st.number_input("Cantidad:", min_value=1, value=1)
precio_unitario = menu[producto]
total = cantidad * precio_unitario

st.write(f"**Total a pagar:** {total:.2f} BS")

if st.button("Confirmar Venta"):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ventas (fecha, producto, cantidad, total) VALUES (?, ?, ?, ?)",
                   (datetime.now(), producto, cantidad, total))
    conn.commit()
    conn.close()
    st.success(f"¡Venta de {producto} registrada con éxito!")

# --- REPORTE (Analítica) ---
st.divider()
st.subheader("📊 Reporte de Ventas")
if st.checkbox("Mostrar historial de ventas"):
    conn = conectar()
    df = pd.read_sql("SELECT * FROM ventas", conn)
    conn.close()
    st.dataframe(df)