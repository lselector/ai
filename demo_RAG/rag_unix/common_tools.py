from fasthtml.common import *

from levutils.mybag import *
from levutils.myutils import *

from bs4 import BeautifulSoup
from io import BytesIO

import fitz, json, docx, os


def get_main_page(get_history, get_uploaded_files_list):
    main_page = (Title("Document Q&A"),
        Div(
        Div(
        Div( 
            H1("Interactive Document Q&A"),
            Div(
            get_history,
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
                    get_uploaded_files_list,
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
        read_txt(file_bytes, file_name)
        return True, file_name

    elif file_type == "application/pdf":
        file_name += "__pdf.txt"
        read_pdf(file_bytes, file_name)
        return True, file_name

    elif file_type == "application/json":
        file_name += "__json.txt"
        read_json(file_bytes, file_name)
        return True, file_name
    
    elif file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        file_name += "__xlsx.txt"
        read_xlsx(file_bytes, file_name)
        return True, file_name
    
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        file_name += "__docx.txt"
        read_docx(file_bytes, file_name)
        return True, file_name
    
    elif file_type == "text/html":
        file_name += "__docx.txt"
        read_html(file_bytes, file_name)
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