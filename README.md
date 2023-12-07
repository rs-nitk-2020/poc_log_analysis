# Project Structure for log_analysis_dashboard

This project is a single system that provides log analysis and generates an excel report using a Graphical User Interface (GUI) and whose parent project directory is ***log_analysis_dashboard***.

There are three modules in this project which are in the form three top-level directories or folders. They are

1. ***log_analysis_gui*** : This is the module which contains the UI files with 
    - **templates/log_analysis_gui** : contains html files.
    - **static/css** : contains css files.
    - **static/js** : contains js files.
    - **static/img** : contains any image files.

2. ***log_analysis_api*** : This is the module which contains the core python logic to access environment based logs, analyze and process them and generate reports. The three environments {env} used here are **dev** (for development), **qa** (for quality assurance and user acceptance testing) and **prod** (for production environment).

    These three environments are present under the ***config*** and ***data*** folders, since they are bound to change with respect to environment. The rest of the directories are as follows:
    - **src/services** : for the core process logic of file analysis with a group of functionalities contained in their own file. For example compiler_analysis_service.py has all functions related to compiler log analysis.
    - **src/utils** : has common reusable code such as file_utils.py (for file manipulation functionalities), log_utils for log creation and so on.
    - **tests/services**: has pyunit test cases for the respective service present in src/services
    - **tests/utils** : has pyunit test cases for the respective util functionality.
    - **data/{env}/warnings/Misra Warnings** : has the log files for Misra warnings.
    - **data/{env}/warnings/Compiler Warnings** : has the log files for Compiler warnings.

3. ***log_analysis_dashboard*** : This module has the core Django configuration for rendering the frontend application defined in log_analysis_gui as a web application.

The application launches as a regular Django web application from the parent log_analysis_dashboard folder using **python manage.py runserver**