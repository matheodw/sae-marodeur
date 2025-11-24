# up_planning_client.py
class UPPlanningClient:
    def fetch_ical(self, url):
        print("Téléchargement iCal depuis:", url)
        return "BEGIN:VCALENDAR..."