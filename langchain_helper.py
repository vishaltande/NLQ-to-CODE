from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, RetrievalQA
from langchain.document_loaders import CSVLoader, DirectoryLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings

def get_insights(question):
    # Load and process the CSV data
    # loader = CSVLoader("data/grid_details.csv")
    loader = DirectoryLoader("data/")
    documents = loader.load()

    # Create embeddings
    embeddings = OllamaEmbeddings(model="codellama:instruct")

    chroma_db = Chroma.from_documents(
        documents, embeddings, persist_directory="./chroma_db"
    )
    chroma_db.persist()

    llm = Ollama(model="codellama:instruct")

    prompt_template = PromptTemplate(
        input_variables=["context", "chat_history"],
        template="Given this context: {context}, please directly answer the question: {question}.",
    )

    # Set up the question-answering chain
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=chroma_db.as_retriever(),
        chain_type_kwargs={"prompt": prompt_template},
    )
    print(chroma_db.as_retriever())
    initial = '''
Task Specification:
Generate a Python dictionary representing a database query based on a natural language input. The input question will be asked in natural language, and the output should be in a structured data response. If the query includes any time in hours or seconds, convert it into minutes and then proceed with the output.

Input Specification:
Natural language queries related to the dataset, including questions about specific data points or conditions. Time units may be mentioned in hours or seconds.

Output Specification:
A Python dictionary with the following keys:

- 'select_column': Data to be retrieved
- 'from_table': Dataset containing the necessary data
- 'where': List of conditions to refine the search. Each condition within 'where' is a dictionary specifying the column, relation, and value.

Table Specifications: The data set contains two Tables rf_stats and grid_details 
Table_name : grid_details
Columns:
ship_name : name of the ship (string)
grid_name : grid is a software launched by the neuron in the ships (string)
grid_version : current software version of the grid (string) (in the format x.x.xxx)
grid_uptime : time in minutes since the grid has been active (int)
grid_time_since_version_change : time in minutes since the grid version was updated (int)
grid_ram  : memory in the grid in gigabytes(int)
grid_last_version : last software version of the grid (string) 
Table name : rf-stats
Columns:
ship_name : name of the ship (string)
system : name of the system (string)
system_signal_strength : signal in the system (int)
is_in_blockage : system is blocked or not (int, It has only 0 and 1 value)
system_snr : sound to noise ratio of the system (int)

Examples
Q1. "What is the priority of the ship Nebula?" your system should output:
{
 'select_column' : 'ship_priority', 
'from_table' : rf-stats', 
'where': [{
'column': 'ship_name',
 'relation': '=',
 'value' : nebula}]
}

Q2. Snr of SCPC_1 system in theta ship ?
Output-> { 'select_column' : 'system_snr', 'from_table' : 'rf_stats', 'where': [{'column': 'system', 'relation': '=', 'value' : 'SCPC_1'} , {'column': 'ship_name', 'relation': '=', 'value' : 'theta'}] }
Q3. Which ships have a grid consuming less than 20 gb memory but has an uptime of more than 6 hours?
Output-> { 'select_column' : 'ship_name', 'from_table' : 'grid_details', 'where': [{{'column': 'grid_ram', 'relation': <, 'value' : 20} , {column : grid_uptime , relation : > , value : 360}] }

Additional Context:
The dataset comprises two tables: "grid_details" and "rf_stats". The tables have specific columns and data specifications. The model should accurately handle time unit conversions from hours or seconds to minutes.

Constraints:

- The model should accurately handle time unit conversions from hours or seconds to minutes.
- Ensure the model's output adheres to the specified Python dictionary format.

        '''
    question = initial + question
    result = qa_chain({"query": question})
    return result
