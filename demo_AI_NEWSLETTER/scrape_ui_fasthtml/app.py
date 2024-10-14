
from fasthtml.common import *

from levutils.mybag import *
from levutils.myutils import *

import pandas as pd
import json
from datetime import datetime
from scraper import fetch_html_selenium, save_raw_data, format_data, save_formatted_data, calculate_price, html_to_markdown_with_readability, create_dynamic_listing_model, create_listings_container_model, scrape_url
from pagination_detector import detect_pagination_elements, PaginationData
import re
from urllib.parse import urlparse
from assets import *
import os, asyncio
from pydantic import BaseModel
from openai import OpenAI



bag = MyBunch()

app, rt, = fast_app(live=True, pico=False, ws_hdr=True, hdrs=[
    Link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css"
        ), 
    Link(
        rel="stylesheet", 
        href="https://cdn.jsdelivr.net/npm/@picocss/pico@latest/css/pico.min.css"
        ),
    Link(
        rel='stylesheet', 
        href='styles.css'
        )
    
])

scraped_sites_data = []
client_openai = OpenAI()

#---------------------------------------------------------------
@rt('/')
def get():
    """ Main page """
    global bag
    bag.list_items = []
    main_page = (Title("Document Q&A"),
        Div(
        Div(
        Div( 
            H1("Interactive Document Q&A"),
            Div(
            get_history(),
            cls="history-container"),
            Div(
                Form(
                    Div(
                        Select(id="shapeInput", name="model")(
                            Option("Ollama", value="ollama", selected=True),
                            Option("OpenAI", value="openai", selected=False),
                           id="select-model"), 
                    Label("Strict:", cls='px-2'),
                        Input(type="checkbox", 
                              cls="checkboxer", 
                              value="strict", 
                              name="strict", 
                              data_foo="bar"
                              ),
                    cls="model-strict-container"),
                    Group( 
                     Input(id="new-prompt", type="text", name="data"),
                     Button("Submit", id="submitButton", onclick="setScrollTrue();")
                     ),
                     id="form-id",
                     ws_send=True, hx_ext="ws", ws_connect="/scrape", 
                     target_id='data-list',
                     hx_swap="beforeend",
                     enctype="multipart/form-data",
                     hx_trigger="submit"
                    )
                    ),
                    cls="wrapper-chat column",
                    id="wrapper-chat-id"
                    ),
                    Div(
                    Div(
                    Div(
                    Div("Uploaded Files:", cls="text-upload"),
                    id="loading-container", cls="loading-container"),
                    Div(
                    Div(
                    #get_uploaded_files_list(),
                    id="container", cls="upload-files"),
                    id="upload-container-wrapper"
                    ),
                    Div("Wrong filetype. Allowed only: .txt, .xlsx, .docx, .json, .pdf, .html", id="error-message", style="color: red; display: none;"),
                    Div(
                    Form(
                    Input(type='file', id='file-upload_', name='files', multiple=True, style="display: none", 
                          onchange="document.getElementById('submit-upload-btn').click()", accept=".txt, .xlsx, .docx, .json, .pdf, .html"),
                    Button('Select Files', cls="select-files-btn", type='button', onclick="document.getElementById('file-upload_').click()"),
                    Button(type="submit", 
                           id="submit-upload-btn", 
                           onclick="createDiv();", 
                           style="display: none",
                           ),
                    **{'hx-on:htmx:after-request':"deleteUploadAnimation();"},
                    id="upload-form",
                    hx_post="/upload",
                    target_id="uploaded-files-list",
                    hx_swap="beforeend",
                    enctype="multipart/form-data",
                    cls="upload-cls",
                    ),
                    Form(Group(
                    Button("Clear", type="submit", id="clear-files")
                    ),
                    hx_post="/delete-all-docs",
                    target_id='uploaded-files-list',
                    hx_swap="outerHTML"
                    # cls="upload-button-container"
                    ),
                    cls="forms-container"
                    ),
                    
                
            Script(
            """
            const container = document.getElementById('container');
            const fileInput = document.getElementById('file-upload_');
            const form = document.getElementById('upload-form');;
            
            container.addEventListener('dragover', (event) => {
                event.preventDefault();
            });

            function validateAndSubmit(input) {
                const allowedExtensions = ['.txt', '.xlsx', '.docx', '.json', '.pdf', '.html'];
                const files = input.files;
                const errorMessage = document.getElementById('error-message');

                for (let i = 0; i < files.length; i++) {
                    const file = files[i];
                    const fileExtension = file.name.split('.').pop().toLowerCase();

                    console.log(fileExtension)

                    if (!allowedExtensions.includes('.' + fileExtension)) {
                        errorMessage.style.display = 'block';
                        input.value = ''; 
                        deleteUploadAnimation();
                        return false; // Indicate invalid file type
                    }
                }
                
                return true; // Indicate all files are valid
            }

            container.addEventListener('drop', (event) => {
                event.preventDefault();

                createDiv();

                const files = event.dataTransfer.files;

                fileInput.files = files; 

                form.dispatchEvent(new Event('submit')); 
                
            });

            container.addEventListener('change', () => {
                event.preventDefault(); 

                createDiv();

                const files = event.dataTransfer.files; 

                fileInput.files = files; 

                form.dispatchEvent(new Event('submit')); 

                });
            """
        ),
        Script(
            """

            const messageList = document.getElementById('chatlist')
            const parent = messageList.parentElement;
            let hasScrolled = false;

            let scrolledPercent_ = 0       

             messageList.addEventListener('scroll', () => {
                const scrollTop = messageList.scrollTop; // Current scroll position from the top
                const scrollHeight = messageList.scrollHeight; // Total height of scrollable content
                const clientHeight = messageList.clientHeight; // Visible height of the div

                scrolledPercent = (scrollTop / (scrollHeight - clientHeight)) * 100;
                
                
                set_scrolled_percent(scrolledPercent)
            });

            function set_scrolled_percent(new_scrolledPercent_) {
                scrolledPercent_ = new_scrolledPercent_
                //console.log(scrolledPercent_);
            }

            const observer = new MutationObserver(() => {
                    
                    if (hasScrolled) {
                    if (scrolledPercent_ > 99) {
                    scrollToBottom();
                    } else {
                    smoothScrollToBottom();
                    }
                    //alert("we did scroll");
                    //hasScrolled = false;
                    }
                    
            });

            observer.observe(messageList, { childList: true, subtree: true });

            function scrollToBottom() {
                messageList.scrollTop = messageList.scrollHeight;
            }

            function smoothScrollToBottom() {
                messageList.scrollTo({
                    top: messageList.scrollHeight,
                    behavior: 'smooth'
                });
              }

            function setScrollFalse() {
                hasScrolled = false;
            }
            function setScrollTrue() {
                hasScrolled = true;
                setFocus();
            }

            let previousScrollPosition = 0; 

            function handleScroll() {
            const currentScrollPosition = messageList.scrollTop;

            if (currentScrollPosition < previousScrollPosition) {
                // Scrolling up
                setScrollFalse(); // Call your desired method here
            }

            previousScrollPosition = currentScrollPosition;
            }

            // Attach the scroll event listener
            messageList.addEventListener('scroll', handleScroll);

            function setFocus() { 
                setTimeout(() => {
                    const inputField = document.getElementById('new-prompt');
                    inputField.focus();
                }, 100); 
            }

            """
        ),

        Script(
            """ 
                function createDiv() {
                // Create the new div element
                const newDiv = document.createElement('div');
                //newDiv.textContent = "This is a new div!"; // Add some content to the new div

                newDiv.id = 'loading-file-id';

                newDiv.className = "loading-line file-upload-line";

                // Get the parent div where you want to add the new div
                const parentDiv = document.getElementById('loading-container');

                // Append the new div to the parent div
                parentDiv.appendChild(newDiv);
                }


                function deleteUploadAnimation() {
                // 1. Get the div element by its ID
                let divToDelete = document.getElementById("loading-file-id");

                // 2. Check if the div exists
                if (divToDelete) {
                    // 3. Remove the div from its parent
                    divToDelete.parentNode.removeChild(divToDelete); 
                } 
                }
            """
        ),
        cls="wrapper-uploaded-files-internal",
        id="uploaded-files-internal"
                    ),
                    cls="wrapper-uploaded-files column",

                    ),                             
        cls="wrapper-content"),
        cls="wrapper-main")
    )

    return main_page

