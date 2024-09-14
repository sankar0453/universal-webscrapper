import streamlit as st
from streamlit_tags import st_tags_sidebar
import pandas as pd
import json
from datetime import datetime
from scraper import fetch_html_playwright, save_raw_data, format_data, save_formatted_data, calculate_price,html_to_markdown_with_readability, create_dynamic_listing_model,create_listings_container_model

import asyncio
from assets import PRICING
import sys

# Ensure ProactorEventLoop for Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
def main():
    # Initialize Streamlit app
    st.set_page_config(page_title="Universal Web Scraper")
    st.title("Web Scraper")

    # Sidebar components
    st.sidebar.title("Web Scraper Settings")
    model_selection = st.sidebar.selectbox("Select Model", options=list(PRICING.keys()), index=0)
    url_input = st.sidebar.text_input("Enter URL")


    # Tags input specifically in the sidebar
    tags = st.sidebar.empty()  # Create an empty placeholder in the sidebar
    tags = st_tags_sidebar(
        label='Enter Fields to Extract:',
        text='Press enter to add a tag',
        value=[],  # Default values if any
        suggestions=[],  # You can still offer suggestions, or keep it empty for complete freedom
        maxtags=-1,  # Set to -1 for unlimited tags
        key='tags_input'
    )


    st.sidebar.markdown("---")

    # Process tags into a list
    fields = tags

    # Initialize variables to store token and cost information
    input_tokens = output_tokens = total_cost = 0  # Default values

    # Buttons to trigger scraping
    # Define the scraping function
    def perform_scrape():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        raw_html = asyncio.run(fetch_html_playwright(url_input))
        markdown = html_to_markdown_with_readability(raw_html)
        save_raw_data(markdown, timestamp)
        DynamicListingModel = create_dynamic_listing_model(fields)
        DynamicListingsContainer = create_listings_container_model(DynamicListingModel)
        formatted_data, tokens_count = format_data(markdown, DynamicListingsContainer,DynamicListingModel,model_selection)
        input_tokens, output_tokens, total_cost = calculate_price(tokens_count, model=model_selection)
        df = save_formatted_data(formatted_data, timestamp)

        return df, formatted_data, markdown, input_tokens, output_tokens, total_cost, timestamp

    # Handling button press for scraping
    if 'perform_scrape' not in st.session_state:
        st.session_state['perform_scrape'] = False

    if st.sidebar.button("Scrape"):
        with st.spinner('Please wait... Data is being scraped.'):
            st.session_state['results'] = perform_scrape()
            st.session_state['perform_scrape'] = True

    if st.session_state.get('perform_scrape'):
        df, formatted_data, markdown, input_tokens, output_tokens, total_cost, timestamp = st.session_state['results']
        # Display the DataFrame and other data
        st.write("Scraped Data:", df)
        st.sidebar.markdown("## Token Usage")
        st.sidebar.markdown(f"**Input Tokens:** {input_tokens}")
        st.sidebar.markdown(f"**Output Tokens:** {output_tokens}")
        st.sidebar.markdown(f"**Total Cost:** :green-background[***${total_cost:.4f}***]")

        # Create columns for download buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button("Download JSON", data=json.dumps(formatted_data.dict() if hasattr(formatted_data, 'dict') else formatted_data, indent=4), file_name=f"{timestamp}_data.json")
        with col2:
            # Convert formatted data to a dictionary if it's not already (assuming it has a .dict() method)
            if isinstance(formatted_data, str):
                # Parse the JSON string into a dictionary
                data_dict = json.loads(formatted_data)
            else:
                data_dict = formatted_data.dict() if hasattr(formatted_data, 'dict') else formatted_data

            
            # Access the data under the dynamic key
            first_key = next(iter(data_dict))  # Safely get the first key
            main_data = data_dict[first_key]   # Access data using this key

            # Create DataFrame from the data
            df = pd.DataFrame(main_data)

            # data_dict=json.dumps(formatted_data.dict(), indent=4)
            st.download_button("Download CSV", data=df.to_csv(index=False), file_name=f"{timestamp}_data.csv")
        with col3:
            st.download_button("Download Markdown", data=markdown, file_name=f"{timestamp}_data.md")

    # Ensure that these UI components are persistent and don't rely on re-running the scrape function
    if 'results' in st.session_state:
        df, formatted_data, markdown, input_tokens, output_tokens, total_cost, timestamp = st.session_state['results']



if __name__ == "__main__":
     main()