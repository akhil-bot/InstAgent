class Tools:
    def __init__(self):
        pass

    def get_available_tools(self):
        tools = [
            {
                "name": "filetool",
                "key": "FILETOOL",
                "appId": "filetool",
                "description": "File I/O tool. Used for any file operations.",
                "categories": ["local", "File Operations"],
                "no_auth": True
            },
            {
                "name": "codeinterpreter",
                "key": "CODEINTERPRETER",
                "appId": "ab43c846-0bd6-4f34-b5f7-5f6dd25edb7b",
                "description": "CodeInterpreter extends Python-based coding environments with integrated data analysis, enabling developers to run scripts, visualize results, and prototype solutions inside supported platforms",
                "categories": ["Developer Tools & DevOps", "Analytics & Data"],
                "no_auth": True
            },
            {
                "name": "browserhub",
                "key": "BROWSERHUB",
                "appId": "a046cb08-47f6-46c7-a66a-66d67b1f37e2",
                "description": "BrowserHub offers powerful web scraping and automation capabilities through its API, allowing for scalable data extraction and browser automation.",
                "categories": ["Workflow Automation", "Analytics & Data"],
                "no_auth": False
            },
            {
                "name": "gmail",
                "key": "GMAIL",
                "appId": "a90e7d79-4f7a-4ff2-bd7d-19c78640b8f8",
                "description": "Connect to Gmail to send and manage emails.",
                "categories": ["Collaboration & Communication"],
                "no_auth":False
            },
            {
                "name": "github",
                "key": "GITHUB",
                "appId": "01e22f33-dc3f-46ae-b58d-050e4d2d1909",
                "description": "GitHub is a code hosting platform for version control and collaboration, offering Git-based repository management, issue tracking, and continuous integration features",
                "categories": ["Developer Tools & DevOps"],
                "no_auth":False
            },
            {
                "name": "googledrive",
                "key": "GOOGLEDRIVE",
                "appId": "417b9b36-3dac-4fb4-8cbd-3b77dff05235",
                "description": "Connect to Google Drive!",
                "categories": ["Document & File Management"],
                "no_auth":False
            },
            {
                "name": "googlesheets",
                "key": "GOOGLESHEETS",
                "appId": "f034804e-ac1e-49ee-8e9d-1c4fab4767f4",
                "description": "Google Sheets is a web-based spreadsheet program that is part of the Google Drive office suite.",
                "categories": ["Productivity & Project Management"],
                "no_auth":False
            },
            {
                "name": "notion",
                "key": "NOTION",
                "appId": "dbfb6202-e358-4271-8a80-a8b6d53a717b",
                "description": "Notion centralizes notes, docs, wikis, and tasks in a unified workspace, letting teams build custom workflows for collaboration and knowledge management",
                "categories": ["Productivity & Project Management"],
                "no_auth":False
            },
            {
                "name": "ragtool",
                "key": "RAGTOOL",
                "appId": "ragtool",
                "description": "Rag Tool",
                "categories": ["local"],
                "no_auth":True
            },
            {
                "name": "reddit",
                "key": "REDDIT",
                "appId": "6ae6f8e7-ef5a-4468-ad5a-e0c3b1a02b8a",
                "description": "Connect to Reddit to post and comment.",
                "categories": ["Marketing & Social Media", "Entertainment & Media"],
                "no_auth":False
            },
            {
                "name": "slack",
                "key": "SLACK",
                "appId": "933dfc28-17b1-4764-95b3-ecd134a9bb06",
                "description": "Slack is a channel-based messaging platform unifying team communication, file sharing, and integrations with external tools for an organized workflow",
                "categories": ["Collaboration & Communication"],
                "no_auth":False
            },
            {
                "name": "linkedin",
                "key": "LINKEDIN",
                "appId": "f1518b4e-453c-4b0a-b163-674fd61fd1f4",
                "description": "Connect to Linked to send and manage emails. A knowledge sharing platform where you can share your thoughts, ideas, and insights.",
                "categories": ["Marketing & Social Media"],
                "no_auth":False
            },
            {
                "name": "tavily",
                "key": "TAVILY",
                "appId": "14fe4af7-3e45-4c50-a92b-9851d7e8a8bb",
                "description": "Tavily provides advanced search capabilities with various options including image inclusion, raw content, and domain filtering.",
                "categories": ["Analytics & Data"],
                "no_auth":False
            },
            {
                "name": "serpapi",
                "key": "SERPAPI",
                "appId": "9826af81-71be-4381-9aa4-ac3d750973c4",
                "description": "SerpApi provides a real-time API for structured search engine results, allowing developers to scrape, parse, and analyze SERP data for SEO and research",
                "categories": ["Analytics & Data"],
                "no_auth":False
            },
            {
                "name": "exa",
                "key": "EXA",
                "appId": "52d547cb-f5d0-4ab5-9709-dde95dc0c77f",
                "description": "The Exa class extends the base Tool class to interact with the Exa Search service, offering actions like Search and Similarlink. These actions enable querying and finding similar links. Currently, no triggers are defined, but they can be added as needed to enhance functionality.",
                "categories": ["Analytics & Data"],
                "no_auth":False
            }
        ]
        return tools