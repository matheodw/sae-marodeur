"""Client interne utilisé pour mettre à jour les données du planning.
Peut interroger un service externe pour synchroniser les salles/présences.
"""
class UPPlanningClient:
    def fetch_ical(self, url):
        print("Téléchargement iCal depuis:", url)
        return "BEGIN:VCALENDAR..."