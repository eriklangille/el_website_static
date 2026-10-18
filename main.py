import shutil
from dataclasses import dataclass
from pathlib import Path
from datetime import date

import markdown
from jinja2 import FileSystemLoader, Environment, select_autoescape

@dataclass
class Post:
  title: str
  date_iso: date
  content: str
  description: str
  slug: str

  @property
  def date(self):
    return f'{self.date_iso:%B} {self.date_iso.day}, {self.date_iso.year}'

  @property
  def url(self):
    return f'/blog/{self.slug}'

  @staticmethod
  def from_file(file: Path) -> 'Post':
    with file.open('r') as f:
      content = f.read()
      md = markdown.Markdown(extensions=['meta', 'codehilite'])
      html = md.convert(content)
      return Post(title=md.Meta['title'][0],
                  date_iso=date.fromisoformat(md.Meta['date'][0]),
                  description=md.Meta['description'][0],
                  content=html,
                  slug=file.stem)

env = Environment(
  loader=FileSystemLoader('templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

def generate_posts() -> list[Post]:
  posts: list[Post] = []
  for file in Path('posts').glob('*.md'):
    post = Post.from_file(file)
    posts.append(post)
  # sort posts by date
  posts.sort(key=lambda post: post.date_iso, reverse=True)

  return posts

def clean_build():
  shutil.rmtree('build', ignore_errors=True)
  Path('build/blog').mkdir(parents=True)

def render_blog_posts(posts: list[Post]):
  for post in posts:
    with open(f'build/blog/{post.slug}.html', 'w') as f:
      out = env.get_template('post.html').render(post=post)
      f.write(out)

def render_index(posts: list[Post]):
  with open('build/index.html', 'w') as f:
    out = env.get_template('index.html').render(posts=posts)
    f.write(out)

def render_about():
  with open('build/about.html', 'w') as f:
    out = env.get_template('about.html').render()
    f.write(out)

def render_404():
  with open('build/404.html', 'w') as f:
    out = env.get_template('404.html').render()
    f.write(out)

def copy_assets():
  shutil.copytree('assets', 'build/assets')
  shutil.copy('assets/favicon.ico', 'build/favicon.ico')

if __name__ == '__main__':
  clean_build()
  posts = generate_posts()
  render_index(posts)
  render_blog_posts(posts)
  render_about()
  render_404()
  copy_assets()
