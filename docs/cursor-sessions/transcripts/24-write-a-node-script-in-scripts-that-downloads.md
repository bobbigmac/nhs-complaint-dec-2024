---
cursor_session: 4e8b989c-bc7e-471b-bb6f-19516af28935
source: cursor-composer
cursor_hint: ?
user_entries: 1
---

# transcript — write-a-node-script-in-scripts-that-downloads

### you

write a node script in /scripts that downloads all txt books for a search against project gutenberg, excluding books with an id already found in /ebooks or /ebooks.

We want to run 2 basic retrievals...  first we want the utf-8.txt file for any jpg/png found in /ebooks/next/ that doesn't have a txt file (and it should be saved as #PGID#.txt alongside the image (and save the meta as #PGID#.meta.json).



The second we want to be able to search by author and download all book texts (and meta) for that author (just use gutendex search enpoint, as we will also search by book names or similar, and don't mind over-catching content. don't build a complex autho manager tool), exlcuding those with txt files already in ebooks, ebooks/next or ebooks/rendered.

This key from formats is the file we want. @12.meta.json (37-38) .

Use gutendex.com, and the tool should figure out what it's going to download and offer a summary before the user confirms yes or no to download all files to the ebooks/next folder.



................



Documention



For long-term use, please run your own server with the code and installation instructions on GitHub.

Lists of Books

Lists of book information in the database are queried using the API at /books (e.g. gutendex.com/books). Book data will be returned in the format

{

  "count": <number>,

  "next": <string or null>,

  "previous": <string or null>,

  "results": <array of Books>

}

where results is an array of 0-32 book objects, next and previous are URLs to the next and previous pages of results, and count in the total number of books for the query on all pages combined.

By default, books are ordered by popularity, determined by their numbers of downloads from Project Gutenberg.

Parameters can also be added to book-list queries in a typical URL format. For example, to get the first page of written by authors alive after 1899 and published in English or French, you can go to /books?author_year_start=1900&languages=en,fr

You can find available query parameters below.

author_year_start and author_year_end

Use these to find books with at least one author alive in a given range of years. They must have positive or negative integer values. For example, /books?author_year_end=-499 gives books with authors alive before 500 BCE, and /books?author_year_start=1800&author_year_end=1899 gives books with authors alive in the 19th Century.

copyright

Use this to find books with a certain copyright status: true for books with existing copyrights, false for books in the public domain in the USA, or null for books with no available copyright information. These can be combined with commas. For example, /books?copyright=true,false gives books with available copyright information.

ids

Use this to list books with Project Gutenberg ID numbers in a given list of numbers. They must be comma-separated positive integers. For example, /books?ids=11,12,13 gives books with ID numbers 11, 12, and 13.

languages

Use this to find books in any of a list of languages. They must be comma-separated, two-character language codes. For example, /books?languages=en gives books in English, and /books?languages=fr,fi gives books in either French or Finnish or both.

mime_type

Use this to find books with a given MIME type. Gutendex gives every book with a MIME type starting with the value. For example, /books?mime_type=text%2F gives books with types text/html, text/plain; charset=us-ascii, etc.; and /books?mime_type=text%2Fhtml gives books with types text/html, text/html; charset=utf-8, etc.

search

Use this to search author names and book titles with given words. They must be separated by a space (i.e. %20 in URL-encoded format) and are case-insensitive. For example, /books?search=dickens%20great includes Great Expectations by Charles Dickens.

sort

Use this to sort books: ascending for Project Gutenberg ID numbers from lowest to highest, descending for IDs highest to lowest, or popular (the default) for most popular to least popular by number of downloads.

topic

Use this to search for a case-insensitive key-phrase in books' bookshelves or subjects. For example, /books?topic=children gives books on the "Children's Literature" bookshelf, with the subject "Sick children -- Fiction", and so on.

Individual Books

Individual books can be found at /books/<id>, where <id> is the book's Project Gutenberg ID number. Error responses will appear in this format:

{

  "detail": <string of error message>

}

API Objects

Types of JSON objects served by Gutendex are given below.

Book

{

  "id": <number of Project Gutenberg ID>,

  "title": <string>,

  "subjects": <array of strings>,

  "authors": <array of Persons>,

  "summaries": <array of strings>,

  "translators": <array of Persons>,

  "bookshelves": <array of strings>,

  "languages": <array of strings>,

  "copyright": <boolean or null>,

  "media_type": <string>,

  "formats": <Format>,

  "download_count": <number>

}

Format

{

  <string of MIME-type>: <string of UR>,

  ...

}

Person

{

  "birth_year": <number or null>,

  "death_year": <number or null>,

  "name": <string>

}

### assistant

I’ll first inspect your existing `ebooks` structure and the sample meta file, then create a Node script under `scripts` that (1) finds missing texts for images in `ebooks/next` and (2) searches Gutendex by author/title and prepares a summary of downloads, with a confirm step before saving into `ebooks/next`.

### assistant

I’ve inspected your repo layout and the sample meta format, next I’ll examine existing helper scripts and ebook folders, then add a new Node script under `scripts` that matches your current style and supports both retrieval modes with a yes/no confirmation step.

### assistant

### What I added

- **New script**: `scripts/gutendex-download-texts.js` (ESM, same style as your other scripts).

### How to use it

- **Mode 1 – covers in `ebooks/next`**  
  Finds `.png`/`.jpg` in `ebooks/next` that **don’t** have a matching `#ID#.txt`, fetches Gutendex meta, selects the `formats["text/plain; charset=us-ascii"]` URL (or another `text/plain` `.txt.utf-8` fallback), and plans downloads to `ebooks/next/#ID#.txt` and `ebooks/next/#ID#.meta.json`.  
  It prints a summary and asks for confirmation first.
  ```bash
  node scripts/gutendex-download-texts.js covers
  ```

- **Mode 2 – search by author/title (via Gutendex `search`)**  
  Uses `https://gutendex.com/books?search=...` (paging through `next`) to collect matches, **excluding any IDs that already have `.txt` files** in `ebooks`, `ebooks/next`, or `ebooks/rendered`.  
  For remaining books it picks the same `formats` key as above, plans downloads into `ebooks/next/#ID#.txt` and `ebooks/next/#ID#.meta.json`, prints a summary, then asks for confirmation.
  ```bash
  node scripts/gutendex-download-texts.js search "Lewis Carroll"
  # or:
  node scripts/gutendex-download-texts.js search "dickens great"
  ```

If you want, I can tweak the ID detection, MIME preference logic, or the summary output format.
