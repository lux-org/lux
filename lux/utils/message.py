class Message:
    def __init__(self):
        self.content = []
    def append(self,item):
        self.content.append(item)
    def to_html(self):
        if (len(self.content)==0):
            return ""
        else:
            html = "<ul>"
            for item in self.content:
                html+=f"<li>{item}</li>"
            html += "</ul>"
            return html