# Low Sodium

Process Salt Jinja templates with Pillar data, without Salt.

Inspired by https://github.com/kolypto/j2cli

## Usage

```bash
# Pass files explicitly
python low-sodium.py [-d pillar.yaml] template.jinja > output.txt

# Pass template via stdin
cat template.jinja | python [-d pillar.yaml] low-sodium.py > output.txt

# Pass data in enviornment variable
PILLAR_YAML='"kube-config:node-env": "staging"' \
	low-sodium.py template.jinja > output.txt
```
