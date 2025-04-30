import streamlit as st
import requests

# FastAPI Backend URL
FASTAPI_URL = "http://127.0.0.1:8000"  # Change if hosted elsewhere

# Streamlit interface
st.title("Product Search and Query Answering")

# User input for query
question = st.text_input("Ask a question about a product")

# Button to trigger search and response generation
if st.button("Search and Get Answer"):
    if question:
        # Send request to FastAPI /search endpoint
        response = requests.post(f"{FASTAPI_URL}/search", json={"question": question})
        
        if response.status_code == 200:
            search_results = response.json()
            if search_results:
                st.write("Top 5 Relevant Products:")
                for i, product in enumerate(search_results):
                    st.write(f"{i + 1}. **{product['name']}** - Rs.{product['price']}")
                    st.write(f"   Description: {product['description']}\n")
            else:
                st.write("No relevant products found.")
            
            # Now, generate the answer using /gen endpoint
            gen_response = requests.post(f"{FASTAPI_URL}/gen", json={"question": question})
            
            if gen_response.status_code == 200:
                answer = gen_response.json().get("response")
                st.write("AI Generated Answer:")
                st.write(answer)
            else:
                st.write("Error in generating answer.")
        else:
            st.write("Error in fetching products.")
    else:
        st.write("Please enter a question to search.")
