import math
import os
import re
from typing import Any, OrderedDict
import pandas as pd
from collections import Counter
from log_analysis_api.src.utils.report_utils import ReportOps as reports
from multiprocessing import Pool

class CompilerWarningReport:
    """
    Conatins methods for compiler report validation, formatting of sheets and report generation.
    """

    def _generate_driverwise_count_sheet_data(self):
        """
        This method generates the driverwise count from the dataframe contained in the filewise calculation sheet
        """
        df_filewise_count = self.df_data_dict[self.FILE_WISE_CALCULATION][0]
        
        # Grouping by 'driver' and summing 'total count'
        df_driverwise_count = df_filewise_count.groupby(self.filewise_count_header[1], as_index=False).agg({self.filewise_count_header[2]: 'sum'})

        # Removing index column
        df_driverwise_count = df_driverwise_count.reset_index(drop=True)

        # Adding zero count drivers / cfgstat
        drivers = [key.lower() for key in self.df_data_dict.keys()]
        for driver in self.df_data_dict:
            driver = driver.lower()
            if driver != self.FILE_WISE_CALCULATION.casefold() and driver not in drivers:
                df_driverwise_count.loc[len(df_driverwise_count.index)] = [driver, 0]

        # Convert 'Driver' column to categorical with specified order
        df_driverwise_count[self.filewise_count_header[1]] = pd.Categorical(df_driverwise_count[self.filewise_count_header[1]], categories=drivers, ordered=True)

        # Sort the DataFrame based on the categorical 'Driver' column
        df_driverwise_count = df_driverwise_count.sort_values(self.filewise_count_header[1]).reset_index(drop=True)

        # Set Column Headers
        df_driverwise_count.columns = self.driverwise_count_header

        self.df_data_dict[self.DRIVER_WISE_COUNT] = [df_driverwise_count]

    def _generate_filewise_calculation_sheet_data(self):
        """
        This method processes the sheetwise compiler driver / cfgstat data and generate a filewise count
        that is added to the dictionary of dataframes which is an attribute of the class that can then be
        used to generate the compiler warnings report.
        """
        # File wise driver count
        file_count_data = dict({
            header_col_name: [] for header_col_name in self.filewise_count_header
        })

        for driver in self.df_data_dict:
            driver_name = driver.lower()
            self.df_data_dict[driver] = [pd.concat(self.df_data_dict[driver], ignore_index=True)]
            # Extract filenames from filepath
            file_info = self.df_data_dict[driver][0][self.warnings_sheet_header[0]].apply(lambda x: os.path.basename(x)).to_list()
            # Count instances of each file name
            file_count = Counter(file_info)

            if file_count:
                filenames, filecounts = zip(*file_count.items())
                file_count_data[self.filewise_count_header[0]].extend(filenames)
                file_count_data[self.filewise_count_header[1]].extend([driver_name] * len(filenames))
                file_count_data[self.filewise_count_header[2]].extend(filecounts)

        self.df_data_dict[self.FILE_WISE_CALCULATION] = [pd.DataFrame(file_count_data, index=None)]

    def _generate_warnings_sheet_data(self, is_driver) -> bool:
        """
        This method iterates through the driver group dictionary of log files and generates
        sheet wise Warnings data for each driver and cfgstat. 
        
        Based on the is_driver flag, the logic varies between cfgstat and driver.

        Args:
            is_driver (bool): a flag to differentiate processing logic between driver and cfgstat

        Returns:
            bool: a flag for sheet warning generation status.
        """
        warnings_sheet_status = False
        cfgstat_filter_pattern = self.cfgstat_filter_pattern
        is_driver_list = []
        cfgstat_filter_pattern_list =[]
        driver_list = []
        driver_filter_pattern_list = []
        log_file_list = []

        for driver in self.driver_groups:
            driver_name = driver.lower()
            driver_filter_pattern = re.compile(
                self.driver_filter_pattern_prefix
                + re.escape(driver_name) 
                + self.driver_filter_pattern_suffix
            )

            log_files = self.driver_groups[driver]
            log_file_list.extend(log_files)
            is_driver_list.extend([is_driver]*len(log_files))
            cfgstat_filter_pattern_list.extend([cfgstat_filter_pattern]*len(log_files))
            driver_list.extend([driver]*len(log_files))
            driver_filter_pattern_list.extend([driver_filter_pattern]*len(log_files))


        # Create an iterable of arguments using zip
        arguments = zip(is_driver_list, cfgstat_filter_pattern_list, driver_list, driver_filter_pattern_list, log_file_list)
        # Parallel processing
        with Pool(processes=math.ceil(os.cpu_count()*0.4)) as pool:
            results = []
            results = pool.starmap(self.process_log_file, arguments)
            
            final_result = {}
            for result in results:
                for key, value in result.items():
                    if key in final_result:
                        final_result[key].extend(value)
                    else:
                        final_result[key] = value
        
        self.df_data_dict.update(final_result)
        warnings_sheet_status = True

        return warnings_sheet_status

    def process_log_file(self, is_driver: bool, cfgstat_filter_pattern: Any, 
                         driver: str, driver_filter_pattern: Any,
                         log_file: str)-> dict:
        """
        This file takes driver type, filter patterns, driver name and log file path as arguments
        and processes and returns the relevant compiler warnings for the driver from the log file

        Args:
            is_driver (bool): flag for is_driver or for cfgstat
            cfgstat_filter_pattern (Any): Regex pattern for filtering cfgstat warnings
            driver (str): name of the driver
            driver_filter_pattern (Any): Regex pattern for filtering driver warnings
            log_file (str): path of the log file

        Returns:
            dict: processed warnings data for particular driver or cfgstat from specified log file
        """
        shared_dict = dict()
        log_file_path = os.path.join(self.log_directory, log_file)
        df_file_data = pd.DataFrame(columns=self.warnings_sheet_header)
        with open(log_file_path, mode="r+", encoding="utf-8") as l_file:
            file_data = l_file.readlines()
            block_open = False
            note = ""
            remarks = ""
            warning = ""
            line_number = ""
            file_path = ""
            for line in file_data:
                match = re.match(self.compiler_warning_pattern_start, line)
                sheet_filter_pattern = driver_filter_pattern if is_driver else cfgstat_filter_pattern
                if (
                            match
                            and re.match(sheet_filter_pattern, match.group(1))
                            and block_open is False
                        ):
                    warning = ""
                    note = ""
                    file_path = match.group(1)
                    file_path = re.sub(self.date_time_pattern, "", str(file_path))
                    line_number = match.group(2)
                    block_open = True
                    if match.group(4) == self.warnings_sheet_header[2].casefold():
                        warning = match.group(5)
                    elif match.group(4) == self.warnings_sheet_header[3].casefold():
                        note = match.group(5)
                elif (
                            re.match(self.compiler_warning_pattern_end, line)
                            and match
                            and block_open is True
                        ):
                    block_open = False
                    df_row = pd.DataFrame([
                                {
                                    self.warnings_sheet_header[0]: str(file_path).strip(),
                                    self.warnings_sheet_header[1]: str(line_number).strip(),
                                    self.warnings_sheet_header[2]: str(warning).strip(),
                                    self.warnings_sheet_header[3]: str(note).strip(),
                                    self.warnings_sheet_header[4]: remarks,
                                }
                            ])
                            # Add next row of warning
                    df_file_data = pd.concat([
                                df_file_data,
                                df_row
                            ],
                            ignore_index=True
                            )
                    if match and re.match(sheet_filter_pattern, match.group(1)) and block_open is False:
                        warning = ""
                        note = ""
                        file_path = match.group(1)
                        file_path = re.sub(self.date_time_pattern, "", str(file_path))
                        line_number = match.group(2)
                        block_open = True
                        if match.group(4) == self.warnings_sheet_header[2].casefold():
                            warning = match.group(5)
                        elif match.group(4) == self.warnings_sheet_header[3].casefold():
                            note = match.group(5)
                elif block_open is True:
                    if warning:
                        warning = warning + "\n" + line
                    elif note:
                        note = note + "\n" + line
                    # process dataframe to merge warning and note
            for index, row in df_file_data.iterrows():
                if pd.isnull(row[self.warnings_sheet_header[3]]) or row[self.warnings_sheet_header[3]] == '':
                    if index >= 0 and index < len(df_file_data)-1 and row[self.warnings_sheet_header[0]] == df_file_data.at[index + 1, self.warnings_sheet_header[0]]:
                        row[self.warnings_sheet_header[3]] = df_file_data.at[index + 1, self.warnings_sheet_header[3]]
                        df_file_data.at[index + 1, self.warnings_sheet_header[3]] = ''  # Clear the merged row
            
            # drop rows with no Warning
            blank_rows = df_file_data[(df_file_data[self.warnings_sheet_header[2]].str.strip() == '')]
            df_file_data = df_file_data.drop(blank_rows.index)
            # clean data in Warnings and Note stop with line ending with ";"
            df_file_data[self.warnings_sheet_header[2]] = df_file_data[self.warnings_sheet_header[2]].apply(lambda x: str(x).split(";")[0]+";" if str(x).strip() else x)
            df_file_data[self.warnings_sheet_header[3]] = df_file_data[self.warnings_sheet_header[3]].apply(lambda x: str(x).split(";")[0]+";" if str(x).strip() else x)

            # Drop duplicate data
            df_file_data.drop_duplicates(inplace=True)

            # Collect all data for formatting and report generation
            if is_driver:
               shared_dict[driver] = shared_dict[driver].append(df_file_data) if driver in shared_dict else [df_file_data] 
            else:
                if self.cfgstat_name in shared_dict:
                    shared_dict[self.cfgstat_name].append(df_file_data)
                else:
                    shared_dict[self.cfgstat_name] = [df_file_data]
        return shared_dict

    def process_compiler_report(self, log_directory, report_path, props: Any) -> OrderedDict:
        """
        This methods accepts the path to the compiler log diretcory, destination path for the report
        and properties object 

        Args:
            log_directory (str): path to the compiler log directory
            report_path (str): path for the report
            props (Any): a python object of properties from the yaml file

        Returns:
            OrderedDict: report data
        """
        self.DRIVER_WISE_COUNT = props.compiler_warning_report_props.constants.DRIVER_WISE_COUNT
        self.FILE_WISE_CALCULATION = props.compiler_warning_report_props.constants.FILE_WISE_CALCULATION
        self.log_directory = log_directory
        self.report_data = OrderedDict()

        self.filewise_count_header = props.compiler_warning_report_props.filewise_count_header
        self.driverwise_count_header = props.compiler_warning_report_props.driverwise_count_header

        # warnings_sheet_header = ["File_Path", "Line Number", "Warning", "Note", "Remarks"]
        self.warnings_sheet_header = props.compiler_warning_report_props.warnings_sheet_header
        # Define the regular expression pattern
        self.compiler_warning_pattern_start = props.compiler_warning_report_props.compiler_warning_pattern_start
        self.compiler_warning_pattern_end = props.compiler_warning_report_props.compiler_warning_pattern_end
        self.driver_filter_pattern_prefix = props.compiler_warning_report_props.driver_filter_pattern_prefix
        self.driver_filter_pattern_suffix = props.compiler_warning_report_props.driver_filter_pattern_suffix
        self.cfgstat_filter_pattern = props.compiler_warning_report_props.cfgstat_filter_pattern

        # naming cfg sheet from cfgstat_filter_pattern obtained from config properties yaml 
        self.cfgstat_name = self.cfgstat_filter_pattern.split("(")[1].split(")")[0].upper()

        # Define a regex pattern to match the desired format
        self.compiler_file_pattern = props.compiler_warning_report_props.compiler_file_pattern

        self.date_time_pattern = props.compiler_warning_report_props.date_time_pattern

        # Find log files using os.walk
        self.log_files = []
        self.driver_groups = {}
        self.df_data_dict = dict()
        for root, dirs, files in os.walk(log_directory):
            for file in files:
                match = re.match(self.compiler_file_pattern, file)
                if match:
                    self.log_files.append(file)
                    driver_name = match.group(1)
                    self.driver_groups.setdefault(driver_name, []).append(file)


                
        if self.log_files:
            # will generate HAL_CFGSTAT warning sheet
            self._generate_warnings_sheet_data(is_driver=False)
            # will generate driver wise warning sheets
            self._generate_warnings_sheet_data(is_driver=True)
            # will generate filewise count sheet
            self._generate_filewise_calculation_sheet_data()
            # will generate driverwise count sheet
            self._generate_driverwise_count_sheet_data()

            # # Generate the report
            self.report_data = reports.generate_excel_report_data(report_path, self.df_data_dict)
        # print(type(self.report_data))
        return self.report_data

    


                    
