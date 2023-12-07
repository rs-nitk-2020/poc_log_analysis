import json
import os
from django.shortcuts import render
from log_analysis_api import app_dashboard
from django.http import HttpResponse, JsonResponse

# Create your views here.
def home(request):
    basic_gui_data = None
    log_dashboard = app_dashboard.LogAnalysisApi()
    basic_gui_data = log_dashboard.load_gui_basic_data()
    return render(request, 'home.html', basic_gui_data)

def validation_rules(request):
    log_dashboard = app_dashboard.LogAnalysisApi()
    basic_gui_data = log_dashboard.load_gui_basic_data()
    return JsonResponse(basic_gui_data)


def process_log_warnings(request):
    response_data = JsonResponse({})
    files_data = None
    log_dashboard = app_dashboard.LogAnalysisApi()
    if request.method == 'POST' and request.POST['warning_type'] == 'Compiler_Warnings': 
        files_data = request.FILES
        report_data, report_name = log_dashboard.process_compiler_warnings(files_data)

        response_data = dict({
            'report_name': report_name,
            'report_data': report_data
        })
    elif request.method == 'POST' and request.POST['warning_type'] == 'MISRA_Warnings':
        files_data = request.FILES
        # print(files_data)
        report_data, report_name = log_dashboard.process_misra_warnings(files_data)
        response_data = dict({
            'report_name': report_name,
            'report_data': report_data
        })

    return JsonResponse(response_data, content_type='application/json', charset='utf-8')

def display_report(request):
    return render(request, 'report.html')

def download_report(request):
    # Decode the bytes object from the request body into a string and parse it as JSON
    request_data = json.loads(request.body.decode('utf-8'))

    # Assuming the request_data contains 'report_name' key
    report_name = request_data.get('report_name')
    log_dashboard = app_dashboard.LogAnalysisApi()
    report_path = log_dashboard.download_report(report_name)
    try:
        if os.path.exists(report_path):
            with open(report_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename="report.xlsx"'
                return response
        else:
            return HttpResponse("File not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error occurred while handling the file: {e}", status=500)
