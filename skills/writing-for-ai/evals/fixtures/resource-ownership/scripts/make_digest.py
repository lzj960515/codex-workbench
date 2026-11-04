import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True)
a=p.parse_args();data=json.loads(Path(a.input).read_text());out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
out.write_text('# '+data['title']+'\n\n'+''.join('- '+item+'\n' for item in data['points']))
