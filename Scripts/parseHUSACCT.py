import csv
import os
import re
import subprocess
from threading import Thread
from enum import Enum

JAVACLASSES = {}
DEPENDENCIES = []
MATCHES = {}

## Support for multithreading with return value
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self):
        Thread.join(self)
        return self._return

## Analyses the source code files and imports the HUSACCT dependencies
class Setup(object):
  def __init__(self, filepath_repository, filepath_dependencies, namespace, matchfilter):
    self.regex_p1 = re.compile('\.[a-z].*\.[A-Z].*$|^[a-z]')
    self.regex_p2 = re.compile('\.[A-Z]')
    self.ignore = [namespace + ".R"]
    self.getJavaClasses(filepath_repository)
    self.getDependencies(filepath_dependencies)
    self.getMatches(matchfilter)

  # Create a dictionary of all Java classes
  # This is used for getting a code block using a HUSACCT dependency
  def getJavaClasses(self, filepath):
    global JAVACLASSES

    for root, dirs, files in os.walk(filepath):
        for file in files:
            if file.endswith(".java"):
              JAVACLASSES[file[:-5]] = os.path.join(root, file)

  # Detect innerclasses in HUSACCT dependencies and adds this relation to JAVACLASSES
  # This only works if it is actually an inner class. Two classes on the same level won't work
  def detectInnerclass(self, s, namespace):
    if namespace in s and not(s in self.ignore):
      s = s[12:]

      # Format string to [(Object.)*Class]
      x1 = self.regex_p1.search(s)

      if x1 != None:
        s = s[x1.span()[0]+1:]
        x2 = self.regex_p2.search(s)
        if x2 != None:
          s = s[x2.span()[0]+1:]

      # Split string
      values = s.split('.')
      path = JAVACLASSES[values[0]]
      for i in reversed(range(1, len(values))):
        JAVACLASSES[values[i]] = path

  # Parse the XML file of HUSACCT dependencies
  def getDependencies(self, filepath):
    with open(filepath, newline='') as csvfile:
      spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
      for row in spamreader:
        self.detectInnerclass(row[0], namespace)
        self.detectInnerclass(row[1], namespace)
        DEPENDENCIES.append(row)

  # Generate an array of matches based on file and linenumber
  def getMatches(self, dependency):
    for i in range(0, len(DEPENDENCIES)):
      row = DEPENDENCIES[i]
      if (dependency in row[1] and row[2] != "Import"):
        t1 = ThreadWithReturnValue(target=self.searchDependencies, args=("Search up ", row[0], i, -1))
        t2 = ThreadWithReturnValue(target=self.searchDependencies, args=("Search down", row[0], i, 1))
        t1.start()
        t2.start()
        results = t1.join()  + t2.join()

        if len(results) == 0:
          continue

        try:
          old = MATCHES[row[0]]
          new = [row[4], row[2], results]
          old.append(new)
          MATCHES[row[0]] = old
        except:
          MATCHES[row[0]] = [[row[4], row[2], results]]

  # Search for matching dependencies on file and linenumber
  def searchDependencies(self, threadName, file, startlinenr, searchDirection):
    i = startlinenr + searchDirection
    results = []
    while i >= 0 and i < len(DEPENDENCIES) - 1 and DEPENDENCIES[i][0] == file:
      if (int(DEPENDENCIES[i][4]) == int(DEPENDENCIES[startlinenr][4])):
        results.append(i)
      i += searchDirection
    return results

