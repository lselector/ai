
# pagination_detector.py

import os
import json
from typing import List, Dict, Tuple, Union
from pydantic import BaseModel, Field, ValidationError

import tiktoken
from dotenv import load_dotenv

import openai
from openai import OpenAI
import google.generativeai as genai
from groq import Groq

from assets import PROMPT_PAGINATION, PRICING, LLAMA_MODEL_FULLNAME, GROQ_LLAMA_MODEL_FULLNAME

load_dotenv()
import logging

class PaginationData(BaseModel):
    page_urls: List[str] = Field(default_factory=list, description="List of pagination URLs, including 'Next' button URL if present")

def calculate_pagination_price(token_counts: Dict[str, int], model: str) -> float:
    """
    Calculate the price for pagination based on token counts and the selected model.
    
    Args:
    token_counts (Dict[str, int]): A dictionary containing 'input_tokens' and 'output_tokens'.
    model (str): The name of the selected model.

    Returns:
    float: The total price for the pagination operation.
    """
    input_tokens = token_counts['input_tokens']
    output_tokens = token_counts['output_tokens']
    
    input_price = input_tokens * PRICING[model]['input']
    output_price = output_tokens * PRICING[model]['output']
    
    return input_price + output_price

def detect_pagination_elements(url: str, indications: str, selected_model: str, markdown_content: str) -> Tuple[Union[PaginationData, Dict, str], Dict, float]:
    try:
        """
        Uses AI models to analyze markdown content and extract pagination elements.

        Args:
            selected_model (str): The name of the OpenAI model to use.
            markdown_content (str): The markdown content to analyze.

        Returns:
            Tuple[PaginationData, Dict, float]: Parsed pagination data, token counts, and pagination price.
        """ 
        prompt_pagination = PROMPT_PAGINATION+"\n The url of the page to extract pagination from   "+url+"if the urls that you find are not complete combine them intelligently in a way that fit the pattern **ALWAYS GIVE A FULL URL**"
        if indications != "":
            prompt_pagination +=PROMPT_PAGINATION+"\n\n these are the users indications that, pay special attention to them: "+indications+"\n\n below are the markdowns of the website: \n\n"
        else:
            prompt_pagination +=PROMPT_PAGINATION+"\n There are no user indications in this case just apply the logic described. \n\n below are the markdowns of the website: \n\n"

        if selected_model in ["gpt-4o-mini", "gpt-4o-2024-08-06"]:
            # Use OpenAI API
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            completion = client.beta.chat.completions.parse(
                model=selected_model,
                messages=[
                    {"role": "system", "content": prompt_pagination},
                    {"role": "user", "content": markdown_content},
                ],
                response_format=PaginationData
            )

            # Extract the parsed response
            parsed_response = completion.choices[0].message.parsed

            # Calculate tokens using tiktoken
            encoder = tiktoken.encoding_for_model(selected_model)
            input_token_count = len(encoder.encode(markdown_content))
            output_token_count = len(encoder.encode(json.dumps(parsed_response.dict())))
            token_counts = {
                "input_tokens": input_token_count,
                "output_tokens": output_token_count
            }

            # Calculate the price
            pagination_price = calculate_pagination_price(token_counts, selected_model)

            return parsed_response, token_counts, pagination_price

        elif selected_model == "gemini-1.5-flash":
            # Use Google Gemini API
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": PaginationData
                }
            )
            prompt = f"{prompt_pagination}\n{markdown_content}"
            # Count input tokens using Gemini's method
            input_tokens = model.count_tokens(prompt)
            completion = model.generate_content(prompt)
            # Extract token counts from usage_metadata
            usage_metadata = completion.usage_metadata
            token_counts = {
                "input_tokens": usage_metadata.prompt_token_count,
                "output_tokens": usage_metadata.candidates_token_count
            }
            # Get the result
            response_content = completion.text
            
            # Log the response content and its type
            logging.info(f"Gemini Flash response type: {type(response_content)}")
            logging.info(f"Gemini Flash response content: {response_content}")
            
            # Try to parse the response as JSON
            try:
                parsed_data = json.loads(response_content)
                if isinstance(parsed_data, dict) and 'page_urls' in parsed_data:
                    pagination_data = PaginationData(**parsed_data)
                else:
                    pagination_data = PaginationData(page_urls=[])
            except json.JSONDecodeError:
                logging.error("Failed to parse Gemini Flash response as JSON")
                pagination_data = PaginationData(page_urls=[])

            # Calculate the price
            pagination_price = calculate_pagination_price(token_counts, selected_model)

            return pagination_data, token_counts, pagination_price

        elif selected_model == "Llama3.1 8B":
            # Use Llama model via OpenAI API pointing to local server
            openai.api_key = "lm-studio"
            openai.api_base = "http://localhost:1234/v1"
            response = openai.ChatCompletion.create(
                model=LLAMA_MODEL_FULLNAME,
                messages=[
                    {"role": "system", "content": prompt_pagination},
                    {"role": "user", "content": markdown_content},
                ],
                temperature=0.7,
            )
            response_content = response['choices'][0]['message']['content'].strip()
            # Try to parse the JSON
            try:
                pagination_data = json.loads(response_content)
            except json.JSONDecodeError:
                pagination_data = {"next_buttons": [], "page_urls": []}
            # Token counts
            token_counts = {
                "input_tokens": response['usage']['prompt_tokens'],
                "output_tokens": response['usage']['completion_tokens']
            }
            # Calculate the price
            pagination_price = calculate_pagination_price(token_counts, selected_model)

            return pagination_data, token_counts, pagination_price

        elif selected_model == "Groq Llama3.1 70b":
            # Use Groq client
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            response = client.chat.completions.create(
                model=GROQ_LLAMA_MODEL_FULLNAME,
                messages=[
                    {"role": "system", "content": prompt_pagination},
                    {"role": "user", "content": markdown_content},
                ],
            )
            response_content = response.choices[0].message.content.strip()
            # Try to parse the JSON
            try:
                pagination_data = json.loads(response_content)
            except json.JSONDecodeError:
                pagination_data = {"page_urls": []}
            # Token counts
            token_counts = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens
            }
            # Calculate the price
            pagination_price = calculate_pagination_price(token_counts, selected_model)

            # Ensure the pagination_data is a dictionary
            if isinstance(pagination_data, PaginationData):
                pagination_data = pagination_data.dict()
            elif not isinstance(pagination_data, dict):
                pagination_data = {"page_urls": []}

            return pagination_data, token_counts, pagination_price

        else:
            raise ValueError(f"Unsupported model: {selected_model}")

    except Exception as e:
        logging.error(f"An error occurred in detect_pagination_elements: {e}")
        # Return default values if an error occurs
        return PaginationData(page_urls=[]), {"input_tokens": 0, "output_tokens": 0}, 0.0
