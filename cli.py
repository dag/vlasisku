from optparse import OptionParser


parser = OptionParser()

parser.add_option('-p', '--port', action='store', type='int', default=8080,
                  help='Listen on this port')
parser.add_option('-d', '--debug', action='store_true',
                  help='Enable debugging')
parser.add_option('-r', '--reloader', action='store_true',
                  help='Reload modules when they are modified')

options, args = parser.parse_args()
