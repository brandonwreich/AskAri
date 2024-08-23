from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


async def send_chat(request_input, docs, vectorstore, llm):
    message = request_input["message"]
    if (message == "hello" or
            message == "hi" or
            message == "Hello" or
            message == "Hi"):
        return "Hello! My name is Ari Adams. How can I help you today?"
    elif (message == "How are you?" or
          message == "how are you?" or
          message == "How are you" or
          message == "how are you"):
        return ("I'm an AI, so I don't have feelings, but I'm here and ready to help you with any questions or tasks "
                "you have! How can I assist you today?")

    # Retrieve and generate using the relevant snippets of the blog.
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
    prompt = hub.pull("rlm/rag-prompt")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )

    result = rag_chain.invoke(request_input["message"])

    if (result == "I don't know." or
            "The provided context does not indicate" in result or
            "The provided context does not contain" in result or
            "The context does not provide specific information" in result or
            "I don't have specific information about" in result or
            "I don't have information specifically about" in result or
            "I don't have information about" in result):
        result = ("I am not quite sure I understand. Could you please rephrase your question? If you require extra "
                  "help, click <a href='https://support.netdocuments.com/s/flow/Create_Customer_Case' "
                  "target='_blank'>here</a> to submit a support ticket.")
        return result
    if (("document" in message or
         "doc" in message or
         "user" in message or
         "ndmail" in message) and
            (not "netdocuments" in message and
             not "Netdocuments" in message and
             not "netdocs" in message)):
        result += "<br><br>Here are some topics that might interest you:"
        if "document" in message or "doc" in message:
            result += ("<br> <ul><li><a href='https://support.netdocuments.com/s/article/205217720' "
                       "target='_blank'>Adding Documents</a></li><li><a "
                       "href='https://support.netdocuments.com/s/article/205220330' target='_blank'>Add or Edit a Profile "
                       "Value</a></li><li><a href='https://support.netdocuments.com/s/article/205217480' "
                       "target='_blank'>Profiling a Document</a></li><li><a "
                       "href='https://support.netdocuments.com/s/article/205217360' target='_blank'>Version "
                       "Management</a></li><li><a href='https://support.netdocuments.com/s/article/205217700' "
                       "target='_blank'>Modify Access List</a></li></ul>")

        if "user" in message:
            result += ("<br><ul><li><a href='https://support.netdocuments.com/s/article/360056374051' "
                       "target='_blank'>Users and Groups</a></li><li><a "
                       "href='https://support.netdocuments.com/s/article/205218900' target='_blank'>External User "
                       "Access</a></li></ul>")

        if "ndmail" in message:
            result += ("<br><ul><li><a href='https://support.netdocuments.com/s/article/360014624391' "
                       "target=_blank>ndMail</a></li><li><a "
                       "href='https://support.netdocuments.com/s/article/M365-Outlook' target=_blank>M365 "
                       "Outlook</a></li></ul>")

    return result
