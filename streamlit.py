"""
Crypto Scam Checker (EVM Version)
 
This module provides a Streamlit-based web application to help users identify potential scams in cryptocurrencies.
Users can choose to check a single cryptocurrency by filling out a form or check multiple cryptocurrencies by uploading a CSV file.
 
Dependencies:
- streamlit
- requests
- pandas
- io
- os
 
API URL:
- The application expects an API running at "http://127.0.0.1:8000" to handle prediction requests.
 
Functions:
- Single cryptocurrency check using a form.
- Multiple cryptocurrencies check using a CSV file upload.
 
Details:
1. Single Cryptocurrency Check:
    - Users fill out a form with various cryptocurrency attributes.
    - The form collects data such as contract address, total supply, supply sent to pool, number of snipers, ATH prices and market caps, buy blocks, liquidity, and funding details.
    - On form submission, data is sent to the API for prediction.
    - The result is displayed in JSON format.
 
2. Multiple Cryptocurrencies Check:
    - Users can download a CSV template to fill in data for multiple cryptocurrencies.
    - The uploaded CSV file is displayed for verification.
    - On file upload, data is sent to the API for batch prediction.
    - The result is provided as a downloadable CSV file.
 
Example Usage:
    1. Run the Streamlit app:
        $ streamlit run script_name.py
    2. Open the app in the browser.
    3. Select the option to check one cryptocurrency or upload a CSV for multiple checks.
    4. Fill in the required details and run the prediction.
 
Note:
- Ensure the API service is running and accessible at the specified URL before using the app.
 
To run: streamlit run streamlit/app.py
"""
 
import io
import os
 
import streamlit as st
import requests
import pandas as pd
 
# API URL
API_URL = "http://127.0.0.1:8000"
 
st.title("Crypto Scam Checker (EVM Version)")
 
# Description text
st.markdown("""
This tool helps you identify potential scams in cryptocurrencies.  
You can run check for:
- single cryptocurrency using form (all data required)
- upload CSV (sep='~') with cryptocurrencies data. Template can be downloaded.
 
Important: contract_address column is only for keeping the hash for result.  
""")
 
# Options to be chosen
option = st.selectbox(
    "What do you want to do?",
    ("", "Check one cryptocurrency (with form)", "Check multiple cryptocurrencies (with CSV)"),
    index=0
)
 
# OP1: Predict single crypto
if option == "Check one cryptocurrency (with form)":
    st.header("Check one cryptocurrency (with form)")
    form = st.form(key="crypto_form")
    contract_address = form.text_input("Contract Address",
                                       help="Hash of contract (cryptocurrency)."
                                       )
    total_supply = form.number_input("Total Supply",
                                     step=1,
                                     help="Total available supply of the token."
                                     )
    supply_send_to_pool = form.number_input("Supply Sent to Pool",
                                            step=1,
                                            help="Supply of the token send to pool by the creator."
                                            )
    number_of_snipers = form.number_input("Number of Snipers",
                                          step=1,
                                          help="Number of people who bought crypto in first 3 blocks from first buy block."
                                          )
    price_at_ath_1d = form.number_input("Price at ATH (1 day)",
                                        step=0.01,
                                        format="%.20f",
                                        help="Highest price from 1 day candles (open price)."
                                        )
    price_at_ath_1m = form.number_input("Price at ATH (1 minute)",
                                        step=0.01,
                                        format="%.20f",
                                        help="Highest price from 1 minute candles (open price)."
                                        )
    first_buy_block = form.number_input("First Buy Block",
                                        step=1,
                                        help="First buy block."
                                        )
    initial_liquidity = form.number_input("Initial Liquidity",
                                          help="Amount of ETH added during liquidity definition."
                                          )
    liquidity_block = form.number_input("Liquidity Block",
                                        step=1,
                                        help="Block of liquidity definition."
                                        )
    funding_amount = form.number_input("Funding Amount",
                                       step=0.01,
                                       format="%.20f",
                                       help="Amount of ETH send to creator of token."
                                       )
    funding_block = form.number_input("Funding Block",
                                      step=1,
                                      help="Funding block."
                                      )
    creation_block = form.number_input("Creation Block",
                                       step=1,
                                       help="Block when token where created."
                                       )
 
    submit_button = form.form_submit_button(label="Run prediction")
 
    if submit_button:
        payload = {
            "contract_address": contract_address,
            "total_supply": total_supply,
            "supply_send_to_pool": supply_send_to_pool,
            "number_of_snipers": number_of_snipers,
            "price_at_ath_1d": price_at_ath_1d,
            "price_at_ath_1m": price_at_ath_1m,
            "first_buy_block": first_buy_block,
            "initial_liquidity": initial_liquidity,
            "liquidity_block": liquidity_block,
            "funding_amount": funding_amount,
            "funding_block": funding_block,
            "creation_block": creation_block,
        }
        response = requests.post(f"{API_URL}/predict_single_crypto", json=payload)
 
        if response.status_code == 200:
            st.success("Prediction successful!")
            st.json(response.json())
        else:
            st.error("Error during prediction")
            st.json(response.json())
 
# Option 2: predict CSV cryptos
elif option == "Check multiple cryptocurrencies (with CSV)":
    st.header("Check multiple cryptocurrencies (with CSV)")
    template = {
        "contract_address": [],
        "total_supply": [],
        "supply_send_to_pool": [],
        "number_of_snipers": [],
        "price_at_ath_1d": [],
        "price_at_ath_1m": [],
        "first_buy_block": [],
        "initial_liquidity": [],
        "liquidity_block": [],
        "funding_amount": [],
        "funding_block": [],
        "creation_block": [],
    }
    template_df = pd.DataFrame(template)
    st.download_button(label="Download CSV template", data=template_df.to_csv(index=False, sep='~'),
                       file_name="template.csv", mime="text/csv")
 
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
 
    if uploaded_file:
        st.write("CSV file content:")
        df = pd.read_csv(uploaded_file, sep='~')
        st.dataframe(df)
        upload_directory: str = "data\\01_raw\\prediction"
 
        if st.button("Run prediction"):
            file_path = os.path.join(upload_directory, "p_raw_crypto_data.csv")
 
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
 
            with open(file_path, "rb") as f:
                files = {'file': ('p_raw_crypto_data.csv', f, 'text/csv')}
                response = requests.post(f"{API_URL}/upload_and_run_pipeline", files=files)
 
            if response.status_code == 200:
                st.success("Pipeline executed successfully!")
 
                csv_file_path = 'data/07_model_output/prediction/p_result.csv'
                csv_file = pd.read_csv(csv_file_path)
 
                csv_buffer = io.StringIO()
                csv_file.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)
                csv_data = csv_buffer.getvalue()
 
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="result_is_scam.csv",
                    mime="text/csv"
                )
            else:
                st.error("Error executing pipeline")
                st.json(response.json())