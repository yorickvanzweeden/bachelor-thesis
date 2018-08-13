import xml.etree.ElementTree as ET

# Get XML file
tree = ET.parse('/PATH/TO/APPLICATION/MANIFEST/src/main/AndroidManifest.xml')
root = tree.getroot()

# Create reversed tree
parent_map = {c:p for p in tree.iter() for c in p}

# Tag obtaining name attribute
name_tag = '{http://schemas.android.com/apk/res/android}name'

# Print a list of components from the Manifest file
def getComponent(componentType):
  print(f"##{componentType}##")
  for component in root.iter(componentType):
    print(component.attrib[name_tag])

# Print a list of intent filters from the Manifest file
def getIntentFilters():
  for component in root.iter('intent-filter'):
    f = component.find("action").attrib[name_tag]
    c = parent_map[component].attrib[name_tag]
    print(f'{f} -> {c}')

getIntentFilters()

getComponent("activity")
getComponent("service")
getComponent("receiver")
getComponent("provider")