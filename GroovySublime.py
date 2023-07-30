import sublime, sublime_plugin
import subprocess
import os
import json
import pathlib


class GroovyFormatCommand(sublime_plugin.TextCommand):
  def run(self, edit):

    region = sublime.Region(0, self.view.size())
    content = self.view.substr(region)
    fname = self.view.file_name()
    current = pathlib.Path(__file__).parent.resolve()
    print("current = %s" % current)

    tmp_file = "/tmp/code.groovy"
    with open(tmp_file, 'w') as f:
        f.write(content)

    cmd = ["npm-groovy-lint", 
           "--serverhost", 
           "http://127.0.0.1", 
           "--fix", 
           "--output", 
           "json", 
           "--config", 
           "%s/groovylintrc-recommended.json" % current, 
           tmp_file]
    print("cmd = %s" % " ".join(cmd))
    stdout, stderr = subprocess.Popen(
      [" ".join(cmd)],
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,      
      shell=True).communicate()

    #if stderr.strip():
    #  print("GROOVY FORMAT ERROR: %s" % stderr.strip().decode())
    #  print(stdout.decode('UTF-8'))
    #else:

    sublime.status_message("Build finished")

    try:
      r = json.loads(stdout.decode('UTF-8'))

      if 'files' in r and tmp_file in r['files'] and 'updatedSource' in r['files'][tmp_file]:
        updatedSource = r['files'][tmp_file]['updatedSource']

        #print("success %s" % updatedSource)
        self.view.replace(edit, region, updatedSource)
      else:
        sublime.error_message(stdout.decode('UTF-8'))
    except Exception as e:
      print("GroovyFormat fail: %s" % e)
      print("GroovyFormat ERROR: %s" % stderr.strip().decode())
      print("GroovyFormat RESULT: %s" % stdout.decode('UTF-8'))

def check_is_enabled_file(file_name):    
  types = ['.groovy']

  for t in types:
    if file_name.lower().endswith(t):
      return True
  return False

class GroovyEventDump(sublime_plugin.EventListener):

      
  def on_pre_save(self, view):
    if check_is_enabled_file(view.file_name()):
      view.run_command('groovy_format')


    
