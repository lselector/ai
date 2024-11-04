
"""
test02_todo_crud.py
Simple project to show how CRUD operations work.
( CRUD = Create, Read, Update, Delete )

At this moment implemented:
- Create - ready
- Read - ready
- Update - ready
- Delete - ready
"""

from fasthtml.common import *

import levutils
from levutils.mybag import *
from levutils.myutils import *

app, rt, = fast_app(live=True)
bag = MyBunch()

messages = ['Item1', "Item2", "Item3"]

#---------------------------------------------------------------
@rt('/')
def get():
    """ Main page """
    bag.list_items = []
    nums = NumList(5)
    main_page = (
        Title("CRUD List"),
        Titled('CRUD List',
        Div(
            Div(
            P(Img(src="https://fastht.ml/assets/logo.svg", width=100, height=100)),
            ),
            A("About us", href="/about"),
            get_history(),
            Div(P("Add a message with the form below:"),
                Form(Group(Input(id="new-prompt", type="text", name="data"),
                     Button("Submit")),
                     hx_post='/', 
                     target_id='message-list',
                     hx_swap="beforeend"),
                     Div(id='stuff',  hx_get='/change')
                     )
        ))
    )
    
    return main_page

def get_history():
    listed_messages = print_all_messages()
    history = Div(listed_messages)

    return history

#---------------------------------------------------------------
@rt('/')
def post(data:str):
    """ Add message """
    i = len(messages)
    tid = f'message-{i}'
    messages.append(data)
    check = A('Check ',
                hx_post= f'/change_message/{i}',
                hx_target=f"#{tid}",
                hx_swap="innerHTML"
    )
    toggle = A('Delete ',
                hx_delete= f'/delete/{i}',
                hx_target=f"#{tid}",
                hx_swap="outerHTML"
    )
    list_item = Li(check,
                toggle,
                data,
                id=tid)
    bag.list_items.append(list_item)
    clear_input =  Input(id="new-prompt", placeholder="Enter a prompt", type="text", name="data", hx_swap_oob='true')
    return list_item, clear_input

#---------------------------------------------------------------
def NumList(i):
    """ return list of nums """
    return Ul(*[Li(o) for o in range(i)])

#---------------------------------------------------------------
def print_all_messages():
    """ Create ul from messages and return them to main page """
    
    i = 0
    for message in messages:
        tid = f'message-{i}'
                 
        check = A('Check ',
                    hx_post= f'/change_message/{i}',
                    hx_target=f"#{tid}",
                    hx_swap="innerHTML"
        )
        toggle = A('Delete ',
                    hx_delete= f'/delete/{i}',
                    hx_target=f"#{tid}",
                    hx_swap="outerHTML"
        )
        list_item = Li(check,
                       toggle,
                       message,
                       id=tid)  # Create an Li element for each message
        bag.list_items.append(list_item)  # Add the Li element to the list
        i +=1

    return Ul(*bag.list_items, id='message-list')

#---------------------------------------------------------------
@rt('/change')
def get():
    """ fasthtml update example """
    return Titled('Change',
                  P('Change is good!')
                  )

#---------------------------------------------------------------
@rt('/delete/{tid}')
def delete(tid:int):
    """ delete message """
    item = bag.list_items[tid] 
    item = None
    return item

#---------------------------------------------------------------
@rt('/change_message/{tid}')
def post(tid:int):
    """ update message """
    item = bag.list_items[tid] 
    item.children[2] += ' *'
    return item

#---------------------------------------------------------------
@rt('/get_message/{tid}')
def get(tid:int):
    """ get message """
    message = messages[tid]
    return message

#---------------------------------------------------------------
@rt('/about')
def get():
    """ second page """
    nums = NumList(5)
    main_page = (
        Titled('About us',
        Div(
            H1("How Chatbot works:"),
            Div(
            P(Img(src="https://fastht.ml/assets/logo.svg", width=100, height=100)),
            ),
            P("Hi!"),
            #A("Link to Page 2 (to add messages)", href="/page2")
            Div(Div(nums, id='stuff'),
                A("Some text", href="/"))
        ))
    )

    return main_page

serve()
