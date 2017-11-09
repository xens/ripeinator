# Intro

Manipulate RIPE objects through RIPE REST-API

# Usage

```console
python ripe.py --help
usage: ripe.py [-h] --db DB [--objects OBJECTS] [--dryrun] [--pwd PWD]
               [--search SEARCH] [--attribute ATTRIBUTE]

optional arguments:
  -h, --help            show this help message and exit
  --db DB               Database URL
  --objects OBJECTS     Objects to compare / write
  --dryrun              Perform validation and not the upgrade
  --pwd PWD             Password needed to write objects
  --search SEARCH       Search for a particular string
  --attribute ATTRIBUTE
                        Search for a specific attribute
```

# RIPE -> local yaml

For example to do reverse lookups on objects based on strings, to populate a yaml file:

```console
$ ripe.py --db https://rest.db.ripe.net --search maintainer_name --attribute mnt-by
```

or

```
$ ripe.py --db https://rest.db.ripe.net --search org_name --attribute org
```

# Local yaml -> RIPE

Updating and creating objects is supported but must be treated as experimental.

yaml file example (subject to changes):

```yaml
JD666-RIPE:
- person: John Doe
- address: 133 Cambridge Road
- address: London UK
- phone: +6 555 444 333
- e-mail: john.doe@somecompany.com
- nic-hdl: JD666-RIPE
- mnt-by: your-mnter
- source: RIPE
```

can be written into the RIPE.NET DB with:

```console
$ ripe.py --db https://rest.db.ripe.net --objects objects_test/ripe_write.yaml --pwd $PW
```

# Authentication

Only password authentication is supported for now. You can also export your password using the
`RIPE_PASSWORD` env var.
