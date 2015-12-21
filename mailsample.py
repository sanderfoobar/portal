#!/usr/bin/env python
# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import argparse
import email.mime.multipart
import email.mime
import os.path
import smtplib
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("addr", help="IP address of SMTP server")
    parser.add_argument("email", help="Email address")
    parser.add_argument("sample", help="Sample filename")
    args = parser.parse_args()

    if not os.path.exists(args.sample):
        sys.exit("Invalid sample filename given")

    multi = email.mime.multipart.MIMEMultipart()
    multi["Subject"] = "Sample submission"
    multi["To"] = "cuckoo@analysis"
    multi["From"] = args.email

    msg = email.mime.base.MIMEBase("application", "octet-stream")
    msg.set_payload(open(args.sample, "rb").read())
    msg.add_header("Content-Disposition", "attachment",
                   filename=os.path.basename(args.sample))
    multi.attach(msg)

    s = smtplib.SMTP(args.addr)
    s.sendmail(args.email, ["cuckoo@analysis"], multi.as_string())
    s.quit()
