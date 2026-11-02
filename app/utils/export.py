import csv
import io

from flask import Response


def export_attendance_csv(records):
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Employee ID",
        "Date",
        "Status",
        "Check In",
        "Check Out"
    ])

    for record in records:
        writer.writerow([
            record["employee_id"],
            record["date"],
            record["status"],
            record["check_in"],
            record["check_out"]
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=attendance.csv"
        }
    )
