import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

# --- CONFIGURACIÓN ---
DB_NAME = "restaurante_ventas.db"

def get_hora_bolivia():
    return datetime.utcnow() - timedelta(hours=4)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ventas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  fecha TIMESTAMP, 
                  producto TEXT, 
                  categoria TEXT, 
                  cantidad INTEGER, 
                  precio_unitario REAL, 
                  total REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- MENÚ ---
menu_items = {
    "Pollo a la Canasta": {"precio": 35.0, "categoria": "Pollo"},
    "Alitas Barbacoa": {"precio": 30.0, "categoria": "Alitas"},
    "Alitas Miel Mostaza": {"precio": 30.0, "categoria": "Alitas"},
    "Alitas Picantes": {"precio": 30.0, "categoria": "Alitas"},
    "Pollo al Spiedo": {"precio": 40.0, "categoria": "Pollo"},
    "Refresco Personal": {"precio": 8.0, "categoria": "Bebidas"},
    "Cerveza": {"precio": 15.0, "categoria": "Bebidas"}
}

# --- INTERFAZ ---
st.set_page_config(page_title="Sistema Pro", layout="wide")
st.title("🍔 Sistema de Gestión - Restaurante")

tab1, tab2 = st.tabs(["🛒 Registrar Venta", "📊 Dashboard y Gestión"])

with tab1:
    st.subheader("Registro de Pedidos")
    producto = st.selectbox("Producto", list(menu_items.keys()))
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    
    precio = menu_items[producto]["precio"]
    categoria = menu_items[producto]["categoria"]
    total = cantidad * precio
    
    if st.button("Registrar Pedido"):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO ventas (fecha, producto, categoria, cantidad, precio_unitario, total) VALUES (?,?,?,?,?,?)",
                  (get_hora_bolivia().strftime("%Y-%m-%d %H:%M:%S"), producto, categoria, cantidad, precio, total))
        conn.commit()
        conn.close()
        st.success("¡Pedido registrado exitosamente y guardado localmente!")

with tab2:
    st.subheader("Dashboard y Control")
    
    if os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql("SELECT * FROM ventas", conn)
        conn.close()
    else:
        df = pd.DataFrame()
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Ingresos", f"{df['total'].sum():.2f} BS")
        col2.metric("Pedidos", len(df))
        col3.metric("Promedio", f"{df['total'].mean():.2f} BS")
        
        st.divider()
        st.write("### 📈 Ventas por Categoría")
        cat_df = df.groupby('categoria')['total'].sum()
        st.bar_chart(cat_df)
            
        st.write("### 📋 Historial y Gestión")
        st.dataframe(df.sort_values(by='fecha', ascending=False), use_container_width=True)
        
        st.divider()
        st.write("#### 🗑️ Eliminar una Venta")
        id_eliminar = st.number_input("Escribe el ID de la venta a eliminar:", min_value=1, step=1)
        if st.button("Confirmar Eliminación"):
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("DELETE FROM ventas WHERE id = ?", (id_eliminar,))
            conn.commit()
            conn.close()
            st.success(f"Venta ID {id_eliminar} eliminada correctamente.")
            st.rerun()
    else:
        st.info("No hay ventas registradas.")
