import io,sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import public_download as download
URL='https://example.org/public.csv'
class PublicDownloadTests(unittest.TestCase):
 def test_valid_https_response_is_returned(self):
  with patch.object(download,'urlopen',return_value=io.BytesIO(b'valid')):
   self.assertEqual(download.download_bytes(URL,limit=20),b'valid')
 def test_not_found_is_not_masked_by_an_alternate_client(self):
  with patch.object(download,'urlopen',side_effect=HTTPError(URL,404,'missing',{},None)),patch.object(download.subprocess,'run') as run:
   with self.assertRaises(HTTPError):download.download_bytes(URL,limit=20)
   run.assert_not_called()
 def test_fallback_keeps_same_url_and_requires_success(self):
  def curl(command,**kwargs):
   self.assertEqual(command[-1],URL);self.assertIn('--fail',command);self.assertNotIn('--insecure',command)
   Path(command[command.index('--output')+1]).write_bytes(b'valid')
   return SimpleNamespace(returncode=0,stderr='')
  with patch.object(download,'urlopen',side_effect=HTTPError(URL,403,'Forbidden',{},None)),patch.object(download.shutil,'which',return_value='/usr/bin/curl'),patch.object(download.subprocess,'run',side_effect=curl):
   self.assertEqual(download.download_bytes(URL,limit=20),b'valid')
 def test_oversized_or_failed_response_cannot_be_accepted(self):
  with patch.object(download,'urlopen',return_value=io.BytesIO(b'123456')):
   with self.assertRaises(ValueError):download.download_bytes(URL,limit=3)
  with patch.object(download,'urlopen',side_effect=HTTPError(URL,403,'Forbidden',{},None)),patch.object(download.shutil,'which',return_value='/usr/bin/curl'),patch.object(download.subprocess,'run',return_value=SimpleNamespace(returncode=22,stderr='HTTP 403')):
   with self.assertRaises(OSError):download.download_bytes(URL,limit=20)
