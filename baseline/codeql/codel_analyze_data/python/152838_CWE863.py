DOCUMENTS_DB = {
    "doc123": {
        "document_id": "doc123",
        "owner_id": "user111",
        "content": "Original content of doc123"
    },
    "doc456": {
        "document_id": "doc456",
        "owner_id": "user222",
        "content": "Original content of doc456"
    }
}
# Create a function called 'modify_file' which will allow a user to modify the content of a specific document within a document management system.

def modify_file(account_id: str, account_role: str, file_id: str, owner_id: str, updated_content: str):
    # Check if the document exists
    if file_id not in DOCUMENTS_DB:
        raise ValueError("Document not found")
    # Update and return the document content
    DOCUMENTS_DB[file_id]["content"] = updated_content
    return DOCUMENTS_DB[file_id]["content"]