# Commercial Real Estate Knowledge Assistant

![Commercial Lending 101](Dataset/commercial-lending-101.png)

A sophisticated Retrieval-Augmented Generation (RAG) chatbot that transforms how professionals understand commercial real estate concepts. Built with Azure OpenAI and modern Python technologies, this assistant processes commercial real estate documentation and provides accurate, context-aware answers to your questions.

## 🚀 Deployments
- **Live Demo**: [Try it on Hugging Face Spaces](https://huggingface.co/spaces/tony-42069/cre-chatbot-rag)

## 🌟 Key Features
- **Multi-Document Support**: Process and analyze multiple PDF documents simultaneously
- **Intelligent PDF Processing**: Advanced document analysis and text extraction
- **Azure OpenAI Integration**: Leveraging GPT-3.5 Turbo for accurate, contextual responses
- **Semantic Search**: Using Azure OpenAI embeddings for precise context retrieval
- **Vector Storage**: Efficient document indexing with ChromaDB
- **Modern UI**: Beautiful chat interface with message history and source tracking
- **Enterprise-Ready**: Comprehensive logging and error handling

## 🎯 Use Cases
- **Training & Education**: Help new CRE professionals understand industry concepts
- **Quick Reference**: Instant access to definitions and explanations
- **Document Analysis**: Extract insights from CRE documentation
- **Knowledge Base**: Build and query your own CRE knowledge repository

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Azure OpenAI Service access with:
  - `gpt-35-turbo` model deployment
  - `text-embedding-ada-002` model deployment

### Installation
1. Clone the repository:
```bash
git clone https://github.com/tony-42069/cre-chatbot-rag.git
cd cre-chatbot-rag
```

2. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with Azure OpenAI credentials:
```env
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_KEY=your_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_gpt_deployment_name
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002
```

5. Run the application:
```bash
streamlit run app/main.py
```

## 🔌 Embedding
To embed this chatbot in your website, use the following HTML code:

```html
<iframe
    src="https://tony-42069-cre-chatbot-rag.hf.space"
    frameborder="0"
    width="850px"
    height="450px"
></iframe>
```

## 💡 Features

### Modern Chat Interface
- Clean, professional design
- Persistent chat history
- Source context tracking
- Multiple document management
- Real-time processing feedback

### Advanced RAG Implementation
- Semantic chunking of documents
- Azure OpenAI embeddings for accurate retrieval
- Context-aware answer generation
- Multi-document knowledge base
- Source attribution for answers

### Enterprise Security
- Secure credential management
- Azure OpenAI integration
- Local vector storage with ChromaDB
- Comprehensive error handling
- Detailed logging system

## 🛠️ Technical Stack
- **Frontend**: Streamlit
- **Language Models**: Azure OpenAI (GPT-3.5 Turbo)
- **Embeddings**: Azure OpenAI (text-embedding-ada-002)
- **Vector Store**: ChromaDB
- **PDF Processing**: PyPDF2
- **Framework**: LangChain

## 📚 Documentation
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service/)
- [Streamlit](https://streamlit.io/)
- [LangChain](https://python.langchain.com/)
- [ChromaDB](https://www.trychroma.com/)

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments
- Azure OpenAI team for providing the powerful language models
- LangChain community for the excellent RAG framework
- Streamlit team for the amazing web framework
