import streamlit as st
import pandas as pd
import pymongo
from datetime import datetime


def connect_to_mongodb():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["pinnacle_db"]
    return db


def upload_excel_to_mongodb(file_path, db):
    
    column_names = {
        'Contract Account': 'contractNumber',
        'Installation Number': 'installationNumber',
        'BPEM Number': 'bpemNumber',
        'BPEM type': 'bpemType',
        'Root Cause': 'rootCause',
        'Billed': 'billed'
    }
    df = pd.read_excel(file_path, names=column_names.keys(), header=0)
    df = df.rename(columns=column_names)

    
    df['Timestamp'] = datetime.now()

   
    records = df.to_dict(orient='records')
    collection = db["cases"]
    collection.insert_many(records)


def fetch_data_from_mongodb(db, limit=10, page=1):
    collection = db["cases"]
    skip = (page - 1) * limit
    data = collection.find({}, {"_id": 0}).skip(skip).limit(limit)
    return data


def fetch_data_by_installation_number(db, installation_number):
    collection = db["cases"]
    data = collection.find({"installationNumber": installation_number}, {"_id": 0})
    return data


def display_data(data):
  
    df = pd.DataFrame(data)

    st.dataframe(df)


def display_installation_number_history(data):
    if data:
    
        df = pd.DataFrame(data)

        
        df = df.rename(columns={
            'contractNumber': 'Contract Account',
            'installationNumber': 'Installation Number',
            'bpemNumber': 'BPEM Number',
            'bpemType': 'BPEM Type',
            'rootCause': 'Root Cause',
            'billed': 'Billed',
            'Timestamp': 'Upload Timestamp'
        })

        
        with st.expander("Installation Number History"):
            st.dataframe(df)
    else:
        st.warning("No data found for the specified installation number.")


def main():
    st.title("Pinnacle Consulting LLC Dashboard")
    st.markdown("---")

    
    st.sidebar.title("Upload Excel File")
    uploaded_file = st.sidebar.file_uploader("Choose an Excel file", type="xlsx")

    if uploaded_file:
        st.sidebar.markdown("---")
        st.sidebar.info("Uploaded successfully")

        if st.sidebar.button("Upload"):
            db = connect_to_mongodb()
            upload_excel_to_mongodb(uploaded_file, db)
            st.sidebar.success("Data uploaded to MongoDB")

    
    db = connect_to_mongodb()
    page = st.number_input("Page", value=1, min_value=1)
    data = fetch_data_from_mongodb(db, page=page)
    display_data(data)

    
    st.markdown("---")
    st.subheader("Search by Installation Number")
    installation_number = st.text_input("Enter an installation number:")

    if installation_number:
        data = fetch_data_by_installation_number(db, installation_number)
        display_installation_number_history(data)

if __name__ == "__main__":
    main()
