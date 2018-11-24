import sys
from bs4 import BeautifulSoup

url_base = "https://elixir.bootlin.com/linux"

# Can use either urllib2 or urllib3 
try:
    import urllib3
    def get_url(url):
        http = urllib3.PoolManager()
        resp = http.request('GET', url)
        return resp.data

except ImportError as e:
    try:
        import urllib2
        def get_url(url):
            resp = urllib2.urlopen(url)
            return resp.read()

    except ImportError as e:
        print("ImportError: requires urllib2 or urllib3")

def get_linux_version():
    import subprocess
    # returns something like 4.13.0-46-generic
    uname = str(subprocess.check_output("uname -r", shell=True)).strip()
    version = "v" + ".".join(uname.split(".")[0:2])
    return version 

def search(query):
    version = get_linux_version()
    results = get_url("{base}/{version}/ident/{query}".format(
        base=url_base,
        version=version,
        query=query
    ))
    soup = BeautifulSoup(results, 'html.parser')

    div = soup.find('div', attrs={'class':'lxrident'})
    sections = div.findAll('h2')

    for section in sections:
        header = section.get_text().strip()
        if header:
            print(header)
            ul = section.find_next()
            for atag in ul.find_all('a'):
                # 'include/linux/netlink.h, line 113 (as a prototype)'
                display = atag.get_text().strip()
                # 'line 113 (as a prototype)'
                # 113
                lineno = display[display.find('line')+5:].split(" ")[0]
                print("    - {}".format(display))

def vim_search():
    import vim
    search(vim.eval("a:query"))

# filepath is a string url pointing to a specific file in elixir bootlin
# this filepath is returned as the result of running this script with the search command
#
# e.g. v4.13/source/include/linux/netlink.h
def get_source(filepath):
    # Download the page (unfortunately it's formatted in HTML)
    page_source = get_url("{base}/{path}".format(base=url_base, path=filepath))

    # Use beautiful soup to strip out all the tags and get a plain text file
    soup = BeautifulSoup(page_source, 'html.parser')
    code = soup.find('td', attrs={'class' : 'code'})
    text = code.get_text().strip()
    return text.replace("\t", "  ")

def vim_get_source():
    import vim
    line = vim.eval("l:line")
    # - include/linux/netlink.h, line 113 (as a prototype)
    line = line[line.find("-")+2:].strip()
    # include/linux/netlink.h, line 113 (as a prototype)
    sp = line.split(" ")
    filepath = sp[0].replace(",", "")
    lineno = sp[2]
    version = get_linux_version()
    filepath = "{version}/source/{filepath}".format(
        version=version,
        filepath=filepath
    )
    source = get_source(filepath)
    print(source)
    vim.command("let l:bootlinSearchLineNo = {}".format(lineno))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "search":
        search(sys.argv[2])
    elif mode == "get":
        get_source(sys.argv[2])
