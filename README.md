# too-simple-site-generator

This is unsurprisingly also the repository for [suyash.dev](https://suyash.dev). This was never meant to be a static stite generator but it has sort of become one.

## What is this?

I wanted a simple website for myself and I achieved that manually writing HTML pages. However, I wanted something which could read data from a `yaml` or `JSON` file and generate all the HTML pages for me. So I did exactly that.

The website is generated by a single, horribly-written script - `gen.py`.
It fetches data from a JSON (on a different server in this case) and builds all the html files
on each deploy. So, in essence it is a very basic static-site generator.

I did consider using [Jekyll](https://jekyllrb.com/) or [Gatsby](https://www.gatsbyjs.org/)
but having using both in the past, I thought going for something minimalistic would be better.


## How can you use this too?

- Clone this repository
- Set `JSON_URL` in `gen.py` to `sample_data.json`.
- Change `TITLE` in `gen.py` to the title of your website.
- Run the python script: `python gen.py`.
- Update the `sample_data.json` with your data.
- Change the `favicon.ico` to a different icon.
- Push to github and use Netlify or Github Pages to host.


## Should you host the JSON elsewhere?

The reason why I chose to have it this way is so that I can update the JSON if I needed to add new pages to my site or if I wished to change the content of any of the pages without having to alter the HTML directly.