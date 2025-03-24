class Tools:
    def __init__(self):
        pass

    def get_available_tools(self):
        tools = [
            {
                "name": "filetool",
                "key": "FILETOOL",
                "description": "File I/O tool. Used for any file operations.",
                "categories": ["File Operations"],
                "no_auth": True
            },
            {
                "name": "codeinterpreter",
                "key": "CODEINTERPRETER",
                "description": "CodeInterpreter extends Python-based coding environments with integrated data analysis, enabling developers to run scripts, visualize results, and prototype solutions inside supported platforms",
                "categories": ["Developer Tools & DevOps", "Scripting", "Visualization"],
                "no_auth": True
            },
            {
                "name": "tavily",
                "key": "TAVILY",
                "description": "Tavily provides advanced search capabilities with various options including image inclusion, raw content, and domain filtering.",
                "categories": ["web scraping", "research", "analysis", "Analytics & Data", "Search Optimization", "Data Retrieval", "Internet Search"],
                "no_auth":False
            },
            {
                "name": "serpapi",
                "key": "SERPAPI",
                "description": "SerpApi provides a real-time API for structured search engine results, allowing developers to scrape, parse, and analyze SERP data for SEO and research",
                "categories": ["web scraping", "research", "analysis", "Analytics & Data", "SEO Tools", "Data Analysis", "Internet Search"],
                "no_auth":False
            },
            {
                "name": "browserhub",
                "key": "BROWSERHUB",
                "description": "BrowserHub offers powerful web scraping and automation capabilities through its API, allowing for scalable data extraction and browser automation.",
                "categories": ["Workflow Automation", "Analytics & Data", "Web Scraping", "Automation"],
                "no_auth": False
            },
            {
                "name": "gmail",
                "key": "GMAIL",
                "description": "Connect to Gmail to send and manage emails.",
                "categories": ["Collaboration & Communication", "Email Management", "Productivity"],
                "no_auth":False
            },
            {
                "name": "github",
                "key": "GITHUB",
                "description": "GitHub is a code hosting platform for version control and collaboration, offering Git-based repository management, issue tracking, and continuous integration features",
                "categories": ["Developer Tools & DevOps", "Version Control", "Collaboration"],
                "no_auth":False
            },
            {
                "name": "googledrive",
                "key": "GOOGLEDRIVE",
                "description": "Connect to Google Drive!",
                "categories": ["Document & File Management", "Cloud Storage", "Collaboration"],
                "no_auth":False
            },
            {
                "name": "googlesheets",
                "key": "GOOGLESHEETS",
                "description": "Google Sheets is a web-based spreadsheet program that is part of the Google Drive office suite.",
                "categories": ["Productivity & Project Management", "Data Analysis", "Collaboration"],
                "no_auth":False
            },
            {
                "name": "notion",
                "key": "NOTION",
                "description": "Notion centralizes notes, docs, wikis, and tasks in a unified workspace, letting teams build custom workflows for collaboration and knowledge management",
                "categories": ["Productivity & Project Management", "Knowledge Management", "Collaboration"],
                "no_auth":False
            },
            {
                "name": "ragtool",
                "key": "RAGTOOL",
                "description": "Rag Tool",
                "categories": ["local", "Utilities", "Data Management"],
                "no_auth":True
            },
            {
                "name": "reddit",
                "key": "REDDIT",
                "description": "Connect to Reddit to post and comment.",
                "categories": ["Marketing & Social Media", "Entertainment & Media", "Community Engagement"],
                "no_auth":False
            },
            {
                "name": "slack",
                "key": "SLACK",
                "description": "Slack is a channel-based messaging platform unifying team communication, file sharing, and integrations with external tools for an organized workflow",
                "categories": ["Collaboration & Communication", "Team Management", "Productivity"],
                "no_auth":False
            },
            {
                "name": "linkedin",
                "key": "LINKEDIN",
                "description": "Connect to Linked to send and manage emails. A knowledge sharing platform where you can share your thoughts, ideas, and insights.",
                "categories": ["Marketing & Social Media", "Professional Networking", "Content Sharing"],
                "no_auth":False
            },
            {
                "name": "exa",
                "key": "EXA",
                "description": "The Exa class extends the base Tool class to interact with the Exa Search service, offering actions like Search and Similarlink. These actions enable querying and finding similar links. Currently, no triggers are defined, but they can be added as needed to enhance functionality.",
                "categories": ["Analytics & Data", "Search Tools", "Data Retrieval", "Web Search"],
                "no_auth":False
            },
            {
                "name": "youtube",
                "key": "YOUTUBE",
                "description": "Youtube actions to interact with youtube app",
                "categories": ["Entertainment & Media", "Video Streaming", "Content Creation"],
                "no_auth":False
            }
        ]
        return tools