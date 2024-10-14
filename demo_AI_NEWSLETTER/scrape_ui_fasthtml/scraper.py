
import os
import random
import time
import re
import json
from datetime import datetime
from typing import List, Dict, Type

import pandas as pd
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, create_model
import html2text
import tiktoken

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from openai import OpenAI
import google.generativeai as genai
from groq import Groq

import ollama

from assets import USER_AGENTS,PRICING,HEADLESS_OPTIONS,SYSTEM_MESSAGE,USER_MESSAGE,LLAMA_MODEL_FULLNAME,GROQ_LLAMA_MODEL_FULLNAME
load_dotenv()

# Set up the Chrome WebDriver options

def setup_selenium():
    options = Options()

    # Randomly select a user agent from the imported list
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"user-agent={user_agent}")

    # Add other options
    for option in HEADLESS_OPTIONS:
        options.add_argument(option)

    # Specify the path to the ChromeDriver
    #service = Service(r"./chromedriver-win64/chromedriver.exe")  

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=options)
    return driver

def click_accept_cookies(driver):
    """
    Tries to find and click on a cookie consent button. It looks for several common patterns.
    """
    try:
        # Wait for cookie popup to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button | //a | //div"))
        )
        
        # Common text variations for cookie buttons
        accept_text_variations = [
            "accept", "agree", "allow", "consent", "continue", "ok", "I agree", "got it"
        ]
        
        # Iterate through different element types and common text variations
        for tag in ["button", "a", "div"]:
            for text in accept_text_variations:
                try:
                    # Create an XPath to find the button by text
                    element = driver.find_element(By.XPATH, f"//{tag}[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]")
                    if element:
                        element.click()
                        print(f"Clicked the '{text}' button.")
                        return
                except:
                    continue

        print("No 'Accept Cookies' button found.")
    
    except Exception as e:
        print(f"Error finding 'Accept Cookies' button: {e}")

def fetch_html_selenium(url):
    driver = setup_selenium()
    try:
        print(f"URL: {url}")
        driver.get(url)
        
        # Add random delays to mimic human behavior
        time.sleep(1)  # Adjust this to simulate time for user to read or interact
        driver.maximize_window()
        

        # Try to find and click the 'Accept Cookies' button
        # click_accept_cookies(driver)

        # Add more realistic actions like scrolling
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(random.uniform(1.1, 1.8))  # Simulate time taken to scroll and read
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1.2);")
        time.sleep(random.uniform(1.1, 1.8))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1);")
        time.sleep(random.uniform(1.1, 2.1))
        html = driver.page_source
        return html
    finally:
        driver.quit()

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove headers and footers based on common HTML tags or classes
    for element in soup.find_all(['header', 'footer']):
        element.decompose()  # Remove these tags and their content

    return str(soup)


def html_to_markdown_with_readability(html_content):

    
    cleaned_html = clean_html(html_content)  
    
    # Convert to markdown
    markdown_converter = html2text.HTML2Text()
    markdown_converter.ignore_links = False
    markdown_content = markdown_converter.handle(cleaned_html)
    
    return markdown_content


    
def save_raw_data(raw_data: str, output_folder: str, file_name: str):
    """Save raw markdown data to the specified output folder."""
    os.makedirs(output_folder, exist_ok=True)
    raw_output_path = os.path.join(output_folder, file_name)
    with open(raw_output_path, 'w', encoding='utf-8') as f:
        f.write(raw_data)
    print(f"Raw data saved to {raw_output_path}")
    return raw_output_path


def remove_urls_from_file(file_path):
    # Regex pattern to find URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    # Construct the new file name
    base, ext = os.path.splitext(file_path)
    new_file_path = f"{base}_cleaned{ext}"

    # Read the original markdown content
    with open(file_path, 'r', encoding='utf-8') as file:
        markdown_content = file.read()

    # Replace all found URLs with an empty string
    cleaned_content = re.sub(url_pattern, '', markdown_content)

    # Write the cleaned content to a new file
    with open(new_file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_content)
    print(f"Cleaned file saved as: {new_file_path}")
    return cleaned_content


