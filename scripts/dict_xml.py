import dicttoxml

example_dict = {
  "Team": "myteam",
  "Opp": "myopp",
  "Game": "mygame",
  "Style": "Opponent",
  "Win%": "mywin",
  "Total": "mytotal",
  "Stat": "mystat",
  "Formatted": "myforatted"
}

xml = dicttoxml.dicttoxml(example_dict)

print "=========== result ==========="
print xml


with open('result.xml', 'w') as f:
  f.write(xml)
  f.close()

