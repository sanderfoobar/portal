#!/usr/bin/env python
# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import asyncore
import email
import os.path
import smtpd
import sys

from portal import submit_file, emit_options

class SmtpSubmit(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data):
        options = {
            "procmemdump": "1",
            "json.calls": "0",
        }

        custom = {
            "email": mailfrom,
            "reports": ["txt", "html", "pdf"],
        }

        for msg in email.message_from_string(data).walk():
            if msg.is_multipart():
                continue

            data = {
                "options": emit_options(options),
            }

            # TODO Extract an appropriate package based on the content-type.
            # content_type = msg.get_content_type()

            payload = msg.get_payload(decode=True)
            filename = os.path.basename(msg.get_filename())

            uniqid = submit_file(payload, filename, data, custom)
            uniqid

        # TODO Email back with the future URLs.

if __name__ == "__main__":
    if len(sys.argv) == 1:
        addr = "127.0.0.1"
        port = 25
    elif len(sys.argv) == 2:
        addr = sys.argv[1]
        port = 25
    elif len(sys.argv) == 3:
        addr = sys.argv[1]
        port = int(sys.argv[2])
    else:
        sys.exit("Unknown parameter count")

    SmtpSubmit((addr, port), None)
    asyncore.loop()
