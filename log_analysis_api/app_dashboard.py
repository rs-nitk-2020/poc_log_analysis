from typing import Any, OrderedDict

from django.http import FileResponse, HttpResponse
from log_analysis_api.src.utils.property_utils import PropertyLoader, DictToObject
from log_analysis_api.src.utils.log_utils import LoggingUtils
from log_analysis_api.src.services.compiler_warning_ops import CompilerWarningReport as cwr
from log_analysis_api.src.services.misra_warning_ops import execute as exe
from log_analysis_api.src.utils.date_time_utils import DateTimeOps as date_time_ops
from log_analysis_api.src.utils.file_utils import FileOps as file_ops
import os
    
class LogAnalysisApi:
    
    def __init__(self, env: str= 'dev', properties_config_file: str = 'config/dev/properties.yaml'):
        """
        Initialses the back end evironment, logs and properties when invoked from the front end GUI

        Args:
            env (str, optional): _description_. Defaults to 'dev'.
            properties_config_file (str, optional): _description_. Defaults to 'config/dev/properties.yaml'.
        """
        yaml_file_path = properties_config_file
        properties = PropertyLoader.load_properties_from_yaml(yaml_file_path)
        self.env = env
        self.props = DictToObject(properties)
        self.log = LoggingUtils.time_rotated_log(props = self.props,
                                                log_dir_path=f'log_analysis_api/logs/{env}/')

    
    def load_gui_basic_data(self)-> OrderedDict:
        """
        Invoked from the GUI to load options and validations for log analysis

        Returns:
            OrderedDict: Dictionary of GUI options to load and populate the form entry page options.
        """
        basic_data = OrderedDict()
        basic_data['log_analysis_options'] = self.props.log_analysis_options.to_dict()
        basic_data['log_analysis_valid_file_patterns'] = self.props.log_analysis_valid_file_patterns.to_dict()
        return basic_data
    
    def process_compiler_warnings(self, files: Any):
        """
        Accepts file objects from the front end GUI, processes them and sends the generated report 
        and report name back to the GUI

        Args:
            files (Any): File objects passed from the front end

        Returns:
            OrderedDict, str: report data and report name
        """
        log_and_report_dir_name = date_time_ops.get_current_timestamp_utc(self.props.compiler_warning_report_props.report_prefix)
        log_and_report_dir_path = os.path.join(f"log_analysis_api/data/{self.env}/warnings/Compiler Warnings",log_and_report_dir_name)
        file_ops.create_dir(log_and_report_dir_path)
        for file in files.getlist("files[]"):
            file_name = file.name
            file_content = file.read()
            file_destination = os.path.join(log_and_report_dir_path, file_name)
            with open(file_destination, 'wb') as destination:
                destination.write(file_content)
        
        report_name = "_".join([log_and_report_dir_name, self.props.compiler_warning_report_props.report_suffix])
        report_path = os.path.join(log_and_report_dir_path, report_name)

        report_data = cwr().process_compiler_report(log_directory=log_and_report_dir_path, report_path=report_path, props=self.props)

        return report_data, report_name
    
    def process_misra_warnings(self, files: Any):

        log_and_report_dir_name = date_time_ops.get_current_timestamp_utc(self.props.misra_warning_report_props.report_prefix)
        log_and_report_dir_path = os.path.join(f"log_analysis_api/data/{self.env}/warnings/Misra Warnings",log_and_report_dir_name)
        report_name = "_".join([log_and_report_dir_name, self.props.misra_warning_report_props.report_suffix])
        report_path = os.path.join(log_and_report_dir_path, report_name)
        file_ops.create_dir(log_and_report_dir_path)
        for file in files.getlist("files[]"):
            file_name = file.name
            file_content = file.read()
            file_destination = os.path.join(log_and_report_dir_path, file_name)
            with open(file_destination, 'wb') as destination:
                destination.write(file_content)
        report_data = exe(log_directoryy=log_and_report_dir_path, report_path=report_path, props=self.props)
        return report_data, report_name
    
    def download_report(self, report_name):
        base_dir = os.path.dirname(__file__)  # Get the base directory of the current file
        report_parts = report_name.split("_")
        # This logic is specific to report format YYYYMMDD_HHMMSS_Type_Warnings_Report.xlsx
        # If the pattern changes then logic needs to be changed , here type is Compiler or MISRA
        log_and_report_dir_name = "_".join(report_parts[:2])
        if 'compiler' in report_name.casefold():
            report_path = os.path.join(base_dir,f"data/{self.env}/warnings/Compiler Warnings",log_and_report_dir_name, report_name)
        elif 'misra' in report_name.casefold():
            report_path = os.path.join(base_dir,f"data/{self.env}/warnings/Misra Warnings",log_and_report_dir_name, report_name)
        else:
            return HttpResponse("Invalid File")
        
        return report_path


