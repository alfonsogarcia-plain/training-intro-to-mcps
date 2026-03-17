from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

# Tool to read a doc
@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document given its name and return it as a string.",
)
def read_document(
    doc_id: str = Field(description="ID of the document to read, e.g. 'deposition.md'"),
):
    if doc_id not in docs:
        raise ValueError(f"Document with ID '{doc_id}' not found.")
    
    return docs[doc_id]

# Tool to edit a doc
@mcp.tool(
    name="edit_document",
    description="Edit the contents of a document by replacing a string in the document with a new string.",
)
def edit_document(
    doc_id: str = Field(description="ID of the document to edit, e.g. 'deposition.md'"),
    old_string: str = Field(description="The string in the document to be replaced. Must match exactly (including whitespace)."),
    new_string: str = Field(description="The string to replace the old string with."),
):
    if doc_id not in docs:
        raise ValueError(f"Document with ID '{doc_id}' not found.")
    
    docs[doc_id] = docs[doc_id].replace(old_string, new_string)

# Resource that returns all doc IDs
@mcp.resource(
    uri="docs://documents",
    mime_type="application/json",
)
def list_docs() -> list[str]:
    return list(docs.keys())

# Resource that returns the contents of a particular doc given its ID
@mcp.resource(
    uri="docs://documents/{doc_id}",
    mime_type="text/plain",
)
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document with ID '{doc_id}' not found.")
    return docs[doc_id]

# Prompt to rewrite a doc in markdown format
@mcp.prompt(
    name="format",
    description="Rewrites the contents of a document in Markdown format."
)
def format_document(
    doc_id: str = Field(description="ID of the document to format")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax.

    The id of the document you need to reformat is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, tables, etc as necessary. Feel free to add in structure.
    Use the 'edit_document' tool to edit the document. After the document has been reformatted...
    """
    
    return [
        base.UserMessage(prompt)
    ]

# Prompt to summarize a doc
@mcp.prompt(
    name="summarize",
    description="Summarizes the contents of a document."
)
def summarize_document(
    doc_id: str = Field(description="ID of the document to summarize")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to summarize the contents of a document.

    The id of the document you need to summarize is:
    <document_id>
    {doc_id}
    </document_id>

    Provide a concise summary of the document's contents.
    """
    
    return [
        base.UserMessage(prompt)
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")
