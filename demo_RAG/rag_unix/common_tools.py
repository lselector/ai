
"""
# common_tools.py 
# common methods for chatbots
"""

from fasthtml.common import *

from levutils.mybag import *
from levutils.myutils import *

from bs4 import BeautifulSoup
from io import BytesIO

import fitz, json, docx, os, asyncio, nltk
import ollama, asyncio
from openai import OpenAI

import pandas as pd
from sentence_transformers import SentenceTransformer

bag = MyBunch()

messages = []
messages_for_show = []
bag.uploaded_files = []
bag.uploaded_files_to_show_history = []
bag.not_uploaded_files = []

client_ollama = ollama.Client()
client_openai = OpenAI()

env_var = os.environ.get('OLLAMA_MODEL')
model = ""
if env_var is None:
    print("Environment variable OLLAMA_MODEL is not set.")
    exit()
else:
   model = env_var

#model = "mistral:7b-instruct-v0.3-q4_0"
#model = "llama3:8b-instruct-q4_0"

nltk.download('punkt')
nltk.download('punkt_tab')

bag.embedding_model = SentenceTransformer('all-MiniLM-L6-v2') 

loaded_files_len = 0
chunks_id = 0
bag.script_dir = os.path.dirname(os.path.realpath(__file__))
bag.dir_out = bag.script_dir + "/uploaded_files"

sp = {"role": "system", "content": "You are a helpful and concise assistant."}

def get_main_page():
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
                     ws_send=True, hx_ext="ws", ws_connect="/wscon", 
                     target_id='message-list',
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
                    get_uploaded_files_list(),
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
def convert_files(file_bytes, file_name, file_type, dir_out):
    """ Converts different files to txt """
    print(f"Filename: {file_name}, File type: {file_type}")

    if file_type == "text/plain":
        file_name += "__txt.txt"
        read_txt(file_bytes, file_name, dir_out)
        return True, file_name

    elif file_type == "application/pdf":
        file_name += "__pdf.txt"
        read_pdf(file_bytes, file_name, dir_out)
        return True, file_name

    elif file_type == "application/json":
        file_name += "__json.txt"
        read_json(file_bytes, file_name, dir_out)
        return True, file_name
    
    elif file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        file_name += "__xlsx.txt"
        read_xlsx(file_bytes, file_name, dir_out)
        return True, file_name
    
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        file_name += "__docx.txt"
        read_docx(file_bytes, file_name, dir_out)
        return True, file_name
    
    elif file_type == "text/html":
        file_name += "__docx.txt"
        read_html(file_bytes, file_name, dir_out)
        return True, file_name
    
    return False, None

#---------------------------------------------------------------
def read_html(file_bytes,filename, dir_out):
    """ Read MS Word file """

    soup = BeautifulSoup(BytesIO(file_bytes), 'html.parser')

    # Extract all the text from the HTML
    all_text = soup.get_text(separator='\n')  # Use '\n' as separator for better readability

    write_txt(all_text.strip().encode('utf-8'), filename, dir_out) 

#---------------------------------------------------------------
def read_docx(file_bytes,filename, dir_out):
    """ Read MS Word file """

    doc = docx.Document(BytesIO(file_bytes))

    # Extract text from the document
    all_text = ""
    for paragraph in doc.paragraphs:
        all_text += paragraph.text + "\n"

    write_txt(all_text.encode('utf-8'), filename, dir_out) 

#---------------------------------------------------------------
def read_xlsx(file_bytes,filename, dir_out):
    """ Read Excel file """

    excel_data = pd.read_excel(BytesIO(file_bytes))

    output = BytesIO()
    excel_data.to_excel(output, index=False)  # Write DataFrame to the BytesIO object
    text_content = excel_data.to_csv(index=False, sep='\t').replace('\t', ' ')  

    #print(text_content)
    write_txt(text_content.encode('utf-8'), filename, dir_out) 


#---------------------------------------------------------------
def read_json(json_data, filename, dir_out):
    """ Read JSON file """

    #print(f"Text from json: {json_data}", flush=True) 

    if isinstance(json_data, bytes):
        json_data = json_data.decode('utf-8')
        json_data = json.loads(json_data)  # Now parse the JSON string
    
    text_ = ""

    def extract_text_recursive(data):
        nonlocal text_

        if isinstance(data, dict):
            for value in data.values():
                extract_text_recursive(value)
        elif isinstance(data, list):
            for item in data:
                extract_text_recursive(item)
        elif isinstance(data, str):
            text_ += data + " "  

    extract_text_recursive(json_data)
    write_txt(text_.strip().encode('utf-8'), filename, dir_out)

#---------------------------------------------------------------
def read_pdf(file_bytes,filename,dir_out):
    """ Read PDF file """
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf:  # Open PDF from bytes
        for page in pdf:
            text += page.get_text()
    
    bytes = text.encode('utf-8') 
    write_txt(bytes, filename, dir_out)

