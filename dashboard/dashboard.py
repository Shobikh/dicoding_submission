import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os
from babel.numbers import format_currency

sns.set(style='dark')


# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    return daily_orders_df

def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    return monthly_orders_df

def top_product_category_df(df):
    top_product_category_df = df.groupby("product_category_name_english").order_id.nunique().sort_values(ascending=False).reset_index()
    top_product_category_df.rename(columns={
        "product_category_name_english": "product_category",
        "order_id": "Sold"
    }, inplace=True)
    return top_product_category_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)

    return bystate_df

def most_used_payment_type_df(df):
    most_used_payment_type_df = df.groupby("payment_type").order_id.nunique().reset_index()
    return most_used_payment_type_df

# Load cleaned data
file_path = os.path.join(os.path.dirname(__file__), 'main_data.csv')
all_df = pd.read_csv(file_path)

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter data
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    #st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

# st.dataframe(main_df)

# # Menyiapkan berbagai dataframe
daily_orders_df = create_daily_orders_df(main_df)
monthly_orders_df = create_monthly_orders_df(main_df)
top_product_category_df = top_product_category_df(main_df)
bystate_df = create_bystate_df(main_df)
most_used_payment_type_df = most_used_payment_type_df(main_df)

# plot number of daily orders
st.header('Dicoding Submission Dashboard :sparkles:')
st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='es_CO')
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# Monthly Order
st.subheader('Monthly Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "BRL", locale='es_CO')
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["order_purchase_timestamp"],
    monthly_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# Product performance
st.subheader("Best & Worst Performing Product")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

best_colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
worst_colors = ["#FF6347", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="Sold", y="product_category", data=top_product_category_df.head(5), palette=best_colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Sold Quantity", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="Sold", y="product_category",
            data=top_product_category_df.sort_values(by="Sold", ascending=True).head(5), palette=worst_colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Sold Quantity", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

#Most Used Pament Type
st.subheader("Most Used Payment Type")

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#FF6347"]
sns.barplot(
    x="order_id",
    y="payment_type",
    data=most_used_payment_type_df.sort_values(by="order_id", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Most Used Payment Type", loc="center", fontsize=30)
ax.set_ylabel("Payment Type", fontsize=20)
ax.set_xlabel("Used (Time)", fontsize=20)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# customer demographic
st.subheader("Top 10 of Customer Demographics")

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_count",
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False).head(10),
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer by States", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.caption('Copyright © Mukhammad Shobikh')
