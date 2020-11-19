#  Copyright 2019-2020 The Lux Authors.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


class Message:
    def __init__(self):
        self.messages = []

    def add_unique(self, item, priority=-1):
        msg = {"text": item, "priority": priority}
        if msg not in self.messages:
            self.messages.append(msg)

    def add(self, item, priority=-1):
        self.messages.append({"text": item, "priority": priority})

    def to_html(self):
        if len(self.messages) == 0:
            return ""
        else:
            sorted_msgs = sorted(self.messages, key=lambda i: i["priority"], reverse=True)
            html = "<ul>"
            for msg in sorted_msgs:
                msgTxt = msg["text"]
                html += f"<li>{msgTxt}</li>"
            html += "</ul>"
            return html
