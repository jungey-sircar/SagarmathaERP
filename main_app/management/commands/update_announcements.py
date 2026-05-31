from django.core.management.base import BaseCommand

from main_app.models import Announcement, Staff


class Command(BaseCommand):
    help = "One-off: inspect and update existing Announcement rows. Dry-run by default; use --commit to apply."

    def add_arguments(self, parser):
        parser.add_argument(
            "--match",
            default="",
            help="Case-insensitive substring to match announcement titles. Ignored with --all.",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Match all announcements (dangerous).",
        )
        parser.add_argument(
            "--title",
            default=None,
            help="Optional replacement title.",
        )
        parser.add_argument(
            "--body",
            default=None,
            help="Optional replacement body.",
        )
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Apply updates. Without this flag the command runs in dry-run mode.",
        )
        parser.add_argument(
            "--target-emails",
            default="",
            help="Comma-separated list of staff admin emails to target this announcement to.",
        )

    def handle(self, *args, **options):
        match = options.get("match")
        use_all = options.get("all")
        new_title = options.get("title")
        new_body = options.get("body")
        commit = options.get("commit")
        target_emails_raw = options.get("target_emails") or ""
        target_emails = [e.strip() for e in target_emails_raw.split(",") if e.strip()]

        if use_all:
            qs = Announcement.objects.all()
        else:
            qs = Announcement.objects.filter(title__icontains=match)

        count = qs.count()
        if count == 0:
            self.stdout.write(self.style.WARNING("No matching announcements found."))
            return

        self.stdout.write(self.style.NOTICE(f"Found {count} announcement(s):"))
        for a in qs:
            self.stdout.write(f" - id={a.id} title={a.title!r}")

        self.stdout.write("")
        self.stdout.write("Proposed replacement:")
        self.stdout.write(f" Title -> {new_title if new_title is not None else '[unchanged]'}")
        self.stdout.write(f" Body  -> {new_body if new_body is not None else '[unchanged]'}")
        self.stdout.write("")

        if not commit:
            self.stdout.write(
                self.style.WARNING(
                    "Dry-run: no changes applied. Rerun with --commit to apply."
                )
            )
            return

        updated = 0
        for a in qs:
            try:
                if new_title is not None:
                    a.title = new_title
                if new_body is not None:
                    a.body = new_body
                a.save()
                # If target emails were provided, map them to Staff objects and set targets
                if target_emails:
                    staff_qs = Staff.objects.filter(admin__email__in=target_emails)
                    a.targets.set(staff_qs)
                updated += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to update id={a.id}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Updated {updated} announcement(s)."))