#---------------------------------------------------------------
def read_txt(file_bytes,filename,dir_out):
    """ Read txt file """
    write_txt(file_bytes, filename,dir_out)

#---------------------------------------------------------------
def write_txt(bytes, filename, dir_out):
    """ Write extracted text to txt file, use file name of original file """
    write_path = dir_out
    os.makedirs(write_path, exist_ok=True)
    write_path += "/"+filename
    print(f"saving file: {write_path}")
    with open(write_path, "wb") as file:
        file.write(bytes)

# ---------------------------------------------------------------
def get_loading():
    """ Send loading animation """
    
    i = len(messages_for_show)
    tid = f'message-{i}'

    loading = Div(
        Div(cls="loading-line", id="loading-line-id"),
        id=tid+"_")

    return loading

#---------------------------------------------------------------
def get_uploaded_files_list():
    """ Get all uploaded files names """ 

    lis = []
    for filename in bag.uploaded_files_to_show_history:

        lis.append(
            Li(filename, cls='uploaded-file-cls')
        )

    if len(lis) == 0:
        return Div(Ul(id='uploaded-files-list', cls="uploaded-files-list-cls"), id="files-container", hx_swap_oob='true')

    return Div(Ul(*lis, id='uploaded-files-list', cls="uploaded-files-list-cls"), id="files-container", hx_swap_oob='true')

#---------------------------------------------------------------
def get_history():
    """ Get all history messages """ 
    listed_messages = print_all_messages()
    history = Div(listed_messages, id="chatlist", cls="list-of-messages")

    return history

#---------------------------------------------------------------
def add_message(data, role):
    """ Add message """
    i = len(messages_for_show)
    tid = f'message-{i}'
 
    cls_ = ""

    if role == "end":
        cls_ = "primary"
    elif role =="start":
        cls_ = "secondary"

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

#---------------------------------------------------------------
def print_all_messages():
    """ Create ul from messages and return them to main page """
    
    i = 0
    for message in messages_for_show:
        tid = f'message-{i}'

        if message['role'] == "assistant":
            list_item = Div(
                Div(message['content'], id=tid,
                    cls="chat-bubble chat-bubble-secondary"),
                cls = "chat chat-start")
            bag.list_items.append(list_item)  # Add the Li element to the list
        
        elif message['role'] == "user":
            list_item = Div(
                Div(message['content'], id=tid,
                    cls="chat-bubble chat-bubble-primary"),
                cls = "chat chat-end")
            bag.list_items.append(list_item)  # Add the Li element to the list
        
        i +=1
        

    return Div(*bag.list_items, id='message-list')

# ---------------------------------------------------------------
async def split_to_chunks(text):
    """ Spit txt to chunks """
    sentences = nltk.sent_tokenize(text)
    chunk_size = 3 
    chunks = [' '.join(sentences[i:i+chunk_size]) for i in range(0, len(sentences), chunk_size)] 
    return chunks

# ---------------------------------------------------------------
async def save_or_reload_file(uploaded_files, isFileUploaded, load_file, delete_file, is_file_uploaded_=None):
        """ Save or reload uploaded file """
        
        uploaded_files_to_show = []
        not_uploaded_files_to_show = []
        
        for uploaded_file in uploaded_files:

            print(f"Uploaded file: {uploaded_file.filename}")

            file_bytes = await uploaded_file.read()

            file_name = uploaded_file.filename.split('.')[0]
            file_type = uploaded_file.headers.get("content-type") 
            isCorrectType, filename = convert_files(file_bytes, file_name, file_type, bag.dir_out)

            if not isCorrectType:
                print("Wrong Type!")
                not_uploaded_files_to_show.append(uploaded_file.filename+" is not uploaded")
                bag.not_uploaded_files.append(uploaded_file.filename)
                continue
            print(f"Method: {isFileUploaded}")
            is_file_uploaded_, ids_to_reload = await isFileUploaded(filename)

            print(f"is_file_uploaded_:{is_file_uploaded_}")

            if is_file_uploaded_:
                print(f"reloading...{uploaded_file.filename}")
                delete_file(filename)
                
            else:
                print(f"adding...{uploaded_file.filename}")
                bag.uploaded_files.append(filename)
                bag.uploaded_files_to_show_history.append(uploaded_file.filename)
                uploaded_files_to_show.append(uploaded_file.filename)
            
            await load_file(filename,f"{bag.dir_out}/{filename}", ids_to_reload, is_file_uploaded_)

        return uploaded_files_to_show, not_uploaded_files_to_show

