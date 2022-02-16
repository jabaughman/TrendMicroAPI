"""
Usage: 
	# subscribe metohd
	python subscribe.py
	# unsubscribe:
	python subscribe.py --unsubscribe
"""

import argparse

from logfeeder import LogFeeder


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Logfeeder subscribe script.')
    parser.add_argument('--unsubscribe', help='unsubscribe', nargs='?', const=True)
    args = parser.parse_args()
    if args.unsubscribe:
        print "unsubscribe start:"
        LogFeeder().unsubscribe()
    else:
        print "subscribe start:"
        LogFeeder().subscribe()
