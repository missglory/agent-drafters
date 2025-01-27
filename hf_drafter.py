from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from phoenix.otel import register

from smolagents import (
    CodeAgent,
    DuckDuckGoSearchTool,
    LiteLLMModel,
    ManagedAgent,
    ToolCallingAgent,
    VisitWebpageTool,
)




from smolagents import tool 
# import packages that are used in our tools
import requests
from bs4 import BeautifulSoup
import json

@tool
def get_hugging_face_top_daily_paper() -> str:
    """
    This is a tool that returns the most upvoted paper on Hugging Face daily papers.
    It returns the title of the paper
    """
    try:
      url = "https://huggingface.co/papers"
      response = requests.get(url)
      response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
      soup = BeautifulSoup(response.content, "html.parser")

      # Extract the title element from the JSON-like data in the "data-props" attribute
      containers = soup.find_all('div', class_='SVELTE_HYDRATER contents')
      top_paper = ""

      for container in containers:
          data_props = container.get('data-props', '')
          if data_props:
              try:
                  # Parse the JSON-like string
                  json_data = json.loads(data_props.replace('&quot;', '"'))
                  if 'dailyPapers' in json_data:
                      top_paper = json_data['dailyPapers'][0]['title']
              except json.JSONDecodeError:
                  continue

      return top_paper
    except requests.exceptions.RequestException as e:
      print(f"Error occurred while fetching the HTML: {e}")
      return None

from huggingface_hub import HfApi

@tool
def get_paper_id_by_title(title: str) -> str:
    """
    This is a tool that returns the arxiv paper id by its title.
    It returns the title of the paper

    Args:
        title: The paper title for which to get the id.
    """
    api = HfApi()
    papers = api.list_papers(query=title)
    if papers:
        paper = next(iter(papers))
        return paper.id
    else:
        return None
    
import arxiv

@tool
def download_paper_by_id(paper_id: str) -> None:
    """
    This tool gets the id of a paper and downloads it from arxiv. It saves the paper locally 
    in the current directory as "paper.pdf".

    Args:
        paper_id: The id of the paper to download.
    """
    paper = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))
    paper.download_pdf(filename="paper.pdf")
    return None


from pypdf import PdfReader

@tool
def read_pdf_file(file_path: str) -> str:
    """
    This function reads the first three pages of a PDF file and returns its content as a string.
    Args:
        file_path: The path to the PDF file.
    Returns:
        A string containing the content of the PDF file.
    """
    content = ""
    reader = PdfReader('paper.pdf')
    print(len(reader.pages))
    pages = reader.pages[:3]
    for page in pages:
        content += page.extract_text()
    return content  


# Let's setup the instrumentation first

trace_provider = TracerProvider()
trace_provider = register(
  endpoint="http://localhost:4317",  # Sends traces using gRPC
)
trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter("http://0.0.0.0:6006/v1/traces")))

SmolagentsInstrumentor().instrument(tracer_provider=trace_provider)

# Then we run the agentic part!
# model = HfApiModel()
model = LiteLLMModel(
    # model_id="ollama/qwen2.5-coder:32b-instruct-q4_K_M",
    model_id="ollama/llama3.3:70b-instruct-q4_K_S",
    api_base="http://localhost:11434",  # replace with remote open-ai compatible server if necessary
    api_key="your-api-key",  # replace with API key if necessary
)

agent = CodeAgent(
    # tools=[
        # DuckDuckGoSearchTool(), 
        # VisitWebpageTool()
        # ],
    tools=[get_hugging_face_top_daily_paper,
                         get_paper_id_by_title,
                         download_paper_by_id,
                         read_pdf_file],
    model=model,
    additional_authorized_imports=['bs4', 'requests']
)
managed_agent = ManagedAgent(
    agent=agent,
    name="managed_agent",
    description="This is an agent that can parse hf papers",
)
manager_agent = CodeAgent(
    # tools=[DuckDuckGoSearchTool(), VisitWebpageTool()],
    tools=[],
    model=model,
    managed_agents=[managed_agent],
)

manager_agent.run(
    # "If the US keeps it 2024 growth rate, how many years would it take for the GDP to double?"
    "Summarize today's top paper on Hugging Face daily papers by reading it.",
)


# agent = CodeAgent(tools=[get_hugging_face_top_daily_paper,
#                          get_paper_id_by_title,
#                          download_paper_by_id,
#                          read_pdf_file],
#                   model=model,
#                   add_base_tools=True)

# agent.run(
#     "Summarize today's top paper on Hugging Face daily papers by reading it.",
# )