def create_dynamic_listing_model(field_names: List[str]) -> Type[BaseModel]:
    """
    Dynamically creates a Pydantic model based on provided fields.
    field_name is a list of names of the fields to extract from the markdown.
    """
    # Create field definitions using aliases for Field parameters
    field_definitions = {field: (str, ...) for field in field_names}
    # Dynamically create the model with all field
    return create_model('DynamicListingModel', **field_definitions)


def create_listings_container_model(listing_model: Type[BaseModel]) -> Type[BaseModel]:
    """
    Create a container model that holds a list of the given listing model.
    """
    return create_model('DynamicListingsContainer', listings=(List[listing_model], ...))




def trim_to_token_limit(text, model, max_tokens=120000):
    encoder = tiktoken.encoding_for_model(model)
    tokens = encoder.encode(text)
    if len(tokens) > max_tokens:
        trimmed_text = encoder.decode(tokens[:max_tokens])
        return trimmed_text
    return text

def generate_system_message(listing_model: BaseModel) -> str:
    """
    Dynamically generate a system message based on the fields in the provided listing model.
    """
    # Use the model_json_schema() method to introspect the Pydantic model
    schema_info = listing_model.model_json_schema()

    # Extract field descriptions from the schema
    field_descriptions = []
    for field_name, field_info in schema_info["properties"].items():
        # Get the field type from the schema info
        field_type = field_info["type"]
        field_descriptions.append(f'"{field_name}": "{field_type}"')

    # Create the JSON schema structure for the listings
    schema_structure = ",\n".join(field_descriptions)

    # Generate the system message dynamically
    system_message = f"""
    You are an intelligent text extraction and conversion assistant. Your task is to extract structured information 
                        from the given text and convert it into a pure JSON format. The JSON should contain only the structured data extracted from the text, 
                        with no additional commentary, explanations, or extraneous information. 
                        You could encounter cases where you can't find the data of the fields you have to extract or the data will be in a foreign language.
                        Please process the following text and provide the output in pure JSON format with no words before or after the JSON:
    Please ensure the output strictly follows this schema:

    {{
        "listings": [
            {{
                {schema_structure}
            }}
        ]
    }} """

    return system_message



async def format_data(data, selected_model, tags=None):
    token_counts = {}

    print(f"Model choosing: {selected_model}")

    delimiter = " "
    result_string = ""
    if tags:
        result_string = delimiter.join("TAGS: \n")
        result_string += delimiter.join(tags)
    
    print(f"TAGS: {result_string}")
    if selected_model in ["gpt-4o-mini", "gpt-4o-2024-08-06"]:
        pass

    # elif selected_model == "gemini-1.5-flash":
    #     # Use Google Gemini API
    #     genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    #     model = genai.GenerativeModel('gemini-1.5-flash',
    #             generation_config={
    #                 "response_mime_type": "application/json",
    #                 "response_schema": DynamicListingsContainer
    #             })
    #     prompt = SYSTEM_MESSAGE + "\n" + USER_MESSAGE + data
    #     # Count input tokens using Gemini's method
    #     input_tokens = model.count_tokens(prompt)
    #     completion = model.generate_content(prompt)
    #     # Extract token counts from usage_metadata
    #     usage_metadata = completion.usage_metadata
    #     token_counts = {
    #         "input_tokens": usage_metadata.prompt_token_count,
    #         "output_tokens": usage_metadata.candidates_token_count
    #     }
    #     return completion.text, token_counts
    
    elif selected_model == "Llama3.1 8B":

        client = ollama.Client()

        #llama3.1:8b-instruct-q4_1

        # Dynamically generate the system message based on the schema
        #sys_message = generate_system_message(DynamicListingModel)
        # print(SYSTEM_MESSAGE)
        # Point to the local server
        #client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

        response_content = client.generate(model="llama3.1:8b-instruct-q4_1", prompt=SYSTEM_MESSAGE + USER_MESSAGE + data)['response']

        # Extract the content from the response
        #response_content = completion.choices[0].message.content
        print(response_content)
        # Convert the content from JSON string to a Python dictionary
        parsed_response = json.loads(response_content)
        
        # Extract token usage
        token_counts = {
            "input_tokens": 0,
            "output_tokens": 0
        }

        return parsed_response, token_counts
    # elif selected_model== "Groq Llama3.1 70b":
        
    #     # Dynamically generate the system message based on the schema
    #     sys_message = generate_system_message(DynamicListingModel)
    #     # print(SYSTEM_MESSAGE)
    #     # Point to the local server
    #     client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)

    #     completion = client.chat.completions.create(
    #     messages=[
    #         {"role": "system","content": sys_message},
    #         {"role": "user","content": USER_MESSAGE + data}
    #     ],
    #     model=GROQ_LLAMA_MODEL_FULLNAME,
    # )

    #     # Extract the content from the response
    #     response_content = completion.choices[0].message.content
        
    #     # Convert the content from JSON string to a Python dictionary
    #     parsed_response = json.loads(response_content)
        
    #     # completion.usage
    #     token_counts = {
    #         "input_tokens": completion.usage.prompt_tokens,
    #         "output_tokens": completion.usage.completion_tokens
    #     }

    #     return parsed_response, token_counts
    else:
        raise ValueError(f"Unsupported model: {selected_model}")