#---------------------------------------------------------------
def print_all_messages():
    """ Create ul from messages and return them to main page """

    global scraped_sites_data
    
    i = 0
    for site_data in scraped_sites_data:
        tid = f'site-{i}'

        list_item = Div(
            Div(site_data, id=tid,
                cls="chat-bubble chat-bubble-secondary"),
            cls = "chat chat-start")
        bag.list_items.append(list_item)  # Add the Li element to the list
        
        i +=1
        
    return Div(*bag.list_items, id='data-list')

#---------------------------------------------------------------
def get_history():
    """ Get all history messages """ 
    listed_messages = print_all_messages()
    history = Div(listed_messages, id="chatlist", cls="list-of-data")

    return history

def serialize_pydantic(obj):
    if isinstance(obj, BaseModel):
        return obj.dict()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

# Initialize Streamlit app
# st.set_page_config(page_title="Universal Web Scraper", page_icon="🦑")
# st.title("Universal Web Scraper 🦑")

# Initialize session state variables if they don't exist
# if 'results' not in st.session_state:
#     st.session_state['results'] = None
# if 'perform_scrape' not in st.session_state:
#     st.session_state['perform_scrape'] = False

# Sidebar components
# st.sidebar.title("Web Scraper Settings")
# model_selection = st.sidebar.selectbox("Select Model", options=list(PRICING.keys()), index=0)
# url_input = st.sidebar.text_input("Enter URL(s) separated by whitespace")

