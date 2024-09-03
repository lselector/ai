Resume matching app - is app that can extract data from a resume 
and calculate resume rate according to it content

STEPS:

1. Extract data from resume and convert it into standart format
    1.1 Extract data from resume
    1.2 Generate summary about every experience
    1.3 Write standart format as file
2. Generate summary for every resume
3. Generate rate mark (0-10) for every resume
4. Do RAG from all the preparated resumes.
    4.1 Slice resumes into chunks. Best way is 1 resume = 1 chunks
    4.2 Put chunks into ChromaDB
5. Return results to frontend

Standart resume format:
    Name: John Doe
    Address: Kyiv, Ukraine
    web-sites: 
        1. web-site: www.johndoe.com
        2. GitHub: https://github.com/johndoe
        3. LinkedIn: https://www.linkedin.com/in/vitalii-stinskii/
        4. Youtube: ...
        ...

    Contacts:
        1. Email: ...
        2. Phone: ...
        ...

    Skills:
        1. Python
        2. Pandas
        3. Ollama
        ...

    Experience:
        1.  Data: 11/2022 – Present
            Job: Generative AI Developer
            Company: Enterprise Systems
            Address: New York, US
            Summary about experience:
                ... # will be generated
            ...
        
    Education:
        1.  Data: 09/2015 – 12/2020 
            Profession: Software Engineering 
            Degree: Master Degree
            Address: Odessa, Ukraine Odessa National Polytechnic University
            ...

    Summary about the candidate:
    # will be generated
        