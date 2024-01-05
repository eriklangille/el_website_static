import argparse
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from datetime import date

import boto3
import markdown
from jinja2 import FileSystemLoader, Environment, select_autoescape

BUCKET_NAME = 'eriklangille.com'
BUILD_FOLDER_PATH = Path('./build')
DISTRIBUTION_ID = 'E200ARC50I19C0'

@dataclass
class Post:
  title: str
  date_iso: date
  content: str
  description: str
  url: str

  @property
  def date(self):
    return self.date_iso.strftime('%B %d, %Y')

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
  # sort posts by date
  posts.sort(key=lambda post: post.date_iso, reverse=True)

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

def upload_to_s3(bucket_name: str, build_folder_path: Path):
  s3 = boto3.client('s3')
  
  for path in build_folder_path.glob('**/*'):
    if path.is_file():
      s3_file_path = str(path.relative_to(build_folder_path))
      if path.suffix == '.css':
        s3.upload_file(str(path), bucket_name, s3_file_path, ExtraArgs={'ContentType': 'text/css'})
      elif path.suffix == '.html':
        s3.upload_file(str(path), bucket_name, s3_file_path, ExtraArgs={'ContentType': 'text/html'})
      elif path.name == '.DS_Store':
        continue
      else:
        s3.upload_file(str(path), bucket_name, s3_file_path)

      print(f'Uploaded {path} to {s3_file_path}')

def invalidate_cloudfront_distribution(distribution_id):
  cloudfront = boto3.client('cloudfront')
  
  caller_reference = str(int(time.time()))
  invalidation = cloudfront.create_invalidation(
    DistributionId=distribution_id,
    InvalidationBatch={
      'Paths': {
        'Quantity': 1,
        'Items': ['/*']
      },
      'CallerReference': caller_reference
    }
  )
  print(f"Invalidation created with ID: {invalidation['Invalidation']['Id']}")

def parse_args():
    parser = argparse.ArgumentParser(description='Builds the website')
    parser.add_argument('-u', '--upload', action='store_true', help='Flag to indicate if upload to S3 should be performed')
    args = parser.parse_args()
    return args.upload

if __name__ == '__main__':
  upload = parse_args()

  posts = generate_posts()
  render_index(posts)
  render_blog_posts(posts)
  render_about()
  copy_assets()

  if upload:
    upload_to_s3(BUCKET_NAME, BUILD_FOLDER_PATH)
    invalidate_cloudfront_distribution(DISTRIBUTION_ID)