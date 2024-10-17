
"""
app.py
Scraper that uses fastHTML
Features:
- JSON site scraping
- Tags search
- Pagination links search
"""

from fasthtml.common import *

from levutils.mybag import *
from levutils.myutils import *

from scraper import fetch_html_selenium, save_raw_data, save_formatted_data, html_to_markdown_with_readability
from assets import *
import os, asyncio, ollama
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

messages_history = []
pagination_history = ""
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
        Div(Div(Div("Scraped site:", id="scraped-site"),
            Form(
                    Group( 
                     Input(id="new-prompt", type="text", name="data"),
                     Button("Scrape", id="submitButton2")
                     ),
                    id="upload-form",
                    hx_post="/scrape",
                    target_id="scraped-site",
                    hx_swap="outerHTML",
                    cls="upload-cls",
                    ),
                Form(
                    Div(
                        Select(id="shapeInput", name="model")(
                            Option("Llama3.1 8B", value="llama3.1:8b-instruct-q4_1", selected=True),
                            Option("gpt-4o-mini", value="gpt-4o-mini", selected=False),
                           id="select-model"),
                    Label("Tags only:", cls='px-2'),
                        Input(type="checkbox", 
                              cls="checkboxer", 
                              value="tags", 
                              name="isTags", 
                              data_foo="bar",
                              id="tags-checker"
                              ),
                        Div(Textarea("", name="tags"),
                            id="text-area-wrapper", style="display:none;"),

                    cls="model-strict-container"),
                    Group( 
                     Button("Get data", id="submitButton", onclick="setScrollTrue(); clearText()")
                     ),
                    Div(
                    Label("Pagination:", cls="px-2"),
                        Input(type="checkbox", 
                              cls="checkboxer", 
                              value="pagination", 
                              name="pagination", 
                              data_foo="bar",
                              id="pagination-checker"
                              ),cls="pagination-wrapper"),              
                     id="form-id",
                     ws_send=True, hx_ext="ws", ws_connect="/get-data", 
                     target_id='data-list',
                     hx_swap="beforeend",
                     enctype="multipart/form-data",
                     hx_trigger="submit"
                    ),

                    Div("Pagination links:",
                        get_history_pagination(),
                        style="display:none;",
                        id="pagination-links-wrapper",
                        cls="pagination-links-wrapper-cls"
                        )
                    ), cls="wrapper-scrape-controll column"),
        Div( 
            H1("Interactive Document Q&A"),
            Div(
            get_history(),
            cls="history-container"),
            
                    cls="wrapper-chat column",
                    id="wrapper-chat-id"
                    ),
                    Div(
                    Div(
                    
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

                const checkbox = document.getElementById('tags-checker');
                const textareaDiv = document.getElementById('text-area-wrapper');

                checkbox.addEventListener('change', function() {
                if (this.checked) {
                    textareaDiv.style.display = 'block'; // Show the div
                } else {
                    textareaDiv.style.display = 'none';  // Hide the div
                }
                });

                const checkbox2 = document.getElementById('pagination-checker');
                const textareaDiv2 = document.getElementById('pagination-links-wrapper');

                checkbox2.addEventListener('change', function() {
                if (this.checked) {
                    textareaDiv2.style.display = 'block'; // Show the div
                } else {
                    textareaDiv2.style.display = 'none';  // Hide the div
                }
                });

                function clearText() {
                    document.getElementById("pagination-links").innerHTML = "";
                }
            """
        ),
        cls="wrapper-uploaded-files-internal",
        id="uploaded-files-internal"
                    ),
                    cls="wrapper-uploaded-files",

                    ),                             
        cls="wrapper-content"),
        cls="wrapper-main")
    )

    return main_page

#---------------------------------------------------------------
@rt('/scrape')
async def post(data: str):
    """ Main page """

    print("scraping")
    await scrape_and_save_url_data(data)

    return Div(f"Scraped site: {data}", id="scraped-site"), ChatInput()

#---------------------------------------------------------------
def print_all_messages():
    """ Create ul from messages and return them to main page """

    global messages_history
    
    i = 0
    for site_data in messages_history:
        tid = f'site-{i}'

        list_item = Div(
            Pre(site_data, id=tid,
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

#---------------------------------------------------------------
def get_history_pagination():
    """ Get all history messages """ 

    global pagination_history
     
    history = Div(pagination_history, id="pagination-links", hx_swap_oob='true')

    return history

#---------------------------------------------------------------
async def scrape_and_save_url_data(url):
    """ Scrape data from url and save it as .md """
    
    output_folder = os.path.join('output', "site")
    os.makedirs(output_folder, exist_ok=True)
    
    raw_html = fetch_html_selenium(url)
    current_markdown = html_to_markdown_with_readability(raw_html)
    markdown = current_markdown  # Store markdown for the first URL
    save_raw_data(markdown, output_folder, f'rawData.md')
    
    return markdown, output_folder

#---------------------------------------------------------------
def ChatInput():
    """ Clear the input """
    return Input(id="new-prompt", type="text", name='data',
                 placeholder="Type a message",
                 cls="input input-bordered w-full", hx_swap_oob='true')

#---------------------------------------------------------------
def add_message(data, role):
    """ Add message """

    global messages_history

    i = len(messages_history)
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
    
    global messages_history
    i = len(messages_history)
    tid = f'message-{i}'

    loading = Div(
        Div(cls="loading-line", id="loading-line-id"),
        id=tid+"_")

    return loading

#---------------------------------------------------------------
async def ollama_llm_get_pagination_links(send, model, markdown, pagination_prompt):
    """ Get pagination links using Ollama """

    global pagination_history

    ms = []
    ms.append({"role": "assistant", "content": f"Question: \n {pagination_prompt}"})
    ms.append({"role": "user", "content": f"Question: \n {markdown}"})
         
    stream = ollama.chat(
        model=model,
        messages=ms,
        stream=True
    )

    collected_chunks = []
    for chunk in stream:
        chunk = chunk["message"]["content"]
        collected_chunks.append(chunk)
        await send(
                Pre(
                    chunk,
                    hx_swap_oob="beforeend",
                    cls="chat-bubble chat-bubble-secondary",
                    id="pagination-links",
                    )
        )
        await asyncio.sleep(0.01)  # simulate a brief delay

    json_string = "".join(collected_chunks)

    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_folder = os.path.join(script_dir, "output/site/")
    os.makedirs(output_folder, exist_ok=True)

    pagination_history = json_string

    with open(f"{output_folder}pagination_links.txt", 'w') as file:
        file.write(json_string)

#---------------------------------------------------------------
async def openai_llm_get_pagination_links(send, model, markdown, pagination_prompt):
    """ Get pagination links using OpenAI """

    global pagination_history

    stream = client_openai.chat.completions.create(
        model=model,
        stream=True,
        messages=[
            {"role": "system", "content": pagination_prompt},
            {"role": "user", "content": markdown},
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
                    cls="",
                    id="pagination-links",
                    )
        )
            await asyncio.sleep(0.01)  # simulate a brief delay
 
    json_string = "".join(collected_chunks)

    script_dir = os.path.dirname(os.path.realpath(__file__))
    output_folder = os.path.join(script_dir, "output/site/")
    os.makedirs(output_folder, exist_ok=True)

    pagination_history = json_string

    with open(f"{output_folder}pagination_links.txt", 'w') as file:
        file.write(json_string)

#---------------------------------------------------------------
async def get_pagination_links(send, model, markdown, pagination_prompt):
    """ Choose model to get pagination links """

    if model in ["gpt-4o-mini", "gpt-4o-2024-08-06"]:
        await openai_llm_get_pagination_links(send, model, markdown, pagination_prompt)
    elif model == "llama3.1:8b-instruct-q4_1":
        await ollama_llm_get_pagination_links(send, model, markdown, pagination_prompt)

# ---------------------------------------------------------------
@app.ws('/get-data')
async def ws(send, model:str, isTags:str, tags:str, pagination:str):

    global messages_history

    await send(
    Div(get_loading(), hx_swap_oob="beforeend", id="data-list")
    )

    await asyncio.sleep(0)

    await send(
        add_message("", "start")
    )

    script_dir = os.path.dirname(os.path.realpath(__file__))
    markdown = ""
    path = os.path.join(script_dir, "output/site/rawData.md")
    with open(path, "r") as f:
        markdown = f.read()

    user_message = markdown
    if isTags == "tags":
        user_message = f"{USER_MESSAGE} \n TAGS: {tags} \n {markdown}"

    if model in ["gpt-4o-mini", "gpt-4o-2024-08-06"]:
        await openai_llm_get_data(send, model, user_message, SYSTEM_MESSAGE)
    elif model == "llama3.1:8b-instruct-q4_1":
        await ollama_llm_get_data(send, model, user_message, SYSTEM_MESSAGE)

    if pagination == "pagination":
        await get_pagination_links(send, model, markdown, PROMPT_PAGINATION)

#---------------------------------------------------------------
async def ollama_llm_get_data(send, model, user_message, system_message):
    """ Get JSON data from .md file using Ollama """
    
    i = len(messages_history)
    tid = f'message-{i}'

    await send(
                Div(Pre(
                    cls="chat-bubble chat-bubble-secondary",
                    id=tid
                    ),
                cls = "chat chat-start",
                hx_swap_oob="outerHTML",
                id=tid+"_"
            )
        )

    ms = []
    ms.append({"role": "assistant", "content": f"Question: \n {system_message}"})
    ms.append({"role": "user", "content": f"Question: \n {user_message}"})
         
    stream = ollama.chat(
        model=model,
        messages=ms,
        stream=True
    )

    collected_chunks = []
    for chunk in stream:
        chunk = chunk["message"]["content"]
        collected_chunks.append(chunk)
        await send(
                Pre(
                    chunk,
                    hx_swap_oob="beforeend",
                    cls="chat-bubble chat-bubble-secondary",
                    id=tid
                    )
        )
        await asyncio.sleep(0.01)  # simulate a brief delay

    json_string = "".join(collected_chunks)
    messages_history.append(json_string)

    save_formatted_data(json_string)

#---------------------------------------------------------------
async def openai_llm_get_data(send, model, user_message, system_message):
    """ Get JSON data from .md file using OpenAI """

    i = len(messages_history)
    tid = f'message-{i}'

    await send(
                Div(Pre(
                    cls="chat-bubble chat-bubble-secondary",
                    id=tid
                    ),
                cls = "chat chat-start",
                hx_swap_oob="outerHTML",
                id=tid+"_"
            )
        )
    
    stream = client_openai.chat.completions.create(
        model=model,
        stream=True,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]
    )

    collected_chunks = []

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            ss = chunk.choices[0].delta.content
            collected_chunks.append(ss)
            await send(
                Pre(
                    ss,
                    hx_swap_oob="beforeend",
                    cls="chat-bubble chat-bubble-secondary",
                    id=tid
                    )
        )
            await asyncio.sleep(0.01)  # simulate a brief delay
 
    json_string = "".join(collected_chunks)
    messages_history.append(json_string)

    save_formatted_data(json_string)

            
# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("app:app", host='localhost', port=5001, reload=True)