# ---------------------------------------------------------------
async def upload_file(request, isFileUploaded, load_file, delete_file): 
    """ Upload file """
    form = await request.form()
    uploaded_files = form.getlist("files")  # Use getlist to get a list of files
    error_true = Div("Wrong filetype. Allowed only: .txt, .xlsx, .docx, .json, .pdf, .html", hx_swap_oob='true', id="error-message", style="color: red; font-size: 14px;")
    error_false = Div("Wrong filetype. Allowed only: .txt, .xlsx, .docx, .json, .pdf, .html",  hx_swap_oob='true', id="error-message", style="display: none; color: red; font-size: 14px;")
    os.makedirs(bag.dir_out, exist_ok=True)
    print(f"Files to upload: {uploaded_files}")
    uploaded_files_to_show, not_uploaded_files_to_show = await save_or_reload_file(uploaded_files, isFileUploaded, load_file, delete_file)
    list_items = []

    for uploaded_file in uploaded_files_to_show:
        list_item = Li(f"{uploaded_file}", id='uploaded-file')
        list_items.append(list_item)

    if len(not_uploaded_files_to_show) > 0:
        for not_uploaded_file in not_uploaded_files_to_show:
            list_item = Li(f"{not_uploaded_file}", id='not-uploaded-file', style="color: red")
            list_items.append(list_item) 

        return list_items, error_true
               
    if len(bag.not_uploaded_files) > 0:

        bag.not_uploaded_files = []
        return get_uploaded_files_list(), error_false
    
    return list_items, error_false

# ---------------------------------------------------------------
async def chat_ollama(send):
    """ Send message to Ollama model """

    await send(
        add_message("", "start")
    )

    # Model response (streaming)
    stream = ollama.chat(
        model=model,
        messages=[sp] + messages,
        stream=True,
    )
    
    # Send an empty message with the assistant response
    messages.append({"role": "assistant", "content": ""})

    i = len(messages_for_show)
    tid = f'message-{i}'

    msg = ""

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

    # Fill in the message content
    for chunk in stream:
        chunk = chunk["message"]["content"]
        msg = msg + chunk
        messages[-1]["content"] += chunk
        await send(
                Div(
                    chunk,
                    hx_swap_oob="beforeend",
                    cls="chat-bubble chat-bubble-secondary",
                    id=tid
                    )
        )
        await asyncio.sleep(0.01)  # simulate a brief delay

    messages.append({"role": "assistant", "content": ''.join(msg)})
    messages_for_show.append({"role": "assistant", "content": ''.join(msg)})
    
# ---------------------------------------------------------------
async def chat_openai(send):
    """ Send message to OpenAI model """

    await send(
        add_message("", "start")
    )

    stream = client_openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    stream=True,
    )

    messages.append({"role": "assistant", "content": ""})
    
    
    collected_chunks = []

    i = len(messages_for_show)
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

    messages.append({"role": "assistant", "content": ''.join(collected_chunks)})
    messages_for_show.append({"role": "assistant", "content": ''.join(collected_chunks)})

#---------------------------------------------------------------
def ChatInput():
    """ Clear the input """
    return Input(id="new-prompt", type="text", name='data',
                 placeholder="Type a message",
                 cls="input input-bordered w-full", hx_swap_oob='true')

#---------------------------------------------------------------
async def do_chat(data, isRAG, strict, model, send, do_rag):
    """ Chat between LLM and User """

    print(f"isRag: {isRAG}, strict: {strict}")

    await send(
        Div(add_message(data, "end"), hx_swap_oob="beforeend", id="message-list")
    )
    
    messages_for_show.append({"role": "user", "content": f"{data}"})
    
    await send(
        Div(get_loading(), hx_swap_oob="beforeend", id="message-list")
    )

    # Send the clear input field command to the user
    await send(ChatInput())

    await asyncio.sleep(0)

    if isRAG:
        context = await do_rag(data)

        print(f"doing rag: {context}")

        for l in context:
            if len(l) == 0:
                if strict == "strict":
                    messages.append({"role": "user", "content": f"Say: In strict mode I answer only using uploaded files. Please appload files"})
                    print("strict+")
                    break
                else:
                    messages.append({"role": "user", "content": f"Question: \n {data}"})
                    print("strict-") 
                    break 
                        
            else:
                if strict == "strict":
                   messages.append({"role": "user", "content": f"Context: \n {context}, Question: \n {data}\n\n Generate your answer only using context. If meaning of the question is not in the context say: \n There is no information about it in the document. If the answer is in history - use history to create answer"})
                   print("strict++")
                   break
                else:
                    messages.append({"role": "user", "content": f"Context: \n {context}, Question: \n {data}answer the question even if it not in the context"})
                    print("strict--")
                    break
                    
    else:
        if strict == "strict":
            messages.append({"role": "user", "content": f"Say: In strict mode I answer only using uploaded files. Please appload files"})
            print("strict+++")
        else:
            messages.append({"role": "user", "content": f"Question: \n {data}answer the question even if it not in the context"})
            print("strict---")  

    if model == "ollama":
        await chat_ollama(send)
    elif model == "openai":
        await chat_openai(send)