# Low Sodium

Process Salt Jinja templates with Pillar data, without Salt.

Inspired by https://github.com/kolypto/j2cli

## Usage

```bash
# Pass files explicitly
python low-sodium.py template.jinja [pillar.yaml] > output.txt

# Pass template via stdin
cat template.jinja | python low-sodium.py [pillar.yaml] > output.txt
```
