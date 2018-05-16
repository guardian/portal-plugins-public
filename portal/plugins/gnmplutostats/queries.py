from django.db.models import Q
from models import ProjectScanReceipt
from datetime import datetime, timedelta

IN_PRODUCTION_NEED_SCAN = ProjectScanReceipt.objects.filter(project_status="In Production",last_scan__lt=datetime.now()-timedelta(days=1))
NEW_NEED_SCAN = ProjectScanReceipt.objects.filter(project_status="New", last_scan__lt=datetime.now()-timedelta(days=1))
OTHER_NEED_SCAN = ProjectScanReceipt.objects.filter(~Q(project_status="New") & ~Q(project_status="In Production"),last_scan__lt=datetime.now()-timedelta(days=5))
IN_PRODUCTION_DID_SCAN = ProjectScanReceipt.objects.filter(project_status="In Production",last_scan__gte=datetime.now()-timedelta(days=1))
NEW_DID_SCAN = ProjectScanReceipt.objects.filter(project_status="New", last_scan__gte=datetime.now()-timedelta(days=1))
OTHER_DID_SCAN = ProjectScanReceipt.objects.filter(~Q(project_status="New") & ~Q(project_status="In Production"),last_scan__gte=datetime.now()-timedelta(days=5))
