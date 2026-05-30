from django.core.management.base import BaseCommand
import json


class Command(BaseCommand):
    help = "Dump pending LeaveReportStaff records (status=0) as JSON"

    def handle(self, *args, **options):
        try:
            from main_app.models import LeaveReportStaff
        except Exception as e:
            self.stderr.write("ERROR importing models: " + str(e))
            return

        qs = LeaveReportStaff.objects.filter(status=0).select_related("staff__admin")
        out = []
        for l in qs:
            staff = getattr(l, "staff", None)
            admin = getattr(staff, "admin", None) if staff else None
            out.append(
                {
                    "id": l.id,
                    "staff_id": getattr(staff, "id", None),
                    "staff_name": (
                        f"{getattr(admin,'first_name','') } {getattr(admin,'last_name','') }".strip()
                        if admin
                        else None
                    ),
                    "role": getattr(staff, "role", None),
                    "role_detail": getattr(staff, "role_detail", None),
                    "date": str(getattr(l, "date", "")),
                    "message": getattr(l, "message", ""),
                }
            )

        self.stdout.write(json.dumps(out, ensure_ascii=False))
