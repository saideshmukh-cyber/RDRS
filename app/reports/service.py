from __future__ import annotations

import csv, json
from pathlib import Path
from jinja2 import Template
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class ReportService:
    def __init__(self, settings, repository):
        self.settings=settings; self.repository=repository; self.settings.reports_dir.mkdir(parents=True, exist_ok=True)

    def data(self, incident_id):
        i=self.repository.get_incident(incident_id)
        if not i: return None
        return {"id":i.id,"created_at":i.created_at.isoformat(),"level":i.level,"score":i.score,"summary":i.summary,
                "affected_files":json.loads(i.affected_files_json),"signals":json.loads(i.signals_json),
                "suspect_process":json.loads(i.suspect_process_json),"quarantine_dir":i.quarantine_dir}

    def json_report(self, incident_id):
        data=self.data(incident_id)
        if not data: return None
        path=self.settings.reports_dir/f"incident_{incident_id}.json"; path.write_text(json.dumps(data, indent=2), encoding="utf-8"); return path

    def csv_report(self, incident_id):
        data=self.data(incident_id)
        if not data: return None
        path=self.settings.reports_dir/f"incident_{incident_id}.csv"
        with path.open("w", newline="", encoding="utf-8") as fh:
            w=csv.writer(fh); w.writerow(["incident_id","timestamp","level","score","signal","file"])
            for f in data["affected_files"] or [""]:
                for s in data["signals"] or [""]:
                    w.writerow([data["id"],data["created_at"],data["level"],data["score"],s,f])
        return path

    def html_report(self, incident_id):
        data=self.data(incident_id)
        if not data: return None
        template=Template("""<!doctype html><html><head><meta charset='utf-8'><title>RDRS Incident {{ id }}</title></head><body><h1>RDRS Incident #{{ id }}</h1><p><b>Level:</b> {{ level }} <b>Score:</b> {{ score }}</p><p>{{ summary }}</p><h2>Signals</h2><ul>{% for s in signals %}<li>{{ s }}</li>{% endfor %}</ul><h2>Affected files</h2><ul>{% for f in affected_files %}<li>{{ f }}</li>{% endfor %}</ul></body></html>""")
        path=self.settings.reports_dir/f"incident_{incident_id}.html"; path.write_text(template.render(**data), encoding="utf-8"); return path

    def pdf_report(self, incident_id):
        data=self.data(incident_id)
        if not data: return None
        path=self.settings.reports_dir/f"incident_{incident_id}.pdf"; c=canvas.Canvas(str(path), pagesize=letter); y=750
        for line in [f"RDRS Incident #{data['id']}",f"Level: {data['level']}   Score: {data['score']}",data['summary'],"Signals: "+", ".join(data['signals'])]:
            c.drawString(50,y,line[:110]); y-=20
        c.drawString(50,y,"Affected files:"); y-=20
        for f in data['affected_files'][:35]:
            c.drawString(60,y,f[:100]); y-=15
            if y<60: c.showPage(); y=750
        c.save(); return path