## Static class that prints blocks of code
class Lines():
  # Get lines using filename
  def getLines(file, linenr, offset):
    try:
      filepath = JAVACLASSES[file]
    except:
      file = Tools.convertNot(file)
      filepath = JAVACLASSES[file]

    cmd = f'cat {filepath} | head -{linenr + offset} | tail -{1 + 2 * offset}'
    return subprocess.check_output(cmd, shell=True).decode('UTF-8')

  # Get lines by filename and linenumber
  def getLinesByRange(file, start_linenr, end_linenr, offset):
    try:
      filepath = JAVACLASSES[file]
    except:
      file = Tools.convertNot(file)
      filepath = JAVACLASSES[file]

    cmd = f'cat {filepath} | head -{end_linenr + offset} | tail -{end_linenr - start_linenr + 2*offset + 1}'
    return subprocess.check_output(cmd, shell=True).decode('UTF-8')

  # Get lines using dependency
  def printDependencyWithCodeLines(dependency, offset):
    print(Lines.getLines(dependency[0], int(dependency[4]), offset))

  # Get lines of code where matches start in target
  def getCodeLinesStartingFromTarget(component, offset):
    keys = list(MATCHES.keys())
    for key in keys:
      if component != None and Tools.convertNot(key) != component:
        continue
      # Preprocessing of matches
      matches = MATCHES[key]
      # Group by line number distance of max 3
      grouped_matches = Lines.groupLinesByLinenumber(matches, 3)

      for group in grouped_matches:
        # [match1, match2] but sorted by linenr
        linenr_start = group[0][0]
        linenr_end = group[len(group) - 1][0]

        for match in group:
          print(f"{Tools.convertNot(key)}:{match[0]}| {match[1]} \
            --> {[Tools.convertNot(DEPENDENCIES[x][1]) for x in match[2]]}")

        print(Lines.getLinesByRange(key, int(linenr_start), int(linenr_end), offset))

  # Get lines of code where matches end in target
  def getCodeLinesEndingAtTarget(component, offset):
    keys = list(MATCHES.keys())
    for key in keys:
      # Preprocessing of matches
      matches = MATCHES[key]
      # Group by line number distance of max 3
      grouped_matches = Lines.groupLinesByLinenumber(matches, 3)

      for group in grouped_matches:
        # [match1, match2] but sorted by linenr
        linenr_start = group[0][0]
        linenr_end = group[len(group) - 1][0]

        shouldPrint = False

        for match in group:
          if component in [Tools.convertNot(DEPENDENCIES[x][1]) for x in match[2]]:
            shouldPrint = True

        if not(shouldPrint):
          continue

        for match in group:
          print(f"{Tools.convertNot(key)}:{match[0]}| {match[1]} \
            --> {[Tools.convertNot(DEPENDENCIES[x][1]) for x in match[2]]}")

        print(Lines.getLinesByRange(key, int(linenr_start), int(linenr_end), offset))

  # Groups matches by distance of line numbers --> [[match1, match2], [match3]]
  def groupLinesByLinenumber(matches, separation):
    matches.sort(key=lambda x: int(x[0]))
    linenrs = [int(item[0]) for item in matches]
    grouped = []

    current_group = []
    prev_linenr = -1
    for i in range(0, len(linenrs)):
      # New matches --> Fill first group
      if (prev_linenr == -1):
        current_group.append(matches[i])
        prev_linenr = linenrs[i]
        continue

      # Already worked with matches
      current_linenr = linenrs[i]
      if (current_linenr - prev_linenr < separation):
        current_group.append(matches[i])
      elif len(current_group) > 0:
          grouped.append(current_group)
          current_group = []
      
      prev_linenr = linenrs[i]

    # Still have groups left at the end
    if len(current_group) > 0:
      grouped.append(current_group)
      current_group = []

    return grouped

  # Print lines of code of components that occur in the matches
  def getCodeLines(componentfilter, offset, bothDirections = True):
    for target in componentfilter:
      Lines.getCodeLinesStartingFromTarget(target, offset)
      print("_______________\n")

      # If target is None, all matches are shown. This should not be displayed twice
      if bothDirections and target is not None:
        Lines.getCodeLinesEndingAtTarget(target, offset)
        print("_______________\n")
        print("_______________\n")


