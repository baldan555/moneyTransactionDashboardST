import streamlit as st
import psycopg2
from psycopg2 import sql
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set the Streamlit page layout to wide
st.set_page_config(layout="wide")

# Apply custom CSS to make all elements full width and set background color
st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        background-color: #f0f0f0; /* Set container background color to light gray */
    }
    .sidebar .sidebar-content {
        background-color: #f0f0f0; /* Set sidebar background color to light gray */
    }
    .reportview-container .main .block-container > .element-container {
        background-color: #f0f0f0; /* Set elements background color to light gray */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Konfigurasi koneksi
conn_params = {
    'dbname': 'postgres',
    'user': 'postgres.ypomswxeognmrvvzppna',
    'password': 'Keuangan65.',
    'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
    'port': '6543'
}

# Fungsi untuk menghubungkan ke database
def create_connection():
    return psycopg2.connect(**conn_params)

# Fungsi untuk memasukkan data baru ke tabel transaksi
def insert_transaction(date, activity, involved, amount):
    conn = create_connection()
    cursor = conn.cursor()
    query = "INSERT INTO transaksi (date, activity, involved, amount) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (date, activity, involved, amount))
    conn.commit()
    cursor.close()
    conn.close()

# Fungsi untuk mengambil data dari tabel transaksi
def fetch_transactions():
    conn = create_connection()
    df = pd.read_sql("SELECT * FROM transaksi", conn)
    conn.close()
    return df

# Fungsi untuk menampilkan visualisasi data
def display_visualization(df, selected_involved):
    # Menghitung ringkasan aktivitas dan pihak terlibat
    activity_summary = df.groupby('activity')['amount'].sum().reset_index()
    involved_summary = df.groupby('involved')['amount'].sum().reset_index()
    
    col1, col2 = st.columns(2)
    with col1:
        if 'involved' in df.columns and 'amount' in df.columns:
            fig = go.Figure(data=[
                go.Bar(
                    y=involved_summary['involved'],
                    x=involved_summary['amount'],
                    text=involved_summary['amount'],
                    texttemplate='%{text:.2s}',
                    textposition='outside',
                    marker=dict(
                        color=involved_summary['amount'],
                        colorscale=[[0, '#c7f9ee'], [1, '#142459']],  # Gradient from #7d3a7d to #FCEAE6
                        colorbar=dict(title='Amount')
                    ),
                    orientation='h'
                )
            ])
            
            # Center-align the title
            fig.update_layout(
                title=dict(
                    text="Total Amount per Involved Party",
                    x=0.5,
                    xanchor='center'
                ),
                xaxis_title='Total Amount',
                yaxis_title='Involved'
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Kolom 'involved' atau 'amount' tidak ditemukan dalam data frame.")
    
    # Create a bar chart with gradient colors for activities
    with col2:
        if 'activity' in df.columns and 'amount' in df.columns:
            activity_summary_sorted = activity_summary.sort_values(by='amount', ascending=False)
            fig = go.Figure(data=[
                go.Bar(
                    x=activity_summary_sorted['amount'],
                    y=activity_summary_sorted['activity'],
                    text=activity_summary_sorted['amount'],
                    texttemplate='%{text:.2s}',
                    textposition='outside',
                    marker=dict(
                        color=activity_summary_sorted['amount'],
                        colorscale=[[0, '#fceae6'], [1, '#29066b']],  # Gradient from #7d3a7d to #FCEAE6
                        colorbar=dict(title='Amount')
                    ),
                    orientation='h'
                )
            ])

            # Center-align the title
            fig.update_layout(
                title=dict(
                    text="Total Amount per Activity",
                    x=0.5,
                    xanchor='center'
                ),
                xaxis_title='Total Amount',
                yaxis_title='Activity'
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Kolom 'activity' atau 'amount' tidak ditemukan dalam data frame.")

    col3, col4 = st.columns(2)

    # Create a bar chart with gradient colors for filtered activities
    with col3:
        # Plot Transactions Over Time
        if selected_involved:
            filtered_df = df[df['involved'] == selected_involved]
            if not filtered_df.empty:
                activity_summary_filtered = filtered_df.groupby('activity')['amount'].sum().reset_index()
                activity_summary_filtered_sorted = activity_summary_filtered.sort_values(by='amount', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=activity_summary_filtered_sorted['amount'],
                        y=activity_summary_filtered_sorted['activity'],
                        text=activity_summary_filtered_sorted['amount'],
                        texttemplate='%{text:.2s}',
                        textposition='outside',
                        marker=dict(
                            color=activity_summary_filtered_sorted['amount'],
                            colorscale=[[0, '#e7e34e'], [1, '#c02323']],  # Gradient from #7d3a7d to #FCEAE6
                            colorbar=dict(title='Amount')
                        ),
                        orientation='h'
                    )
                ])

                # Center-align the title
                fig.update_layout(
                    title=dict(
                        text=f"Total Amount per Activity for {selected_involved}",
                        x=0.5,
                        xanchor='center'
                    ),
                    xaxis_title='Total Amount',
                    yaxis_title='Activity'
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Tidak ada data untuk pihak yang dipilih.")

    with col4:
        # Total Amount per Activity for selected Involved
        if 'date' in df.columns and 'amount' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.groupby('date')['amount'].sum().reset_index()
            fig = px.line(df, x='date', y='amount', title="Transactions Over Time")
            # Center-align the title
            fig.update_layout(
                title=dict(
                    text="Transactions Over Time",
                    x=0.5,
                    xanchor='center'
                )
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Kolom 'date' atau 'amount' tidak ditemukan dalam data frame.")

# Total initial amount
initial_amount = 65000000

# Bagian utama aplikasi Streamlit
st.markdown("<h1 style='text-align: center;'>Dashboard Keuangan IMF</h1>", unsafe_allow_html=True)

# Menampilkan box dengan total dana awal dan sisa dana
st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)  # Add spacing before total amounts

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(f"""
        <div style="background: linear-gradient(to left, #1ac7e6, #c7f9ee); padding:10px; border-radius:5px; text-align:center;">
            <h3>Total Dana Awal</h3>
            <p style="font-size:24px;">{initial_amount:,.2f} IDR</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    df = fetch_transactions()
    if not df.empty:
        total_spent = df['amount'].sum()
    else:
        total_spent = 0
    remaining_balance = initial_amount - total_spent
    st.markdown(f"""
    <div style="background: linear-gradient(to right, #1ac7e6, #c7f9ee); padding:10px; border-radius:5px; text-align:center;">
        <h3>Sisa Dana</h3>
        <p style="font-size:24px;">{remaining_balance:,.2f} IDR</p>
    </div>
    """, unsafe_allow_html=True)

# Menambahkan dropdown menu untuk memilih pihak yang terlibat
st.sidebar.header("Input Data Baru")
date = st.sidebar.date_input("Tanggal")
activity = st.sidebar.text_input("Aktivitas")
involved = st.sidebar.text_input("Pihak Terlibat")
amount = st.sidebar.number_input("Jumlah", min_value=0.0, format="%.2f")

if st.sidebar.button("Tambahkan Transaksi"):
    insert_transaction(date, activity, involved, amount)
    st.sidebar.success("Transaksi berhasil ditambahkan!")
    # Refresh the page to update the data and balance
    st.experimental_rerun()

# Dropdown untuk memilih pihak yang terlibat
st.sidebar.subheader("Visualisasi Aktivitas per Pihak Terlibat")
involved_options = df['involved'].dropna().unique()

# Set "IMF" as the default option if it exists in the options
default_option = "IMF"
if default_option not in involved_options:
    default_option = involved_options[0] if involved_options.size > 0 else None

selected_involved = st.sidebar.selectbox(
    "Pilih Pihak Terlibat",
    options=involved_options,
    index=involved_options.tolist().index(default_option) if default_option in involved_options else 0
)

# Menambahkan jarak antara visualisasi dan kolom
st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)  # Add spacing before visualizations

# Menampilkan visualisasi data
if not df.empty:
    display_visualization(df, selected_involved)

# Tempat untuk tabel data transaksi di bagian bawah

if df.empty:
    st.warning("Belum ada transaksi yang tercatat.")
else:
    # Center the header using HTML
    st.markdown("<h2 style='text-align: center;'>Data Transaksi</h2>", unsafe_allow_html=True)

    # Filter out 'id' and 'index' columns if they exist
    columns_to_exclude = ['id', 'index']
    df_filtered = df.loc[:, ~df.columns.isin(columns_to_exclude)]

    # Center the table using HTML
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    st.dataframe(df_filtered, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
