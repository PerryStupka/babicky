import datetime
import pathlib
import re
import os
import shutil

import click
import frontmatter
from jinja2 import Environment, select_autoescape, FileSystemLoader
import mistune
from mutagen.mp3 import MP3

SOURCES_DIR = "sources"
META_DIR = "sources/meta"
SOUND_DIR = "sources/sound"
PUBLIC_DIR = "public"
IMG_DIR = "img"
AUDIO_DIR = "audio"

CONFIG = {
    "author":"Perry Stupka"
}

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
        sound_file = f"{SOUND_DIR}/{data['filename']}.mp3"
        data["length"] = os.path.getsize(sound_file)
        audio = MP3(sound_file)
        data["duration"] = audio.info.length
        results.append(data)

    return results


@click.command()
def pub():
    #     ensure necessary directories exist
    folders = [IMG_DIR, AUDIO_DIR]
    for folder in folders:
        os.makedirs(f"{PUBLIC_DIR}/{folder}",exist_ok=True)
    """parse the MDs"""
    eps = load_eps()
    env = Environment(
        loader=FileSystemLoader('templates'),
    )
    with open(f'{PUBLIC_DIR}/index.html', 'w') as f:
        f.write(env.get_template('home.html.j2').render(eps=eps, **CONFIG))
    with open(f'{PUBLIC_DIR}/rss.xml', 'w') as f:
        f.write(env.get_template('rss.xml.j2').render(eps=eps))
    #  copy audio files from sound dir
    for file in os.listdir(SOUND_DIR):
        shutil.copy(os.path.join(SOUND_DIR,file), f"{PUBLIC_DIR}/{AUDIO_DIR}")
    for file in os.listdir(f"{SOURCES_DIR}/{IMG_DIR}"):
        shutil.copy(os.path.join(f"{SOURCES_DIR}/{IMG_DIR}",file), f"{PUBLIC_DIR}/{IMG_DIR}")
    # shutil.copytree(f"{SOUND_DIR}/*.*",f"{PUBLIC_DIR}/{AUDIO_DIR}")
#     copy images




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
