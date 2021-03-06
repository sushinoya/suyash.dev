import distutils.dir_util
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import json
import os
from shutil import copyfile
from collections import defaultdict
from datetime import datetime
import urllib
import markdown2

JSON_URL = os.environ["JSON_DATA"]
response = urllib.urlopen(JSON_URL)
json_data = json.loads(response.read())
main_title = json_data.get('title', '')

# Replaces <old_text> with <new_text> in file named <filename>
def replace_text_in_file(old_text, new_text, filename):
  if isinstance(new_text, list):
    new_text = '\n'.join(new_text)
  if not new_text: new_text = ""
  with open(filename, 'r') as file:
    filedata = file.read()
  new_file_data = filedata.replace(old_text, new_text)
  with open(filename, 'w') as file:
    file.write(new_file_data)

# Generates the side menu based on json_data["pages"]
def generate_menu_list(json_data):
  pages = json_data["pages"]
  titles = sorted([ (page_name, page["title"]) for page_name, page in pages.items() if "index" in page and page["index"]])
  html_frag = ["<li><a href=\"/{}.html\">{}</a></li>".format(page_name, page) for page_name, page in titles]
  return "<ul>{}</ul>".format('\n'.join(html_frag))

# Updates the website title, menu title and adds the side menu
def update_generic_params(filename):
  replace_text_in_file("{website_title}", main_title, filename)
  replace_text_in_file("{menu_title}", main_title, filename)
  replace_text_in_file("{menu_list}", generate_menu_list(json_data), filename)

# Coverts list of text into paragraphs. Or returns string as it is.
def unpack_text_list(text_lst, is_markdown=False, is_link=False):
  if is_link: 
    text_lst = urllib.urlopen(text_lst).read()
  if not isinstance(text_lst, list):
    return markdown2.markdown(text_lst, extras=['fenced-code-blocks', 'tables', 'cuddled-lists', 'strike']) if is_markdown else text_lst
  paragraphs = ["<p> {} </p>".format(markdown2.markdown(text, extras=['fenced-code-blocks', 'tables', 'cuddled-lists', 'strike']) if is_markdown else text) for text in text_lst]
  return '\n'.join(paragraphs)

# Adds "id=selected" for the menu item
def mark_menu_item_as_selected(filename):
  current_li = "href=\"/{}\">".format(filename)
  replacement = current_li.replace("href=", "id=\"selected\" href=")
  replace_text_in_file(current_li, replacement, filename)

# Generate the list for a page. Depends on three fields - link, title and desc. 
# Either (link, title) or desc or all three must be present
def generate_page_list(items):
  if not items: return ""
  texts = []
  for item in items:
    text = "<li>{}</li>"
    if "link" in item: text = text.format("<a href=\"{}\">{}</a>{}").format(item["link"], item["title"], "{}")
    text = text.format(": " + item["desc"] if "desc" in item else "")
    texts.append(text)
  return "<ul>{}</ul>".format("\n".join(texts))

def create_and_write_to_file(filename, text):
  if '/' in filename:
    directory, file = filename.rsplit('/', 1)
    distutils.dir_util.mkpath(directory)
  file = open(filename, "w+")
  file.write(text)
  file.close()

def get_html_chunk(tag):
  with open('template.txt', 'r') as myfile:
    s = myfile.read()
    start = s.find("<{}>".format(tag))
    end = s.find("</{}>".format(tag)) + len("</{}>".format(tag))
    return s[start:end]

def generate_redirect_page(subdir, url):
  if subdir in json_data['pages'] or subdir in json_data['subfolders']: return
  page_name = "{}.html".format(subdir)
  create_and_write_to_file(page_name, "<html><head>{meta_tag} {style}</head>{redirect_msg}</html>")
  replace_text_in_file('{meta_tag}', "<meta http-equiv=\"refresh\" content=\"0;url={}\">".format(url), page_name)
  replace_text_in_file('{redirect_msg}', "You are being redirected to {}".format(url), page_name)
  replace_text_in_file('{style}', get_html_chunk("style"), page_name)

def get_datetime_from_str(date_str):
  return datetime.strptime(date_str, "%d/%m/%Y")

def datetime_str_to_posted_str(date_str):
  if not date_str:
    return ""
  date = get_datetime_from_str(date_str)
  return "{}".format(datetime.strftime(date, "%d %B %Y"))

def get_published_datetime_str(date_str):
  return "Published on {}".format(datetime_str_to_posted_str(date_str)) if date_str else ""

def generate_html(page_name, data):
  filename = "{}.html".format(page_name)
  dir_name = os.path.dirname(filename)
  omit_website_title = data.get("omit_page_title", False)
  if dir_name: os.path.exists(dir_name) or os.makedirs(dir_name)
  copyfile('template.txt', filename)

  update_generic_params(filename)
  replace_text_in_file("{page_title}", data["title"] if not omit_website_title else '', filename)
  replace_text_in_file("{date_info}", get_published_datetime_str(data.get("date_info", "")), filename)
  replace_text_in_file("{page_desc}", unpack_text_list(data["description"], is_markdown=data.get("is_markdown", False), is_link=data.get("is_link", False)), filename)
  replace_text_in_file("{text_above_embed}", unpack_text_list(data["text_above_embed"]), filename)
  replace_text_in_file("{embed_content}", data["embed"], filename)
  replace_text_in_file("{page_list}", generate_page_list(data["list"]), filename)
  mark_menu_item_as_selected(filename)

# Fetch a repo:branch and deploy it
def fetch_and_generate_subfolder(path, folder_data):
  if path in json_data['pages']: return
  repo = folder_data['repo']
  build_command = folder_data.get('build_command', '')
  branch_flags = '--single-branch --branch ' + folder_data['branch'] if folder_data['branch'] else ''
  os.system("git clone {} {} {}".format(branch_flags, repo, path))
  os.system("cd {}; {}; cd -".format(path, build_command))

# Generate index.html
generate_html('index', defaultdict(str))

# Populate blog articles
blog_articles = [{
  "title": data["title"], 
  "link": "/{}".format(page_name), 
  "desc": datetime_str_to_posted_str(data["date_info"]),
  "date": get_datetime_from_str(data["date_info"])}
for page_name, data in json_data["pages"].items() if "date_info" in data and data.get("is_blog_post", False)]

json_data["pages"]["blog"]["list"] = reversed(sorted(blog_articles, key=lambda x: x["date"]))


# Generate all pages
for page_name, data in json_data["pages"].items():
  generate_html(page_name, data)

# Generate all redirect pages
for subdir, url in json_data["redirects"].items():
  generate_redirect_page(subdir, url)

# Generate "symlinked" subfolders
for path, data in json_data["subfolders"].items():
  fetch_and_generate_subfolder(path, data)