# Add toggle to show/hide tags field
#show_tags = st.sidebar.toggle("Tags only")

# Conditionally show tags input based on the toggle
tags = []
# if show_tags:
#     tags = st_tags_sidebar(
#         label='Enter Fields to Extract:', 
#         text='Press enter to add a tag',
#         value=[],
#         suggestions=[],
#         maxtags=-1,
#         key='tags_input'
#     )

#st.sidebar.markdown("---")
# Add pagination toggle and input
#use_pagination = st.sidebar.toggle("Enable Pagination")
# pagination_details = None
# if use_pagination:
#     pagination_details = st.sidebar.text_input("Enter Pagination Details (optional)", 
#         help="Describe how to navigate through pages (e.g., 'Next' button class, URL pattern)")

# st.sidebar.markdown("---")


def generate_unique_folder_name(url):
    timestamp = datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
    
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Extract the domain name
    domain = parsed_url.netloc or parsed_url.path.split('/')[0]
    
    # Remove 'www.' if present
    domain = re.sub(r'^www\.', '', domain)
    
    # Remove any non-alphanumeric characters and replace with underscores
    clean_domain = re.sub(r'\W+', '_', domain)
    
    return f"{clean_domain}_{timestamp}"


async def scrape_multiple_urls(url, fields, selected_model, tags=None):
    output_folder = os.path.join('output', generate_unique_folder_name(url))
    os.makedirs(output_folder, exist_ok=True)
    
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0
    all_data = []
    first_url_markdown = None
    
    # for i, url in enumerate(urls, start=1):
    raw_html = fetch_html_selenium(url)
    current_markdown = html_to_markdown_with_readability(raw_html)
    markdown = current_markdown  # Store markdown for the first URL
    
    scrape_url(url, fields, selected_model)
    
    return markdown, output_folder

# # Define the scraping function
# def perform_scrape():
#     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#     raw_html = fetch_html_selenium(url_input)
#     markdown = html_to_markdown_with_readability(raw_html)
#     save_raw_data(markdown, timestamp)
    
#     # Detect pagination if enabled
#     pagination_info = None
#     if use_pagination:
#         pagination_data, token_counts, pagination_price = detect_pagination_elements(
#             url_input, pagination_details, model_selection, markdown
#         )
#         pagination_info = {
#             "page_urls": pagination_data.page_urls,
#             "token_counts": token_counts,
#             "price": pagination_price
#         }
    
#     # Initialize token and cost variables with default values
#     input_tokens = 0
#     output_tokens = 0
#     total_cost = 0
    
#     if show_tags:
#         DynamicListingModel = create_dynamic_listing_model(tags)
#         DynamicListingsContainer = create_listings_container_model(DynamicListingModel)
#         formatted_data, tokens_count = format_data(
#             markdown, DynamicListingsContainer, DynamicListingModel, model_selection, tags
#         )
#         input_tokens, output_tokens, total_cost = calculate_price(tokens_count, model=model_selection)
#         df = save_formatted_data(formatted_data, timestamp)
#     else:
#         formatted_data = None
#         df = None

#     return df, formatted_data, markdown, input_tokens, output_tokens, total_cost, timestamp, pagination_info


#---------------------------------------------------------------
def ChatInput():
    """ Clear the input """
    return Input(id="new-prompt", type="text", name='data',
                 placeholder="Type a message",
                 cls="input input-bordered w-full", hx_swap_oob='true')

