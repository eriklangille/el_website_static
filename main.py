import shutil
from jinja2 import Template, FileSystemLoader, Environment, select_autoescape

env = Environment(
  loader=FileSystemLoader('templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

def render_index():
  with open('build/index.html', 'w') as f:
    out = env.get_template('index.html').render()
    f.write(out)

def render_about():
  with open('build/about.html', 'w') as f:
    out = env.get_template('about.html').render()
    f.write(out)

def copy_css():
  shutil.copytree('assets', 'build', dirs_exist_ok=True)

if __name__ == '__main__':
  render_index()
  render_about()
  copy_css()