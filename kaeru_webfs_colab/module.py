import platform, os, sys, re, time, socket, subprocess
import http.client
from IPython import display

binos = platform.system().lower()
binarch = platform.machine().lower()
if binarch == "x86_64": binarch="amd64"
if binarch == "i386": binarch="386"
if binarch == "i686": binarch="386"
script_dir = os.path.dirname(os.path.abspath(__file__))

def _check_kaeru_webfs(url, timeout=2):
    try:
        if url.startswith("https://"):
            host = url[8:]
            conn = http.client.HTTPSConnection(host, timeout=timeout)
        else:
            host = url[7:]
            conn = http.client.HTTPConnection(host, timeout=timeout)
        conn.request("HEAD", "/heartbeat")
        res = conn.getresponse()
        if 'x-kaeru' in [x[0].lower() for x in res.getheaders()]:
            return True
    except Exception as e:
        pass
    finally:
        if conn is not None:
            conn.close()
    time.sleep(1)
    return False

server_process = None
tproc = None
tunnel_url = None

def serve_webfs():
    global server_process, tproc, tunnel_url
    if True:
        raise Exception("the publication has been stopped due to a potential violation of the TOS. for more details: https://research.google.com/colaboratory/faq.html#disallowed-activities")
    if tunnel_url is None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            port_in_use = s.connect_ex(('localhost', 1234)) == 0
        if not port_in_use:
            bin_path = os.path.normpath(os.path.join(script_dir, f'./bin/kaeru-webfs_{binos}_{binarch}'))
            os.chmod(bin_path,0o755)
            server_process = subprocess.Popen([bin_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            server_process.stdout.readline()
        while not _check_kaeru_webfs("http://127.0.0.1:1234"):
            pass
        bin_path = os.path.normpath(os.path.join(script_dir, f'./cloudflared-linux-amd64'))
        log_path = os.path.normpath(os.path.join(script_dir, f'./cloudflared.log'))
        if not os.path.exists(bin_path):
            subprocess.run(["wget", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64", "-q", "-O", bin_path])
            os.chmod(bin_path, 0o755)
        if os.path.exists(log_path):
            os.remove(log_path)
        tproc = subprocess.Popen([bin_path, "tunnel", "--protocol", "http2", "--url", "http://127.0.0.1:1234", "--logfile", log_path], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        is_target_url = False
        while not os.path.exists(log_path):
            time.sleep(0.1)
        with open(log_path, 'r') as file:
            while True:
                line = file.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                url_matches = re.findall(r'https?://[A-Za-z0-9\-./:]+', line)
                for url in url_matches:
                    if re.search(r'://[^/:]+/?$', url):
                        if url.endswith("/"): url = url[:-1]
                        time.sleep(7)
                        is_target_url = _check_kaeru_webfs(url, timeout=7)
                        if is_target_url:
                            tunnel_url = url
                            break
                if is_target_url:
                    break
    code = """(async (url, element) => {
        if (!google.colab.kernel.accessAllowed) {
            return;
        }
        element.appendChild(document.createTextNode(''));
        const anchor = document.createElement('a');
        anchor.href = url+"/#/content/";
        anchor.target = '_blank';
        anchor.textContent = "Open in new tab";
        element.appendChild(anchor);
        const iframe = document.createElement('iframe');
        iframe.src = url+"/#/content/";
        iframe.height = "400";
        iframe.width = "100%";
        iframe.style.border = 0;
        iframe.style.backgroundColor = "#fff";
        iframe.allow = [
            'clipboard-read',
            'clipboard-write',
        ].join('; ');
        element.appendChild(iframe);
    })""" + '("{url}", window.element)'.format(url=tunnel_url)
    display.display(display.Javascript(code))
