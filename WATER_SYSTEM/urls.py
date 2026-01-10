"""
URL configuration for WATER_SYSTEM project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from auths.views import login_view, logout_view
from manager.views import manager_dashboard, staff_list, manager_customer_list, manager_street_list, manager_sales_list, manager_expenditure_list, manager_weekly_report, manager_reports, manager_water_production, manager_customer_debts, manager_get_debt_payments, manager_reports_hub, manager_mitaa_report, manager_wateja_report, manager_wateja_excel, manager_water_production_report, manager_mapato_report, manager_mapato_excel
from staff.views import staff_dashboard, order_list, get_customers_by_street, sales_list, expenditure_list, weekly_report, water_production_list, customer_debts_list, get_debt_payments
from customers.views import customer_list, street_list
from unit_configs.views import unit_config_list, toggle_unit_config

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('manager/dashboard/', manager_dashboard, name='manager_dashboard'),
    path('manager/staff/', staff_list, name='staff_list'),
    path('manager/customers/', manager_customer_list, name='manager_customer_list'),
    path('manager/streets/', manager_street_list, name='manager_street_list'),
    path('manager/sales/', manager_sales_list, name='manager_sales_list'),
    path('manager/expenditure/', manager_expenditure_list, name='manager_expenditure_list'),
    path('manager/weekly-report/', manager_weekly_report, name='manager_weekly_report'),
    path('manager/reports/', manager_reports, name='manager_reports'),
    path('manager/water-production/', manager_water_production, name='manager_water_production'),
    path('manager/customer-debts/', manager_customer_debts, name='manager_customer_debts'),
    path('manager/api/debt-payments/<int:debt_id>/', manager_get_debt_payments, name='manager_get_debt_payments'),
    path('manager/reports-hub/', manager_reports_hub, name='manager_reports_hub'),
    path('manager/mitaa-report/', manager_mitaa_report, name='manager_mitaa_report'),
    path('manager/wateja-report/', manager_wateja_report, name='manager_wateja_report'),
    path('manager/wateja-excel/', manager_wateja_excel, name='manager_wateja_excel'),
    path('manager/water-production-report/', manager_water_production_report, name='manager_water_production_report'),
    path('manager/mapato-report/', manager_mapato_report, name='manager_mapato_report'),
    path('manager/mapato-excel/', manager_mapato_excel, name='manager_mapato_excel'),
    path('staff/dashboard/', staff_dashboard, name='staff_dashboard'),
    path('staff/orders/', order_list, name='order_list'),
    path('staff/sales/', sales_list, name='sales_list'),
    path('staff/expenditure/', expenditure_list, name='expenditure_list'),
    path('staff/weekly-report/', weekly_report, name='weekly_report'),
    path('staff/water-production/', water_production_list, name='water_production_list'),
    path('staff/customer-debts/', customer_debts_list, name='customer_debts_list'),
    path('api/debt-payments/<int:debt_id>/', get_debt_payments, name='get_debt_payments'),
    path('api/customers-by-street/', get_customers_by_street, name='get_customers_by_street'),
    path('customers/', customer_list, name='customer_list'),
    path('streets/', street_list, name='street_list'),
    path('unit-configs/', unit_config_list, name='unit_config_list'),
    path('unit-configs/toggle/<int:config_id>/', toggle_unit_config, name='toggle_unit_config'),
]
