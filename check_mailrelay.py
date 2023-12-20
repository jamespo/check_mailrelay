#!/usr/bin/env python3

# check_mailrelay - checks if message with certain subject on IMAP server
# (c) James Powell - jamespo [at] gmail [dot] com 2023
# Create ~/.config/.check_mailrelay.conf with 1 or more sections as below:
# (at least one alias must be called default)
#
# [serveralias]
# user=james
# password=2347923rbkaa
# server=yourimapserver.com
# folder=INBOX

from email.header import make_header, decode_header
import os
import re
import socket
import sys
import imaplib
import email
from email.utils import parseaddr
from optparse import OptionParser
import configparser
import shlex

DEBUG = os.getenv('CMRDEBUG')

def getopts():
    '''returns OptionParser.options for CL switches'''
    parser = OptionParser()
    parser.add_option("-a", help="account (default: default)",
                      dest="account", default="default")
    parser.add_option("-t", help="subject tag", dest="subj_tag",
                      default="JP-RELAY-TEST")
    options, _ = parser.parse_args()
    return options


def readconf(account, confpath=os.path.expanduser('~/.config/.check_mailrelay.conf')):
    '''returns ConfigParser object with account details'''
    config = configparser.ConfigParser()
    config.read(confpath)
    account_conf = dict(config.items(account))
    if 'folder' not in account_conf:
        account_conf['folder'] = 'INBOX'
    return account_conf


def debugpr(msg):
    '''print debug msgs'''
    if DEBUG:
        print(msg)


class IMAPSubjFind():
    '''searches for matching emails in IMAP account'''
    def __init__(self, user, pw, server, folder, subj_tag):
        self.user = user
        self.pw = pw
        self.server = server
        self.folder = folder
        self.subj_tag = subj_tag
        self.mailconn = None

    def connect(self):
        '''connect to the mailserver'''
        debugpr('connect (timeout: %s)' % socket.getdefaulttimeout())
        self.mailconn = imaplib.IMAP4_SSL(self.server)
        if 'AUTH=CRAM-MD5' in self.mailconn.capabilities:
            # use cram_md5 for auth
            status, _ = self.mailconn.login_cram_md5(self.user, self.pw)
        else:
            status, _ = self.mailconn.login(self.user, self.pw)
        assert status == 'OK'
        # self.mailconn.list()  # TODO: needed?

    def checknew(self):
        '''connect & search for mails'''
        try:
            self.connect()
            self.matchmail()
        except:  # TODO: make exception checking more specific
            pass  # handled below
        # close connection
        if self.mailconn.state != 'NONAUTH':
            self.mailconn.close()
        self.mailconn.logout()

    def matchmail(self):
        '''find mails matching the tag'''
        allretcode, allmessages_str = self.mailconn.select(self.folder, readonly=True)
        msgrc, match_msgids = self.mailconn.search(None, 'SUBJECT', '"%s"' % self.subj_tag)
        if (msgrc, allretcode) == ('OK', 'OK'):
            allmessages_num = int(allmessages_str[0])
            unread = match_msgids[0].decode(encoding="utf-8", errors='replace')
            if unread == '':
                # no new mails found
                debugpr('No new mails found')
            else:
                # new mails found
                debugpr('New mails found: %s' % unread)
                # TODO: loop round mails & validate more, delete if necessary
                match_msgids_arr = unread.split(' ')
        else:
            raise imaplib.IMAP4.error()

    # # TODO: required?
    # @staticmethod
    # def clean_subject(subj):
    #     '''decode subject if in unicode format'''
    #     subj = IMAPSubjFind.unicode_to_str(subj)
    #     # remove newlines
    #     subj = subj.replace('\r', '')
    #     subj = subj.replace('\n', '')
    #     return subj

    # @staticmethod
    # def unicode_to_str(header):
    #     '''convert unicode header to plain str if required'''
    #     return str(make_header(decode_header(header)))


def main():
    '''load options, start check threads and display results'''
    cmd_options = getopts()
    config = readconf(cmd_options.account)
    socket.setdefaulttimeout(10)  # IMAP server connections
    imapfind = IMAPSubjFind(config['user'], config['password'], config['server'],
                            config['folder'], cmd_options.subj_tag)
    imapfind.checknew()


if __name__ == '__main__':
    main()
