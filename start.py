import Ask
import os
import atexit

from flask import Flask, jsonify, request
from flask_cors import CORS
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings


class ChatRequestBody(BaseModel):
    message: str


# Start app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables
os.environ['LANGCHAIN_TRACING-V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY'] = ''
os.environ['OPENAI_API_KEY'] = ''

# Setup LLM
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)

# Load and split text
loader = DirectoryLoader("SupportDocs", show_progress=True)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=500)
docs = loader.load_and_split(text_splitter=text_splitter)

# Create store
vectorstore = Chroma.from_documents(documents=docs, embedding=OpenAIEmbeddings())


# Clean up on close
def cleanup():
    print("Cleaning up...")
    vectorstore.delete_collection()


atexit.register(cleanup)


# Chat endpoint
@app.route('/chat', methods=['POST'])
async def chat():
    user_input = request.json

    if user_input['message'] == "":
        return "I don't think you typed anything. Please try again."
    else:
        result = await Ask.send_chat(user_input, docs, vectorstore, llm)
        return result


# Where to start endpoint
@app.route('/start', methods=['GET'])
async def where_to_start():
    response = {
        "message": "As a new admin, here are 3 articles that might interest you:",
        "articles": [
            {
                "title": "Navigate Home Page",
                "summary": "NetDocuments is an online document management system that enables users to store, access, "
                           "and share documents from anywhere with an internet connection. The platform features a "
                           "customizable interface, including a Home Page and Navigation Pane, and offers a variety "
                           "of tools for document management, such as creating, uploading, and organizing files. "
                           "Users can perform tasks like checking in/out documents, moving/copying files, "
                           "and emailing copies or links. Additionally, NetDocuments supports integration with email "
                           "applications and offers secure document sharing through features like secure links and "
                           "digital signatures. It also accommodates administrators with specific roles for managing "
                           "user access and organizing content within repositories and cabinets.",
                "link": "https://support.netdocuments.com/s/article/360008910091"
            },
            {
                "title": "How to add users",
                "summary": "The Users and Groups guide details how to manage users, groups, and service accounts in a "
                           "NetDocuments repository. It explains how to add, modify, or remove internal and external "
                           "users, assign them to groups, and set access levels. The guide also covers bulk user "
                           "uploads, creating user and group reports, and managing non-interactive service accounts "
                           "for third-party application authentication. Additionally, it explains the differences "
                           "between internal and external members, the roles of repository administrators, "
                           "and provides options for managing group visibility and permissions within the system.",
                "link": "https://support.netdocuments.com/s/article/360056374051"
            },
            {
                "title": "Configure A Workspace",
                "summary": "The guide explains how to create and manage Workspace Templates in NetDocuments, "
                           "primarily for organizing documents by attributes like Matter or Client. These templates "
                           "help centralize related documents, emails, and other materials in a single location for "
                           "easy access. The setup involves defining the base attribute, organizing documents through "
                           "folders, Saved Searches, or Filters, and customizing workspace titles and access rights. "
                           "It also covers creating templates for different Matter types, with a caution against "
                           "modifying templates after workspaces are created, recommending consultation with "
                           "NetDocuments Support for any changes.",
                "link": "https://support.netdocuments.com/s/article/205220310"
            }
        ]
    }

    return jsonify(response)


# What's new endpoint
@app.route('/new', methods=['GET'])
async def what_is_new():
    response = {
        "message": "Here are some new features! <br><ul><li><a "
                   "href='https://support.netdocuments.com/s/article/NetDocuments-M365-Outlook-2-3-Add-in-Available"
                   "-20-August-2024' target=_blank>NetDocuments M365 Outlook 2.3 Add-In Available</a></li><li><a "
                   "href='https://support.netdocuments.com/s/article/Web-Refreshes' target=_blank>Automatic Subfolder "
                   "Searching</a></li><li><a href='https://support.netdocuments.com/s/article/PatternBuilder-Update"
                   "-Notes' target=_blank>PatternBuilder Updated</a></li><li><a "
                   "href='https://support.netdocuments.com/s/article/ndClick-for-Mac-2-0-Beta-Announcement-20-August"
                   "-2024' target=_blank>ndClick for Mac 2.0 Beta Announced</a></li></ul>",
        "link": "https://support.netdocuments.com/s/what-is-new"
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
