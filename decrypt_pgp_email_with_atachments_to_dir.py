#!/usr/bin/env python3
"""Unpack a PGP message attachments into a directory of files."""

import os, email, mimetypes, gnupg
# import getpass
from email.policy import default
from argparse import ArgumentParser

# psf = getpass.getpass("Please enter your PGP passphrase: ")

def main():
    parser = ArgumentParser(description="""\
                        Decrypt a PGP email message and unpack its attachment into a directory of files.
                        \nAs a prerequisite, GPG package (gnupg) must be configured on the machine.
                        """)
    parser.add_argument('-g', '--gpghome', required=True,
                        help="""The gpghome directory. E.g., /home/testgpguser/.gpghome
                        """)
    parser.add_argument('-d', '--attdir', required=True,
                        help="""Unpack the MIME message into the named
                        directory, which will be created if it doesn't already
                        exist.""")
    parser.add_argument('-f', '--msgfile', required=True,
                        help="""The path with the .pgp file which will be decrypted.
                        """)
    args = parser.parse_args()
    gpg = gnupg.GPG(gnupghome=args.gpghome)

    with open(args.msgfile, 'rb') as f:
        # gpg.decrypt_file(f, passphrase=psf, output='file.txt')
        gpg.decrypt_file(f, output='file.txt')

    with open('file.txt', 'rb') as fb:
        msg = email.message_from_binary_file(fb, policy=default)

    try:
        os.mkdir(args.attdir)
    except FileExistsError:
        pass

    counter = 1
    for part in msg.walk():
        # multipart/* are just containers
        if part.get_content_maintype() == 'multipart':
            continue
        # Applications should really sanitize the given filename so that an
        # email message can't be used to overwrite important files
        filename = part.get_filename()
        if not filename:
            ext = mimetypes.guess_extension(part.get_content_type())
            if not ext:
                # Use a generic bag-of-bits extension
                ext = '.bin'
            filename = f'part-{counter:03d}{ext}'
        counter += 1
        with open(os.path.join(args.attdir, filename), 'wb') as fp:
            fp.write(part.get_payload(decode=True))
    print("\nDone! See {}:\n".format(args.attdir))
    os.system("ls -lt " + args.attdir)
    os.remove('file.txt')

if __name__ == '__main__':
    main()


# python decrypt_pgp_email_with_atachments_to_dir.py -g /Users/paulrobu/.gnupg -d /tmp/att -f ~/Desktop/Message.pgp 

# https://www.saltycrane.com/blog/2011/10/python-gnupg-gpg-example/
# https://docs.python.org/3/library/email.examples.html
# https://www.digitalocean.com/community/tutorials/how-to-verify-code-and-encrypt-data-with-python-gnupg-and-python-3
# https://www.programcreek.com/python/example/82300/gnupg.GPG
# https://stackoverflow.com/questions/12900542/decrypt-gpg-file-attached-from-email-file-pgp
