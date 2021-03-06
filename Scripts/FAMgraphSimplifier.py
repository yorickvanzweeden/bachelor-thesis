from graphviz import Digraph

# dot = Digraph(comment='K-9 Mail app')
# dot.node('W', 'Widgets')
# dot.node('L', 'Message list')
# dot.node('C', 'Compose mails')
# dot.node('A', 'Accounts')
# dot.node('S', 'Setup')
# dot.node('F', 'Fetch services')
# dot.node('R', 'RemoteControl')
# dot.node('R', 'RemoteControl')
# dot.node('M', 'Load messages')
# dot.node('U', 'Upgrade database')
# dot.node('G', 'Settings')

# dot.edges(['WL', 'WC', 'WA'])
# dot.edges(['LU', 'LC', 'LA', 'LF', 'LG'])
# dot.edges(['CU', 'CM', 'CA', 'CF'])
# dot.edges(['AU', 'AM', 'AC', 'AF', 'AG','AS'])
# dot.edges(['SA'])
# dot.edges(['RF'])
# # dot.edges(['UM', 'UC', 'UW', 'UA'])
# dot.edges(['GL', 'GF'])
# dot.edges(['FM'])


dot = Digraph(comment='OmniNotes App')
dot.node('W', 'Widgets')
dot.node('R', 'Reminders')
dot.node('E', 'Extensions')
dot.node('S', 'Storage')
dot.node('G', 'Settings')
dot.node('N', 'Notes')
dot.edges(['WN', 'WS'])
dot.edges(['NS', 'NE', 'NG', 'NR'])
dot.edges(['RS', 'RE'])
dot.edges(['GS'])

dot.render('test-output/FAML.gv', view=True)