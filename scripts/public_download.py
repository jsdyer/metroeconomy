"""Bounded HTTPS retrieval with a standard curl transport fallback.

Both clients request the same public URL, verify TLS, and require HTTP success.
No retained file or check timestamp is updated here.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from http.client import HTTPException
from time import sleep


def download_bytes(url, *, limit, timeout=90, user_agent='CoolCode public data collector (+https://coolcode.ca/)'):
    if not url.startswith('https://'):
        raise ValueError('An HTTPS source URL is required')
    for attempt in range(2):
        try:
            request = Request(url, headers={'User-Agent': user_agent, 'Accept': '*/*'})
            with urlopen(request, timeout=timeout) as response:
                body = response.read(limit + 1)
            if len(body) > limit:
                raise ValueError('Source response exceeds the configured size limit')
            return body
        except (OSError, HTTPException) as error:
            if isinstance(error, HTTPError) and error.code not in (403, 408, 429) and error.code < 500:
                raise
            if attempt == 0 and not isinstance(error, HTTPError):
                sleep(2)
                continue
            failure = error
            break
    if not shutil.which('curl'):
        raise failure
    print(f'Primary HTTPS request failed ({failure}); trying curl for the same public source: {url}', flush=True)
    with tempfile.TemporaryDirectory() as work:
        output = Path(work) / 'response'
        result = subprocess.run([
            'curl', '--fail', '--silent', '--show-error', '--location',
            '--proto', '=https', '--proto-redir', '=https',
            '--connect-timeout', '20', '--max-time', str(timeout),
            '--max-filesize', str(limit), '--user-agent', user_agent,
            '--header', 'Accept: */*', '--output', str(output), url,
        ], capture_output=True, text=True, timeout=timeout + 10)
        if result.returncode:
            raise OSError(f'Public source retrieval failed: {url}: {result.stderr.strip()}') from failure
        if output.stat().st_size > limit:
            raise ValueError('Source response exceeds the configured size limit')
        return output.read_bytes()
