import shutil
from dataclasses import dataclass
from pathlib import Path

import markdown
from jinja2 import Template, FileSystemLoader, Environment, select_autoescape

@dataclass
class Post:
  title: str
  date: str
  content: str
  description: str
  url: str

  @staticmethod
  def from_file(file: Path) -> 'Post':
    with file.open('r') as f:
      content = f.read()
      md = markdown.Markdown(extensions=['meta'])
      html = md.convert(content)
      return Post(title=md.Meta['title'][0],
                  date=md.Meta['date'][0],
                  description=md.Meta['description'][0],
                  content=html,
                  url=f'{file.stem}.html')

env = Environment(
  loader=FileSystemLoader('templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

def generate_posts() -> list[Post]:
  posts: list[Post] = []
  for file in Path('posts').glob('*.md'):
    post = Post.from_file(file)
    posts.append(post)
  return posts

def render_blog_posts(posts: list[Post]):
  Path('build/blog').mkdir(parents=True, exist_ok=True)
  for post in posts:
    with open(f'build/blog/{post.url}', 'w') as f:
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

def copy_assets():
  shutil.copytree('assets', 'build/assets', dirs_exist_ok=True)

if __name__ == '__main__':
  posts = generate_posts()
  render_index(posts)
  render_blog_posts(posts)
  render_about()
  copy_assets()