#!/usr/bin/python3

import os, requests, threading, sys, time
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse

AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"
headers = {'User-Agent': AGENT}
main_url = "https://blogtruyen.vn"

def get_elements(url, ele, attr):
    try:
        r = requests.get(url, headers=headers)
        return [i.get(f"{attr}") for i in bs(r.content, "html.parser").find_all(f"{ele}")]
    except Exception as e:
        print(f"[-]In get_elements(): {e}")

def make_chapter(c_link,chapters, m_dir):
    try:
        c_dir = f"chapter-{chapters.index(c_link)+1}"
        c_link = f"{main_url}{c_link}"
        img_links = []
        myT = list()
        print(f"[!]Trying to get {c_link}")
        os.makedirs(f"{m_dir}/{c_dir}", exist_ok=True)
        r = requests.get(c_link, headers=headers)
        if r.status_code == 200:
            print(f"[+]Getting img from {c_link}")
            tree = bs(r.text, "html.parser")
            for i_link in tree.find_all("img"):
                if "https" in i_link.get("src"):
                    print(f"[++]Found link: {i_link.get('src')}")
                    img_links.append(i_link.get("src"))
            for i_link in img_links:
                t = threading.Thread(target=get_img, args=(i_link, img_links.index(i_link), c_dir, m_dir))
                myT.append(t)
                t.start()
            for t in myT:
                t.join()
    except Exception as e:
        print(f"[-]At make_chapter {c_dir}: {e}")

def get_img(link, i_name, c_dir, m_dir):
    try:
        time.sleep(1)
        r = requests.get(link, headers=headers)
        if r.status_code == 200:
            print(f"[*][At chapter {c_dir}] Trying to retrieve {link} and rename to {i_name}.jpg")
            with open(f"{m_dir}/{c_dir}/{i_name}.jpg", "wb") as f:
                f.write(r.content)
    except Exception as e:
        print(f"[-]At get_img {link}: {e}")

def get_name(url):
    return urlparse(url).path.split("/")[-1]

def get_chapters(url, chapters, manga_name):
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            tree = bs(r.text, "html.parser")
            print(f"[*]Getting chapters from {manga_name}")
            for link in tree.find_all("a"):
                if f"{manga_name}-" in link.get("href"):
                    chapters.append(link.get("href"))
                    print(link.get("href"))
    except Exception as e:
        print(f"[-]At get_chapters(): {e}")

def run():
    chapters = []
    manga_url = input("Enter manga' url: ")
    manga_name = get_name(manga_url)
    myMT = list()
    print(f"[***]Trying to get {manga_name}...")
    os.makedirs(manga_name, exist_ok=True)
    get_chapters(manga_url, chapters, manga_name)
    chapters.reverse()

    select_range = input("Do you want to select a range of chapters? (yes/no): ").lower()

    if select_range == "yes":
        start_chapter = input("Enter the start chapter number (e.g., chapter_01): ")
        end_chapter = input("Enter the end chapter number (e.g., chapter_05): ")
        start_index = None
        end_index = None
        for i, chapter in enumerate(chapters):
            if start_chapter in chapter and start_index is None:
                start_index = i
            if end_chapter in chapter and end_index is None:
                end_index = i

        if start_index is not None and end_index is not None:
            selected_chapters = chapters[start_index:end_index + 1]  # Include end_index

            for chapter in selected_chapters:
                make_chapter(chapter, chapters, manga_name)
                t = threading.Thread(target=make_chapter, args=(chapter, chapters, manga_name,))
                myMT.append(t)
                t.start()
        else:
            print("Invalid chapter range.")
            return
    else:
        for chapter in chapters:
            make_chapter(chapter, chapters, manga_name)
            t = threading.Thread(target=make_chapter, args=(chapter, chapters, manga_name,))
            myMT.append(t)
            t.start()

    for t in myMT:
        t.join()
    #for chapter in chapters:
    #    make_chapter(chapter, chapters,  manga_name)
    #    t = threading.Thread(target=make_chapter, args=(chapter, chapters, manga_name,))
    #    myMT.append(t)
    #    t.start()
    #for t in myMT:
    #    t.join()

if __name__ == "__main__":
    run()
