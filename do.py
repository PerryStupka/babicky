import datetime
import pathlib
import re

import click
import frontmatter
from jinja2 import Environment, select_autoescape, FileSystemLoader
import mistune


META_DIR = "sources/meta"

@click.group()
def main():
    """click"""
    pass


def load_eps():
    return load_mds(META_DIR)


def load_mds(path):
    glob = pathlib.Path(path).glob("*.md")
    results = []
    md = mistune.create_markdown()
    for item in sorted(glob, reverse=True):
        matter = frontmatter.load(item)
        data = dict(matter)
        # how wil this be printable though ?
        data['body'] = md(matter.content)
        title_match = re.search('<h1>(?P<title>.+)</h1>', data['body'])
        data['filename'] = pathlib.Path(item).stem
        if title_match:
            data['title'] = title_match.groupdict().get('title')
        else:
            data['title'] = data['filename']

        results.append(data)

    return results


@click.command()
def pub():
    """parse the MDs"""
    eps = load_eps()
    env = Environment(
        loader=FileSystemLoader('templates'),
    )
    with open(f'public/index.html', 'w') as f:
        f.write(env.get_template('home.html.j2').render(eps=eps))
    with open(f'public/rss.xml', 'w') as f:
        f.write(env.get_template('rss.xml.j2').render(eps=eps))



@click.command()
@click.argument('name')
def newep(name):
    """generate a file for a new episode todo: get lenght automatically ?"""
    env = Environment(
        loader=FileSystemLoader('templates'),
    )
    today = datetime.date.today()
    filename = name
    published = today.strftime('%d-%m-%Y')
    with open(f'{META_DIR}/{filename}.md', 'w') as nd:
        nd.write(env.get_template('ep.md.j2').render(filename=filename, published=published))
    print(f'{filename} added')


main.add_command(pub)
main.add_command(newep)


if __name__ == "__main__":
    main()