def save_formatted_data(formatted_data, output_folder: str, json_file_name: str, excel_file_name: str):
    """Save formatted data as JSON and Excel in the specified output folder."""
    os.makedirs(output_folder, exist_ok=True)
    
    # Parse the formatted data if it's a JSON string (from Gemini API)
    if isinstance(formatted_data, str):
        try:
            formatted_data_dict = json.loads(formatted_data)
        except json.JSONDecodeError:
            raise ValueError("The provided formatted data is a string but not valid JSON.")
    else:
        # Handle data from OpenAI or other sources
        formatted_data_dict = formatted_data.dict() if hasattr(formatted_data, 'dict') else formatted_data

    # Save the formatted data as JSON
    json_output_path = os.path.join(output_folder, json_file_name)
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_data_dict, f, indent=4)
    print(f"Formatted data saved to JSON at {json_output_path}")

    # Prepare data for DataFrame
    if isinstance(formatted_data_dict, dict):
        # If the data is a dictionary containing lists, assume these lists are records
        data_for_df = next(iter(formatted_data_dict.values())) if len(formatted_data_dict) == 1 else formatted_data_dict
    elif isinstance(formatted_data_dict, list):
        data_for_df = formatted_data_dict
    else:
        raise ValueError("Formatted data is neither a dictionary nor a list, cannot convert to DataFrame")

    # Create DataFrame
    try:
        df = pd.DataFrame(data_for_df)
        print("DataFrame created successfully.")

        # Save the DataFrame to an Excel file
        excel_output_path = os.path.join(output_folder, excel_file_name)
        df.to_excel(excel_output_path, index=False)
        print(f"Formatted data saved to Excel at {excel_output_path}")
        
        return df
    except Exception as e:
        print(f"Error creating DataFrame or saving Excel: {str(e)}")
        return None

def calculate_price(token_counts, model):
    input_token_count = token_counts.get("input_tokens", 0)
    output_token_count = token_counts.get("output_tokens", 0)
    
    # Calculate the costs
    input_cost = input_token_count * PRICING[model]["input"]
    output_cost = output_token_count * PRICING[model]["output"]
    total_cost = input_cost + output_cost
    
    return input_token_count, output_token_count, total_cost


def generate_unique_folder_name(url):
    timestamp = datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
    url_name = re.sub(r'\W+', '_', url.split('//')[1].split('/')[0])  # Extract domain name and replace non-alphanumeric characters
    return f"{url_name}_{timestamp}"


def scrape_multiple_urls(url, fields, selected_model):
    output_folder = os.path.join('output', generate_unique_folder_name(url))
    os.makedirs(output_folder, exist_ok=True)
    
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0
    all_data = []
    markdown = None  # We'll store the markdown for the first (or only) URL
    
    # for i, url in enumerate(urls, start=1):
    #     raw_html = fetch_html_selenium(url)
    #     current_markdown = html_to_markdown_with_readability(raw_html)
    #     if i == 1:
    #         markdown = current_markdown  # Store markdown for the first URL
    
    raw_html = fetch_html_selenium(url)
    current_markdown = html_to_markdown_with_readability(raw_html)
    scrape_url(url, fields, selected_model, output_folder, 0, current_markdown)

def scrape_url(output_folder: str, file_number: int, markdown: str):
    """Scrape a single URL and save the results."""
    save_raw_data(markdown, output_folder, f'rawData_{file_number}.md')
