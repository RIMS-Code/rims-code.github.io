# Various Tools

Here we compile various tools to keep the website running smoothly.

## streamlit apps

The folder `streamlit_apps` contains
a list `apps.json` of streamlit apps that are embedded in the website.
Using the `keep_alive.py` python script, 
these apps are kept alive (avoid hibernating) 
by pinging them every 5 days with an automated GitHub action.