#---------------------------------------------------------------
def add_message(data, role):
    """ Add message """

    global scraped_sites_data

    i = len(scraped_sites_data)
    tid = f'message-{i}'

    cls_ = "primary"


    list_item = Div(
                Div(data,
                cls=f"chat-bubble chat-bubble-{cls_}",
                id=tid,
                hx_swap_oob="true"
                ),
                cls = f"chat chat-{role}"
                )
    bag.list_items.append(list_item)

    return list_item

# ---------------------------------------------------------------
def get_loading():
    """ Send loading animation """
    
    global scraped_sites_data
    i = len(scraped_sites_data)
    tid = f'message-{i}'

    loading = Div(
        Div(cls="loading-line", id="loading-line-id"),
        id=tid+"_")

    return loading

# ---------------------------------------------------------------
@app.ws('/scrape')
async def ws(data:str, send, model:str):

    global scraped_sites_data
    
    url = data
    field_list = tags

    await send(
        Div(add_message(data, "end"), hx_swap_oob="beforeend", id="data-list")
    )

    await send(
    Div(get_loading(), hx_swap_oob="beforeend", id="data-list")
    )

    # Send the clear input field command to the user
    await send(ChatInput())

    await asyncio.sleep(0)
    
    pagination_info = {
                "page_urls": [],
                "token_counts": {"input_tokens": 0, "output_tokens": 0},
                "price": 0.0
    }
    
    print(f"DATA: {url}")
    markdown, output_folder = await scrape_multiple_urls(url, field_list, model, tags)

    #formatted_data, token_counts = await format_data(markdown, model, tags)
    
    # Save formatted data
    await send(
        add_message("", "start")
    )
    
    #save_formatted_data(formatted_data, output_folder, f'sorted_data_{0}.json', f'sorted_data_{0}.xlsx')

    #messages.append({"role": "assistant", "content": ""})

    i = len(scraped_sites_data)
    tid = f'message-{i}'

    await send(
                Div(Div(
                    cls="chat-bubble chat-bubble-secondary",
                    id=tid
                    ),
                cls = "chat chat-start",
                hx_swap_oob="outerHTML",
                id=tid+"_"
            )
        )
    
    # delimiter = " "
    # result_string = ""
    # if tags:
    #     result_string = delimiter.join("TAGS: \n")
    #     result_string += delimiter.join(tags)
    
    stream = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        stream=True,
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": USER_MESSAGE + markdown},
        ]
    )

    collected_chunks = []

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            ss = chunk.choices[0].delta.content
            collected_chunks.append(ss)
            await send(
                Div(
                    ss,
                    hx_swap_oob="beforeend",
                    cls="chat-bubble chat-bubble-secondary",
                    id=tid
                    )
        )
            await asyncio.sleep(0.01)  # simulate a brief delay

# Display results if they exist in session state
# if st.session_state['results']:
#     print("printing")
#     all_data, _, first_url_markdown, input_tokens, output_tokens, total_cost, output_folder, pagination_info = st.session_state['results']
    
#     # Display scraping details in sidebar only if scraping was performed and the toggle is on
#     print("Display scraping details:")
#     #if all_data and show_tags:
#     if all_data:
#         print("printing data")
#         # st.sidebar.markdown("---")
#         # st.sidebar.markdown("### Scraping Details")
#         # st.sidebar.markdown("#### Token Usage")
#         # st.sidebar.markdown(f"*Input Tokens:* {input_tokens}")
#         # st.sidebar.markdown(f"*Output Tokens:* {output_tokens}")
#         # st.sidebar.markdown(f"**Total Cost:** :green-background[**${total_cost:.4f}**]")
#         # st.sidebar.markdown(f"*All the data:* {all_data}")
#         st.subheader("---")
#         st.subheader("### Scraping Details")
#         st.subheader("#### Token Usage")
#         st.subheader(f"*Input Tokens:* {input_tokens}")
#         st.subheader(f"*Output Tokens:* {output_tokens}")
#         st.subheader(f"**Total Cost:** :green-background[**${total_cost:.4f}**]")
#         st.json(f"{all_data}")
       
#         # Display scraped data in main area
#         print("Display scraped data in main area")
#         st.subheader("Links from site:")
#         all_data_ = json.loads(all_data[0])
#         for data in all_data_['all-links']:
#             print(f"Data from URL {data}:")
#             st.write(f"{data}:")
            
#             # Handle string data (convert to dict if it's JSON)
#             # if isinstance(data, str):
#             #     try:
#             #         data = json.loads(data)
#             #     except json.JSONDecodeError:
#             #         st.error(f"Failed to parse data as JSON for URL {data}")
#             #         continue
            
