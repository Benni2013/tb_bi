import streamlit.web.cli as stcli
import sys
import os

if __name__ == '__main__':
    # Get the directory of this script
    dashboard_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_file = os.path.join(dashboard_dir, 'streamlit_dashboard.py')
    
    # Set up the streamlit command
    sys.argv = [
        "streamlit", 
        "run", 
        dashboard_file,
        "--server.port=8501",
        "--server.address=localhost"
    ]
    
    # Run streamlit
    stcli.main()