class Tools(object):
  # Convert notation (HUSSACT: x.x.x.y -> y)
  def convertNot(s):
      regex_p1 = re.compile('\.[a-z].*\.[A-Z].*$|^[a-z]')
      regex_p2 = re.compile('\.[A-Z]')
      x1 = regex_p1.search(s)

      if x1 != None:
        s = s[x1.span()[0]+1:]
        x2 = regex_p2.search(s)
        if x2 != None:
          s = s[x2.span()[0]+1:]

      if "." in s:
        return s.split(".")[0]

      return s

  # Search the dependencies using criteria
  def searchDependencies(component, relationship):
    result = []
    for dep in DEPENDENCIES:
      if (component in dep[1] and dep[2] == relationship):
         result.append(dep)

    return result
    
  # Find a list of context-declared broadcast receivers
  def findContextDeclaredBroadcastReceivers():
    result = Tools.searchDependencies("xLibraries.android.content.BroadcastReceiver", "Inheritance")
    
    if len(result) == 0:
      print("No BroadcastReceivers found")
      return

    for r in result:
      print(f"{Tools.convertNot(r[0])} \t\t <-- {r[0]}")
      result += Tools.searchDependencies(r[0], "Inheritance")

  # Find list of third party dependencies
  def findingThirdPartyDependencies(namespaces):
    namespaces += ["android.support", "butterknife", "xLibraries.android", "xLibraries.com.bumptech", 
                    "xLibraries.com.google", "xLibraries.com.squareup", "xLibraries.java", "xLibraries.org.apache", 
                    "xLibraries.org.json", "xLibraries.org.jsoup", "xLibraries.org.junit", "xLibraries.org.powermock", 
                    "xLibraries.rx", "xLibraries.timber"]
    thirdParties = set()
    for dep in DEPENDENCIES:
      dep_0 = False
      dep_1 = False
      for namespace in namespaces:
        if namespace in dep[0]:
          dep_0 = True
        if namespace in dep[1]:
          dep_1 = True

      if dep_0 == False:
        thirdParties.add(dep[0])
      if dep_1 == False:
        thirdParties.add(dep[1])

    thirdParties = list(thirdParties)
    thirdParties.sort()
    for thirdParty in thirdParties:
      print(thirdParty)


class MatchFilters(Enum):
  ## Match filters ##
  INTENT_URI = "xLibraries.android.content.Intent"
  PENDING_INTENT_URI = "xLibraries.android.app.PendingIntent"

  # Content resolver does not work if context.getContentResolver() is used (and context is too broad)
  CONTENT_RESOLVER_URI = "Loader"

  # Detecting binders
  BINDER_URI = "xLibraries.android.os.Binder"

  # Used for finding all references from/to a component
  NONE_URI = ""

  # Detecting context-declared broadcast receivers
  LOCAL_RECEIVERS = "BroadcastReceiver"

  CUSTOM_COMPONENT = "Any component"

filepath_repository = "/home/yorick/Repositories/Omni-Notes"
filepath_dependencies = "/home/yorick/Repositories/OZP/dependencies_OmniNotes.csv"
namespace = "it.feio.android.omninotes"
matchFilter = MatchFilters.INTENT_URI

# Stupid exceptions when class files contain two separate classes :<
JAVACLASSES["ImageAndTextViewHolder"] = "/home/yorick/Repositories/Omni-Notes/omniNotes/src/main/java/it/feio/android/omninotes/models/adapters/ImageAndTextAdapter.java"
JAVACLASSES["NoteDrawerAdapterViewHolder"] = "/home/yorick/Repositories/Omni-Notes/omniNotes/src/main/java/it/feio/android/omninotes/models/adapters/NavDrawerAdapter.java"
JAVACLASSES["NoteDrawerCategoryAdapterViewHolder"] = "/home/yorick/Repositories/Omni-Notes/omniNotes/src/main/java/it/feio/android/omninotes/models/adapters/NavDrawerCategoryAdapter.java"

# Run setup; find java files and matches
Setup(filepath_repository, filepath_dependencies, namespace, matchFilter.value)


## Component filters ##
componentFilter = [None] # Show all matches 
componentFilter = ["CategoriesUpdatedEvent","DynamicNavigationReadyEvent","NavigationUpdatedEvent",
  "NavigationUpdatedNavDrawerClosedEvent", "NotesLoadedEvent",
  "NotesMergeEvent", "NotesUpdatedEvent", "NotificationRemovedEvent", "PasswordRemovedEvent",
  "PushbulletReplyEvent", "SwitchFragmentEvent"]

Lines.getCodeLines(componentFilter, 1, True)

# Tools.findContextDeclaredBroadcastReceivers()
# Tools.findingThirdPartyDependencies([namespace])