#             # if isinstance(data, dict):
#             #     if 'listings' in data and isinstance(data['listings'], list):
#             #         df = pd.DataFrame(data['listings'])
#             #     else:
#             #         # If 'listings' is not in the dict or not a list, use the entire dict
#             #         df = pd.DataFrame([data])
#             # elif hasattr(data, 'listings') and isinstance(data.listings, list):
#             #     # Handle the case where data is a Pydantic model
#             #     listings = [item.dict() for item in data.listings]
#             #     df = pd.DataFrame(listings)
#             # else:
#             #     st.error(f"Unexpected data format for URL {data}")
#             #     continue
            
#             # Display the dataframe
#             #st.dataframe(df, use_container_width=True)

#         # Download options
#         st.subheader("Download Options")
#         col1, col2 = st.columns(2)
#         with col1:
#             json_data = json.dumps(all_data, default=lambda o: o.dict() if hasattr(o, 'dict') else str(o), indent=4)
#             st.download_button(
#                 "Download JSON",
#                 data=json_data,
#                 file_name="scraped_data.json"
#             )
#         with col2:
#             # Convert all data to a single DataFrame
#             all_listings = []
#             for data in all_data:
#                 if isinstance(data, str):
#                     try:
#                         data = json.loads(data)
#                     except json.JSONDecodeError:
#                         continue
#                 if isinstance(data, dict) and 'listings' in data:
#                     all_listings.extend(data['listings'])
#                 elif hasattr(data, 'listings'):
#                     all_listings.extend([item.dict() for item in data.listings])
#                 else:
#                     all_listings.append(data)
            
#             combined_df = pd.DataFrame(all_listings)
#             st.download_button(
#                 "Download CSV",
#                 data=combined_df.to_csv(index=False),
#                 file_name="scraped_data.csv"
#             )

#         st.success(f"Scraping completed. Results saved in {output_folder}")

#     # Add pagination details to sidebar
#     if pagination_info and use_pagination:
#         st.sidebar.markdown("---")
#         st.sidebar.markdown("### Pagination Details")
#         st.sidebar.markdown(f"**Number of Page URLs:** {len(pagination_info['page_urls'])}")
#         st.sidebar.markdown("#### Pagination Token Usage")
#         st.sidebar.markdown(f"*Input Tokens:* {pagination_info['token_counts']['input_tokens']}")
#         st.sidebar.markdown(f"*Output Tokens:* {pagination_info['token_counts']['output_tokens']}")
#         st.sidebar.markdown(f"**Pagination Cost:** :red-background[**${pagination_info['price']:.4f}**]")

#         st.markdown("---")
#         st.subheader("Pagination Information")
#         pagination_df = pd.DataFrame(pagination_info["page_urls"], columns=["Page URLs"])
        
#         st.dataframe(
#             pagination_df,
#             column_config={
#                 "Page URLs": st.column_config.LinkColumn("Page URLs")
#             },use_container_width=True
#         )

#         # Create columns for download buttons
#         col1, col2 = st.columns(2)
#         with col1:
#             st.download_button(
#                 "Download Pagination JSON", 
#                 data=json.dumps(pagination_info["page_urls"], indent=4), 
#                 file_name=f"pagination_urls.json"
#             )
#         with col2:
#             st.download_button(
#                 "Download Pagination CSV", 
#                 data=pagination_df.to_csv(index=False), 
#                 file_name=f"pagination_urls.csv"
#             )

#     # Display combined totals only if both scraping and pagination were performed and both toggles are on
#     if all_data and pagination_info and show_tags and use_pagination:
#         st.markdown("---")
#         total_input_tokens = input_tokens + pagination_info['token_counts']['input_tokens']
#         total_output_tokens = output_tokens + pagination_info['token_counts']['output_tokens']
#         total_combined_cost = total_cost + pagination_info['price']
#         st.markdown("### Total Counts and Cost (Including Pagination)")
#         st.markdown(f"**Total Input Tokens:** {total_input_tokens}")
#         st.markdown(f"**Total Output Tokens:** {total_output_tokens}")
#         st.markdown(f"**Total Combined Cost:** :green[**${total_combined_cost:.4f}**]")

# # Add a clear results button
# if st.sidebar.button("Clear Results"):
#     st.session_state['results'] = None
#     st.session_state['perform_scrape'] = False
#     st.rerun()
            
# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("app:app", host='localhost', port=5001, reload=True)
